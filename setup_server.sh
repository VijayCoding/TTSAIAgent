#!/bin/bash

# Server setup script for Ubuntu
echo "Setting up TTSAIAgent on Ubuntu server..."

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python3 and pip if not already installed
echo "Installing Python3 and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Install system dependencies for audio processing and TTS
echo "Installing system dependencies..."
sudo apt install -y ffmpeg espeak espeak-data libespeak1 libespeak-dev festival festvox-kallpc16k

# Install additional dependencies for TTS
sudo apt install -y build-essential python3-dev

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python requirements
echo "Installing Python packages..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p Voice Sounds Downloads

# Make the application executable
chmod +x app.py

echo "Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the app: python3 app.py"
echo ""
echo "The server will be accessible at http://YOUR_SERVER_IP:5000"
