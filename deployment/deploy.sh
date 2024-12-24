#!/bin/bash

# Exit on error
set -e

# Configuration
APP_DIR="/path/to/webp-editor"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="/var/log/webp-editor"
SERVICE_NAME="webp-editor"

# Create necessary directories
sudo mkdir -p $LOG_DIR
sudo chown www-data:www-data $LOG_DIR

# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip nginx

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
fi

# Activate virtual environment and install dependencies
source $VENV_DIR/bin/activate
pip install -r $APP_DIR/app/requirements.txt

# Copy and configure Nginx
sudo cp $APP_DIR/deployment/nginx.conf /etc/nginx/sites-available/$SERVICE_NAME
sudo ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup systemd service
sudo cp $APP_DIR/deployment/webp-editor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

# Set permissions
sudo chown -R www-data:www-data $APP_DIR/app/static/uploads

echo "Deployment completed successfully!"
echo "Check service status with: sudo systemctl status $SERVICE_NAME" 