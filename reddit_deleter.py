#!/usr/bin/env python3
"""
Reddit Post and Comment Deletion Bot

This bot overwrites and deletes all posts and comments for a Reddit account.
It first overwrites the content with replacement text, then deletes the content.
"""

import praw
import time
import sys
import os
import json
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Replacement text used to overwrite content before deletion
REPLACEMENT_TEXT = "[deleted]"

# File to store refresh token for future use
TOKEN_FILE = "reddit_token.json"


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth2 callback."""
    
    def do_GET(self):
        """Handle the OAuth callback from Reddit."""
        # Parse the authorization code from the callback URL
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        if 'code' in query_params:
            # Store the code for retrieval
            self.server.auth_code = query_params['code'][0]
            
            # Send success response to browser
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <head><title>Reddit Authentication</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #4CAF50;">Authentication Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            """)
        elif 'error' in query_params:
            # Handle error from Reddit
            self.server.auth_error = query_params['error'][0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
                <html>
                <head><title>Reddit Authentication Error</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #f44336;">Authentication Failed!</h1>
                    <p>Error: {query_params['error'][0]}</p>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            """.encode())
        
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


class RedditDeleter:
    def __init__(self, client_id, client_secret, user_agent, redirect_uri="http://localhost:8080"):
        """
        Initialize the Reddit API connection with OAuth2.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string for API requests
            redirect_uri: OAuth redirect URI (default: http://localhost:8080)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.redirect_uri = redirect_uri
        self.reddit = None
        self.username = None
        
    def _save_refresh_token(self, refresh_token):
        """Save refresh token to file for future use."""
        with open(TOKEN_FILE, 'w') as f:
            json.dump({'refresh_token': refresh_token}, f)
        print(f"Refresh token saved to {TOKEN_FILE}")
        
    def _load_refresh_token(self):
        """Load refresh token from file if it exists."""
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('refresh_token')
            except (json.JSONDecodeError, IOError):
                return None
        return None
        
    def authenticate(self):
        """
        Authenticate with Reddit using OAuth2 browser flow.
        Tries to use saved refresh token first, falls back to browser auth if needed.
        """
        # Try to use saved refresh token first
        refresh_token = self._load_refresh_token()
        
        if refresh_token:
            print("Found saved refresh token, attempting to use it...")
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent,
                    refresh_token=refresh_token
                )
                # Test the connection
                self.username = self.reddit.user.me().name
                print(f"Successfully authenticated as: {self.username}")
                return
            except Exception as e:
                print(f"Saved token invalid or expired: {e}")
                print("Proceeding with browser authentication...")
                # Remove invalid token file
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
        
        # Perform browser-based OAuth2 authentication
        print("\n" + "=" * 60)
        print("Browser-Based Authentication")
        print("=" * 60)
        print("A browser window will open for you to authorize this application.")
        print("After authorization, you'll be redirected back to this application.")
        print("=" * 60 + "\n")
        
        # Create Reddit instance for OAuth
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
            redirect_uri=self.redirect_uri
        )
        
        # Generate authorization URL
        scopes = ['identity', 'edit', 'history', 'read']
        auth_url = self.reddit.auth.url(scopes, 'random_state', 'permanent')
        
        print("Please open this URL in your browser:")
        print(auth_url)
        print()
        
        # Try to open browser automatically
        import webbrowser
        try:
            webbrowser.open(auth_url)
            print("Browser opened automatically. If not, please copy and paste the URL above.")
        except:
            print("Could not open browser automatically. Please copy and paste the URL above.")
        
        print("\nWaiting for authorization...")
        
        # Start local server to receive callback
        port = int(urlparse(self.redirect_uri).port or 8080)
        server = HTTPServer(('localhost', port), OAuthCallbackHandler)
        server.auth_code = None
        server.auth_error = None
        
        # Wait for one request (the callback)
        server.handle_request()
        
        if server.auth_error:
            raise Exception(f"Authentication failed: {server.auth_error}")
        
        if not server.auth_code:
            raise Exception("No authorization code received")
        
        # Exchange authorization code for refresh token
        refresh_token = self.reddit.auth.authorize(server.auth_code)
        
        # Save refresh token for future use
        self._save_refresh_token(refresh_token)
        
        # Get username
        self.username = self.reddit.user.me().name
        print(f"\nSuccessfully authenticated as: {self.username}")
        
    def overwrite_and_delete_comments(self, delay=2):
        """
        Overwrite and delete all comments for the authenticated user.
        
        Args:
            delay: Delay in seconds between operations (to avoid rate limiting)
            
        Returns:
            Tuple of (successful_count, failed_items) where failed_items is a list of tuples (id, error)
        """
        print(f"Fetching comments for user: {self.username}")
        user = self.reddit.redditor(self.username)
        
        comments = list(user.comments.new(limit=None))
        total_comments = len(comments)
        print(f"Found {total_comments} comments to process")
        
        failed_items = []
        successful_count = 0
        
        for index, comment in enumerate(comments, 1):
            try:
                print(f"[{index}/{total_comments}] Processing comment ID: {comment.id}")
                
                # Overwrite with replacement text
                try:
                    comment.edit(REPLACEMENT_TEXT)
                    print(f"  - Overwritten with replacement text")
                    time.sleep(delay)
                except Exception as edit_error:
                    print(f"  - Warning: Could not overwrite: {edit_error}")
                    # Still try to delete even if overwrite fails
                
                # Delete the comment
                comment.delete()
                print(f"  - Deleted")
                time.sleep(delay)
                successful_count += 1
                
            except Exception as e:
                error_msg = str(e)
                print(f"  - Error processing comment {comment.id}: {error_msg}")
                failed_items.append((comment.id, error_msg))
                continue
                
        print(f"\nCompleted: {successful_count}/{total_comments} comments processed successfully")
        if failed_items:
            print(f"Failed: {len(failed_items)} comments could not be processed")
        
        return successful_count, failed_items
        
    def overwrite_and_delete_posts(self, delay=2):
        """
        Overwrite and delete all posts (submissions) for the authenticated user.
        
        Args:
            delay: Delay in seconds between operations (to avoid rate limiting)
            
        Returns:
            Tuple of (successful_count, failed_items) where failed_items is a list of tuples (id, error)
        """
        print(f"\nFetching posts for user: {self.username}")
        user = self.reddit.redditor(self.username)
        
        posts = list(user.submissions.new(limit=None))
        total_posts = len(posts)
        print(f"Found {total_posts} posts to process")
        
        failed_items = []
        successful_count = 0
        
        for index, post in enumerate(posts, 1):
            try:
                print(f"[{index}/{total_posts}] Processing post ID: {post.id}")
                
                # Only edit if it's a text post (self post)
                if post.is_self:
                    try:
                        post.edit(REPLACEMENT_TEXT)
                        print(f"  - Overwritten with replacement text")
                        time.sleep(delay)
                    except Exception as edit_error:
                        print(f"  - Warning: Could not overwrite: {edit_error}")
                        # Still try to delete even if overwrite fails
                else:
                    print(f"  - Link post, skipping overwrite")
                
                # Delete the post
                post.delete()
                print(f"  - Deleted")
                time.sleep(delay)
                successful_count += 1
                
            except Exception as e:
                error_msg = str(e)
                print(f"  - Error processing post {post.id}: {error_msg}")
                failed_items.append((post.id, error_msg))
                continue
                
        print(f"\nCompleted: {successful_count}/{total_posts} posts processed successfully")
        if failed_items:
            print(f"Failed: {len(failed_items)} posts could not be processed")
        
        return successful_count, failed_items
        
    def delete_all(self, delay=2):
        """
        Delete all comments and posts for the authenticated user.
        
        Args:
            delay: Delay in seconds between operations (to avoid rate limiting)
        """
        print("=" * 60)
        print("Reddit Content Deletion Bot")
        print("=" * 60)
        print(f"Authenticated as: {self.username}")
        print("This will overwrite and delete ALL your posts and comments!")
        print("=" * 60)
        
        all_failed_items = []
        
        # Process comments first
        comment_success, comment_failures = self.overwrite_and_delete_comments(delay)
        all_failed_items.extend([("comment", item_id, error) for item_id, error in comment_failures])
        
        # Process posts
        post_success, post_failures = self.overwrite_and_delete_posts(delay)
        all_failed_items.extend([("post", item_id, error) for item_id, error in post_failures])
        
        print("\n" + "=" * 60)
        print("Deletion process completed!")
        print("=" * 60)
        
        # Display summary of failures if any
        if all_failed_items:
            print(f"\n⚠️  WARNING: {len(all_failed_items)} item(s) could not be processed:")
            for item_type, item_id, error in all_failed_items:
                print(f"  - {item_type} {item_id}: {error}")
            print("\nYou may want to manually check these items.")
        else:
            print("\n✓ All items processed successfully!")


