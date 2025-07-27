#!/bin/bash
cd /home/pi/yourrepo

# Fetch latest changes
git fetch

# Check if there are any new commits
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ $LOCAL != $REMOTE ]; then
    echo "Updates found. Pulling changes..."
    git pull

    # Optional: Install dependencies if needed
    # pip install -r requirements.txt

    # Restart the app (choose one)
    pkill -f main.py && nohup python3 main.py &
    # pm2 restart your-app-name         # If using pm2
    # or kill and restart a Python script manually:
    # pkill -f your_script.py && nohup python3 your_script.py &
else
    echo "No updates found."
fi
