# redditDeleted

A Python bot that overwrites and deletes all of your Reddit posts and comments.

## ⚠️ Warning

This bot will **permanently delete** all your Reddit posts and comments. This action **cannot be undone**. Use with caution!

## Features

- Overwrites all comments and posts with blank text before deletion
- Processes both text posts and comments
- Rate limiting protection with configurable delays
- Progress tracking for all operations
- Confirmation prompt before deletion

## How It Works

1. The bot fetches all your posts and comments using the Reddit API
2. For each comment:
   - Overwrites the content with blank text
   - Deletes the comment
3. For each post:
   - Overwrites text posts (self posts) with blank text
   - Deletes the post
4. All operations include delays to avoid Reddit's rate limiting

## Prerequisites

- Python 3.6 or higher
- A Reddit account
- Reddit API credentials (client ID and secret)

## Setup

### 1. Create a Reddit App

1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..." at the bottom
3. Fill in the form:
   - **name**: Choose any name (e.g., "RedditDeleter")
   - **App type**: Select "script"
   - **description**: Optional
   - **about url**: Optional
   - **redirect uri**: Use `http://localhost:8080` (required but not used)
4. Click "create app"
5. Note your **client ID** (under the app name) and **client secret**

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
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_USER_AGENT=RedditDeleter/1.0
```

## Usage

### Using environment variables from .env file

If you have a `.env` file, export the variables:

```bash
export $(cat .env | xargs)
python reddit_deleter.py
```

### Setting environment variables directly

```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USERNAME="your_username"
export REDDIT_PASSWORD="your_password"
python reddit_deleter.py
```

### Running the bot

When you run the script, it will:
1. Display your username
2. Ask for confirmation by typing `DELETE`
3. Process all your comments first, then all your posts
4. Show progress for each item processed

**Example output:**

```
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

- **Never commit your `.env` file** - it contains your Reddit password and API credentials
- The `.env` file is already included in `.gitignore`
- Consider using a dedicated API-only account for bot operations
- After deletion, remember to revoke the app's access at https://www.reddit.com/prefs/apps

## Troubleshooting

### Authentication Errors

- Verify your credentials are correct
- Make sure you've created a "script" type app, not a "web app"
- Check that your Reddit account password is current

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