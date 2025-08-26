#!/bin/bash
source /script/common.sh

log_message "RUNNING" "start-wine-fastapi.sh"
log_message "INFO" "Starting FastAPI server in Wine environment..."

# Run the FastAPI app using Uvicorn inside Wine
# Replace 'app:app' with the path to your FastAPI app object
wine python -m uvicorn main:app --host 0.0.0.0 --port 8000 &

FASTAPI_PID=$!

# Give the server some time to start
sleep 5

# Check if the FastAPI server is running
if ps -p $FASTAPI_PID > /dev/null; then
    log_message "INFO" "FastAPI server in Wine started successfully with PID $FASTAPI_PID."
else
    log_message "ERROR" "Failed to start FastAPI server in Wine."
    exit 1
fi
Notes: