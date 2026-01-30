# redditDeleted

A Python bot that overwrites and deletes all of your Reddit posts and comments.

## ⚠️ Warning

This bot will **permanently delete** all your Reddit posts and comments. This action **cannot be undone**. Use with caution!

## Features

- Overwrites all comments and posts with replacement text before deletion
- Processes both text posts and comments
- Rate limiting protection with configurable delays
- Progress tracking for all operations
- Detailed error reporting for failed items
- Confirmation prompt before deletion
- Automatic .env file loading for easy configuration

## How It Works

1. The bot fetches all your posts and comments using the Reddit API
2. For each comment:
   - Overwrites the content with replacement text ("[deleted]")
   - Deletes the comment
3. For each post:
   - Overwrites text posts (self posts) with replacement text ("[deleted]")
   - Deletes the post
4. All operations include delays to avoid Reddit's rate limiting
5. Failed operations are tracked and reported at the end

## Prerequisites

- Python 3.6 or higher
- A Reddit account
- Reddit API credentials (client ID and secret from a web app)

## Setup

### 1. Create a Reddit App

1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..." at the bottom
3. Fill in the form:
   - **name**: Choose any name (e.g., "RedditDeleter")
   - **App type**: Select "**web app**" (NOT "script")
   - **description**: Optional
   - **about url**: Optional
   - **redirect uri**: Use `http://localhost:8080` (this is required for OAuth)
4. Click "create app"
5. Note your **client ID** (under the app name) and **client secret**

**Important**: You must create a **web app**, not a "script" app. Web apps don't require Reddit approval and use browser-based OAuth authentication.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Credentials

Create a `.env` file in the project directory (use `.env.example` as a template):

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=RedditDeleter/1.0
REDDIT_REDIRECT_URI=http://localhost:8080
```

**Note**: You no longer need to provide your username and password. The app will use OAuth2 browser authentication instead.

## Usage

The bot will automatically load credentials from a `.env` file if one exists in the same directory.

### Authentication

When you run the script for the first time, it will:
1. Open your web browser automatically
2. Ask you to authorize the application on Reddit
3. Redirect you back to the application
4. Save a refresh token for future use (in `reddit_token.json`)

On subsequent runs, the saved token will be used automatically, so you won't need to authorize again unless the token expires.

### Method 1: Using .env file (Recommended)

Create a `.env` file in the project directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your credentials, then simply run:

```bash
python reddit_deleter.py
```

### Method 2: Setting environment variables directly

```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
python reddit_deleter.py
```

### Running the bot

When you run the script, it will:
1. Authenticate you via browser (first time only)
2. Display your username
3. Ask for confirmation by typing `DELETE`
4. Process all your comments first, then all your posts
5. Show progress for each item processed

**Example output:**

```
============================================================
Browser-Based Authentication
============================================================
A browser window will open for you to authorize this application.
After authorization, you'll be redirected back to this application.
============================================================

Please open this URL in your browser:
https://www.reddit.com/api/v1/authorize?...

Browser opened automatically. If not, please copy and paste the URL above.

Waiting for authorization...
Refresh token saved to reddit_token.json

Successfully authenticated as: your_username

============================================================
WARNING: This will DELETE all your Reddit posts and comments!
============================================================

Type 'DELETE' to confirm: DELETE
============================================================
Reddit Content Deletion Bot
============================================================
Authenticated as: your_username
This will overwrite and delete ALL your posts and comments!
============================================================
Fetching comments for user: your_username
Found 150 comments to process
[1/150] Processing comment ID: abc123
  - Overwritten with blank text
  - Deleted
[2/150] Processing comment ID: def456
  - Overwritten with blank text
  - Deleted
...
```

## Configuration

### Rate Limiting

By default, the bot waits 2 seconds between operations. You can modify the delay in the script if needed:

```python
deleter.delete_all(delay=2)  # Change delay value here
```

## Security Notes

- **Never commit your `.env` file** - it contains your Reddit API credentials
- **Never commit `reddit_token.json`** - it contains your OAuth refresh token
- Both files are already included in `.gitignore`
- Consider using a dedicated API-only account for bot operations
- After deletion, you can revoke the app's access at https://www.reddit.com/prefs/apps
- The refresh token is stored locally and can be deleted at any time by removing `reddit_token.json`

## Troubleshooting

### Authentication Errors

- Verify your client ID and client secret are correct
- Make sure you've created a "**web app**" type, not a "script" app
- Ensure the redirect URI in your app settings is `http://localhost:8080`
- If you get "invalid_grant" errors, delete `reddit_token.json` and re-authenticate
- Make sure no other application is using port 8080

### Browser Doesn't Open

- If the browser doesn't open automatically, copy and paste the URL shown in the terminal
- Make sure you're running the script in an environment where a browser is available
- If running on a remote server, you may need to manually handle the OAuth flow

### Rate Limiting

- If you get rate limited, the bot will show an error for that item and continue
- Increase the delay between operations if needed
- Reddit typically allows around 60 API requests per minute

### Missing Comments/Posts

- Reddit's API may not return all items immediately
- Some very old content might not be accessible
- Deleted or removed content won't appear in the list

## License

MIT

## Disclaimer

This tool is provided as-is. The authors are not responsible for any data loss or consequences of using this tool. Always make sure you want to delete your content before running the bot.