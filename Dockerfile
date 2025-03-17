FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Train the Rasa model
RUN cd backend/rasa_bot && rasa train

# Expose ports
EXPOSE 5005 5055 8000

# Create a script to run all services
RUN echo '#!/bin/bash\n\
cd /app/backend/rasa_bot && rasa run --enable-api --cors "*" --debug &\n\
cd /app/backend/rasa_bot && rasa run actions &\n\
cd /app/backend/flask_api && python app.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Set the entrypoint
ENTRYPOINT ["/app/start.sh"] 