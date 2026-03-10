#!/bin/bash

# Full path to the project (cron doesn't know where you are)
PROJECT_DIR="/Users/macbookair/Desktop/subscription_automation"

# Move into the project folder
cd "$PROJECT_DIR"

# Activate the virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Run the automation
python3 "$PROJECT_DIR/app.py"
