#!/bin/bash

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install -r requirements.txt

# Train Rasa model if it doesn't exist
if [ ! -d "backend/rasa_bot/models" ]; then
    echo "Training Rasa model..."
    cd backend/rasa_bot
    python -m rasa train
    cd ../..
fi

# Start Rasa server in the background
echo "Starting Rasa server..."
cd backend/rasa_bot
python -m rasa run --enable-api --cors "*" --debug > ../../rasa_server.log 2>&1 &
RASA_PID=$!
cd ../..

# Start Rasa actions server in the background
echo "Starting Rasa actions server..."
cd backend/rasa_bot
python -m rasa run actions > ../../rasa_actions.log 2>&1 &
ACTIONS_PID=$!
cd ../..

# Start Flask API server in the background
echo "Starting Flask API server..."
cd backend/flask_api
python app.py > ../../flask_api.log 2>&1 &
FLASK_PID=$!
cd ../..

echo "All services started!"
echo "Rasa server PID: $RASA_PID"
echo "Rasa actions server PID: $ACTIONS_PID"
echo "Flask API server PID: $FLASK_PID"
echo "Access the application at http://localhost:8000"
echo "Press Ctrl+C to stop all services"

# Function to kill all processes on exit
function cleanup {
    echo "Stopping all services..."
    kill $RASA_PID $ACTIONS_PID $FLASK_PID
    echo "All services stopped."
    exit 0
}

# Register the cleanup function for when Ctrl+C is pressed
trap cleanup SIGINT

# Keep the script running
while true; do
    sleep 1
done 