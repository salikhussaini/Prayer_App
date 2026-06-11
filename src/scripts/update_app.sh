#!/bin/bash
# ==============================================================================
# Prayer App Maintenance & Update Script (Linux/Raspberry Pi)
# ==============================================================================

# Configuration
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../" && pwd)"
PYTHON_CMD="python3"
MAIN_SCRIPT="main.py"

echo "Checking for updates in $APP_DIR..."
cd "$APP_DIR" || exit 1

# Check for git repository
if [ ! -d ".git" ]; then
    echo "Error: Not a git repository."
    exit 1
fi

# Fetch latest changes
git fetch --quiet

# Compare local vs remote
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "Updates found. Pulling changes..."
    
    # Backup current database before update
    if [ -f "data/prayer_times.db" ]; then
        echo "Backing up database..."
        cp "data/prayer_times.db" "data/prayer_times.db.bak_$(date +%Y%m%d_%H%M%S)"
    fi

    git pull --quiet

    # Install/Update dependencies
    if [ -f "requirements.txt" ]; then
        echo "Updating dependencies..."
        $PYTHON_CMD -m pip install -r requirements.txt --quiet
    fi

    echo "Restarting application..."
    # Graceful shutdown (sends SIGTERM)
    pkill -15 -f "$MAIN_SCRIPT" 2>/dev/null
    sleep 2
    # Force kill if still running
    pkill -9 -f "$MAIN_SCRIPT" 2>/dev/null

    # Start the app in background
    nohup $PYTHON_CMD "$MAIN_SCRIPT" > /dev/null 2>&1 &
    
    echo "Update complete. Application restarted."
else
    echo "Application is already up to date."
fi

