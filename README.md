# Healthcare Symptom Analysis Chatbot

Healmate - A healthcare chatbot that analyzes symptoms and provides health information using natural language processing and medical APIs.

## Features

- Natural language understanding with Rasa and spaCy
- Symptom analysis using EndlessMedical API
- Responsive web interface
- Health information lookup
- Conversational AI capabilities

## Tech Stack

- **Backend**:
  - Rasa for NLP and dialogue management
  - Flask for API endpoints
  - spaCy + DIETClassifier for intent classification
  - EndlessMedical API for symptom analysis

- **Frontend**:
  - HTML/CSS/JavaScript
  - Responsive design
  - Modern UI with chat interface

## Project Structure

```
healthcare-chatbot/
├── backend/
│   ├── rasa_bot/
│   │   ├── data/
│   │   │   ├── nlu.yml
│   │   │   ├── stories.yml
│   │   │   └── rules.yml
│   │   ├── actions/
│   │   │   └── actions.py
│   │   ├── config.yml
│   │   └── domain.yml
│   └── flask_api/
│       └── app.py
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   └── script.js
│   │   └── images/
│   └── templates/
│       └── index.html
└── requirements.txt
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js and npm (for frontend development)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/healthcare-chatbot.git
   cd healthcare-chatbot
   ```

2. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Download the spaCy language model:
   ```
   python -m spacy download en_core_web_md
   ```

### Running the Application

1. Train the Rasa model:
   ```
   cd backend/rasa_bot
   rasa train
   ```

2. Start the Rasa server (in one terminal):
   ```
   rasa run --enable-api --cors "*" --debug
   ```

3. Start the Rasa actions server (in another terminal):
   ```
   rasa run actions
   ```

4. Start the Flask API server (in another terminal):
   ```
   cd backend/flask_api
   python app.py
   ```

5. Access the application in your browser:
   ```
   http://localhost:8000
   ```

## Usage

1. Open the application in your web browser
2. Type your symptoms or health questions in the chat input
3. The chatbot will analyze your symptoms and provide relevant information
4. For symptom analysis, the chatbot may ask follow-up questions to gather more information

## Disclaimer

This chatbot is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Rasa](https://rasa.com/) for the open-source conversational AI framework
- [EndlessMedical API](https://endlessmedical.com/) for symptom analysis
- [spaCy](https://spacy.io/) for natural language processing
- [Flask](https://flask.palletsprojects.com/) for the web framework