#!/usr/bin/env python3
"""
Reddit Post and Comment Deletion Bot

This bot overwrites and deletes all posts and comments for a Reddit account.
It first overwrites the content with blank text, then deletes the content.
"""

import praw
import time
import sys


class RedditDeleter:
    def __init__(self, client_id, client_secret, username, password, user_agent):
        """
        Initialize the Reddit API connection.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            username: Reddit username
            password: Reddit password
            user_agent: User agent string for API requests
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent
        )
        self.username = username
        
    def overwrite_and_delete_comments(self, delay=2):
        """
        Overwrite and delete all comments for the authenticated user.
        
        Args:
            delay: Delay in seconds between operations (to avoid rate limiting)
        """
        print(f"Fetching comments for user: {self.username}")
        user = self.reddit.redditor(self.username)
        
        comments = list(user.comments.new(limit=None))
        total_comments = len(comments)
        print(f"Found {total_comments} comments to process")
        
        for index, comment in enumerate(comments, 1):
            try:
                print(f"[{index}/{total_comments}] Processing comment ID: {comment.id}")
                
                # Overwrite with blank text
                comment.edit("")
                print(f"  - Overwritten with blank text")
                time.sleep(delay)
                
                # Delete the comment
                comment.delete()
                print(f"  - Deleted")
                time.sleep(delay)
                
            except Exception as e:
                print(f"  - Error processing comment {comment.id}: {e}")
                continue
                
        print(f"\nCompleted processing {total_comments} comments")
        
    def overwrite_and_delete_posts(self, delay=2):
        """
        Overwrite and delete all posts (submissions) for the authenticated user.
        
        Args:
            delay: Delay in seconds between operations (to avoid rate limiting)
        """
        print(f"\nFetching posts for user: {self.username}")
        user = self.reddit.redditor(self.username)
        
        posts = list(user.submissions.new(limit=None))
        total_posts = len(posts)
        print(f"Found {total_posts} posts to process")
        
        for index, post in enumerate(posts, 1):
            try:
                print(f"[{index}/{total_posts}] Processing post ID: {post.id}")
                
                # Only edit if it's a text post (self post)
                if post.is_self:
                    post.edit("")
                    print(f"  - Overwritten with blank text")
                    time.sleep(delay)
                else:
                    print(f"  - Link post, skipping overwrite")
                
                # Delete the post
                post.delete()
                print(f"  - Deleted")
                time.sleep(delay)
                
            except Exception as e:
                print(f"  - Error processing post {post.id}: {e}")
                continue
                
        print(f"\nCompleted processing {total_posts} posts")
        
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
        
        # Process comments first
        self.overwrite_and_delete_comments(delay)
        
        # Process posts
        self.overwrite_and_delete_posts(delay)
        
        print("\n" + "=" * 60)
        print("Deletion process completed!")
        print("=" * 60)


def main():
    """Main entry point for the script."""
    import os
    
    # Get credentials from environment variables
    client_id = os.environ.get('REDDIT_CLIENT_ID')
    client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
    username = os.environ.get('REDDIT_USERNAME')
    password = os.environ.get('REDDIT_PASSWORD')
    user_agent = os.environ.get('REDDIT_USER_AGENT', 'RedditDeleter/1.0')
    
    # Check if all required credentials are provided
    if not all([client_id, client_secret, username, password]):
        print("Error: Missing required environment variables!")
        print("\nRequired environment variables:")
        print("  - REDDIT_CLIENT_ID")
        print("  - REDDIT_CLIENT_SECRET")
        print("  - REDDIT_USERNAME")
        print("  - REDDIT_PASSWORD")
        print("  - REDDIT_USER_AGENT (optional, defaults to 'RedditDeleter/1.0')")
        print("\nSee README.md for setup instructions.")
        sys.exit(1)
    
    # Create deleter instance and run
    try:
        deleter = RedditDeleter(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent
        )
        
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
        sys.exit(1)


if __name__ == "__main__":
    main()
