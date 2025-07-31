#!/bin/bash

# Deployment script for TTSAIAgent Flask app
SERVER_IP="172.19.4.6"  # Replace with your actual server IP
SERVER_USER="ubuntu"
REMOTE_PATH="/home/ubuntu/TTSAIAgent"

echo "Deploying TTSAIAgent to $SERVER_USER@$SERVER_IP:$REMOTE_PATH"

# Create remote directory
ssh $SERVER_USER@$SERVER_IP "mkdir -p $REMOTE_PATH"

# Copy all necessary files
echo "Copying application files..."
scp -r app.py main.py requirements.txt Voice/ setup_server.sh app_production.py ttsaiagent.service $SERVER_USER@$SERVER_IP:$REMOTE_PATH/

# Copy ai_agent folder if it has content
if [ -d "ai_agent" ] && [ "$(ls -A ai_agent)" ]; then
    scp -r ai_agent/ $SERVER_USER@$SERVER_IP:$REMOTE_PATH/
fi

echo "Files copied successfully!"
echo "Next steps:"
echo "1. SSH into the server: ssh $SERVER_USER@$SERVER_IP"
echo "2. Navigate to the project: cd $REMOTE_PATH"
echo "3. Run the setup script: bash setup_server.sh"
