from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import os
import logging

app = Flask(__name__, static_folder="../../frontend/static", template_folder="../../frontend/templates")
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rasa server URL
RASA_API_URL = os.environ.get("RASA_API_URL", "http://localhost:5005/webhooks/rest/webhook")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'default_user')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Forward the message to Rasa
        rasa_payload = {
            "sender": user_id,
            "message": user_message
        }
        
        logger.info(f"Sending message to Rasa: {user_message}")
        response = requests.post(RASA_API_URL, json=rasa_payload)
        
        if not response.ok:
            logger.error(f"Error from Rasa: {response.status_code} - {response.text}")
            return jsonify({"error": "Failed to get response from chatbot"}), 500
        
        rasa_response = response.json()
        
        # Extract text responses from Rasa
        messages = []
        for msg in rasa_response:
            if "text" in msg:
                messages.append({"text": msg["text"], "type": "bot"})
            elif "image" in msg:
                messages.append({"image": msg["image"], "type": "bot"})
            elif "custom" in msg:
                messages.append({"custom": msg["custom"], "type": "bot"})
        
        if not messages:
            messages.append({"text": "I'm not sure how to respond to that.", "type": "bot"})
        
        return jsonify({"messages": messages})
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/health')
def health_check():
    try:
        # Check if Rasa server is running
        rasa_health = requests.get(RASA_API_URL.replace("/webhooks/rest/webhook", "/"))
        rasa_status = "up" if rasa_health.ok else "down"
    except:
        rasa_status = "down"
    
    return jsonify({
        "status": "healthy",
        "rasa_status": rasa_status
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=True) 