def main():
    """Main entry point for the script."""
    from dotenv import load_dotenv
    
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Get credentials from environment variables
    client_id = os.environ.get('REDDIT_CLIENT_ID')
    client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
    user_agent = os.environ.get('REDDIT_USER_AGENT', 'RedditDeleter/1.0')
    redirect_uri = os.environ.get('REDDIT_REDIRECT_URI', 'http://localhost:8080')
    
    # Check if required credentials are provided
    if not all([client_id, client_secret]):
        print("Error: Missing required environment variables!")
        print("\nRequired environment variables:")
        print("  - REDDIT_CLIENT_ID")
        print("  - REDDIT_CLIENT_SECRET")
        print("  - REDDIT_USER_AGENT (optional, defaults to 'RedditDeleter/1.0')")
        print("  - REDDIT_REDIRECT_URI (optional, defaults to 'http://localhost:8080')")
        print("\nYou can set these in a .env file or export them directly.")
        print("See README.md for setup instructions.")
        sys.exit(1)
    
    # Create deleter instance and authenticate
    try:
        deleter = RedditDeleter(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            redirect_uri=redirect_uri
        )
        
        # Authenticate using OAuth2
        deleter.authenticate()
        
        # Prompt for confirmation
        print("\n" + "=" * 60)
        print("WARNING: This will DELETE all your Reddit posts and comments!")
        print("=" * 60)
        response = input("\nType 'DELETE' to confirm: ")
        
        if response.strip() == 'DELETE':
            deleter.delete_all()
        else:
            print("Deletion cancelled.")
            sys.exit(0)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
