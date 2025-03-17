from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import json
import logging

logger = logging.getLogger(__name__)

# EndlessMedical API endpoints
ENDLESS_MEDICAL_BASE_URL = "https://api.endlessmedical.com/v1/dx/"
INIT_SESSION = "InitSession"
UPDATE_SYMPTOM = "UpdateSymptom"
ANALYZE = "Analyze"
GET_SUGGESTED_SYMPTOMS = "GetSuggestedSymptoms"

class ActionAnalyzeSymptoms(Action):
    def name(self) -> Text:
        return "action_analyze_symptoms"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract entities from the latest message
        latest_message = tracker.latest_message
        entities = latest_message.get('entities', [])
        
        # Get existing slot values
        symptoms = tracker.get_slot("symptoms") or []
        body_parts = tracker.get_slot("body_parts") or []
        duration = tracker.get_slot("duration")
        severity = tracker.get_slot("severity")
        
        # Extract new entities from the latest message
        new_symptoms = []
        new_body_parts = []
        
        for entity in entities:
            if entity["entity"] == "symptom":
                new_symptoms.append(entity["value"])
            elif entity["entity"] == "body_part":
                new_body_parts.append(entity["value"])
            elif entity["entity"] == "duration" and not duration:
                duration = entity["value"]
            elif entity["entity"] == "severity" and not severity:
                severity = entity["value"]
        
        # Combine new and existing entities
        symptoms = list(set(symptoms + new_symptoms))
        body_parts = list(set(body_parts + new_body_parts))
        
        # Prepare events to update slots
        events = []
        if symptoms:
            events.append(SlotSet("symptoms", symptoms))
        if body_parts:
            events.append(SlotSet("body_parts", body_parts))
        if duration:
            events.append(SlotSet("duration", duration))
        if severity:
            events.append(SlotSet("severity", severity))
        
        if not symptoms:
            dispatcher.utter_message(text="I need to know your symptoms to analyze them. Could you please describe what you're experiencing?")
            return events
        
        ### 
        try:
            # Initialize session with EndlessMedical API
            init_response = requests.get(f"{ENDLESS_MEDICAL_BASE_URL}{INIT_SESSION}")
            init_data = init_response.json()
            
            if not init_response.ok or not init_data.get("SessionID"):
                dispatcher.utter_message(text="I'm having trouble connecting to our medical database. Please try again later.")
                return events
            
            session_id = init_data.get("SessionID")
            
            # Accept terms (required by EndlessMedical API)
            accept_terms_url = f"{ENDLESS_MEDICAL_BASE_URL}AcceptTermsOfUse?SessionID={session_id}&passphrase=I have read, understood and I accept and agree to comply with the Terms of Use of EndlessMedical Services and Endless Medical API."
            requests.get(accept_terms_url)
            
            # Map symptoms to EndlessMedical API format
            symptom_mapping = {
                "headache": "Headache",
                "fever": "Fever",
                "cough": "Cough",
                "sore throat": "SoreThroat",
                "chest pain": "ChestPain",
                "abdominal pain": "AbdominalPain",
                "nausea": "Nausea",
                "vomiting": "Vomiting",
                "dizziness": "Dizziness",
                "fatigue": "Fatigue",
                # Add more mappings as needed
            }
            
            # Update symptoms in the API
            for symptom in symptoms:
                symptom_key = symptom_mapping.get(symptom.lower(), symptom)
                # Default to 1 (present) if no severity is provided
                symptom_value = 1
                
                # Adjust value based on severity if provided
                if severity:
                    if "mild" in severity.lower():
                        symptom_value = 0.3
                    elif "moderate" in severity.lower():
                        symptom_value = 0.6
                    elif "severe" in severity.lower() or "high" in severity.lower():
                        symptom_value = 1.0
                
                update_url = f"{ENDLESS_MEDICAL_BASE_URL}{UPDATE_SYMPTOM}?SessionID={session_id}&name={symptom_key}&value={symptom_value}"
                update_response = requests.get(update_url)
                
                if not update_response.ok:
                    logger.error(f"Failed to update symptom {symptom}: {update_response.text}")
            
            # Analyze symptoms
            analyze_url = f"{ENDLESS_MEDICAL_BASE_URL}{ANALYZE}?SessionID={session_id}"
            analyze_response = requests.get(analyze_url)
            
            if not analyze_response.ok:
                dispatcher.utter_message(text="I couldn't analyze your symptoms at this time. Please try again later.")
                return events
            
            analyze_data = analyze_response.json()
            
            # Get top 3 possible conditions
            possible_conditions = analyze_data.get("Diseases", {})
            sorted_conditions = sorted(possible_conditions.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Prepare response
            response = "Based on the symptoms you've described, here are some possible conditions:\n\n"
            
            for condition, probability in sorted_conditions:
                prob_percentage = round(probability * 100, 1)
                response += f"- {condition}: {prob_percentage}% probability\n"
            
            response += "\nPlease note that this is not a diagnosis. Consult with a healthcare professional for proper medical advice."
            
            # Get suggested follow-up symptoms to ask about
            suggested_url = f"{ENDLESS_MEDICAL_BASE_URL}{GET_SUGGESTED_SYMPTOMS}?SessionID={session_id}"
            suggested_response = requests.get(suggested_url)
            
            if suggested_response.ok:
                suggested_data = suggested_response.json()
                suggested_symptoms = suggested_data.get("SuggestedSymptoms", [])[:3]
                
                if suggested_symptoms:
                    response += "\n\nTo refine the analysis, do you also have any of these symptoms?\n"
                    for symptom in suggested_symptoms:
                        response += f"- {symptom}\n"
            
            dispatcher.utter_message(text=response)
            
            return events
            
        except Exception as e:
            logger.error(f"Error in symptom analysis: {str(e)}")
            dispatcher.utter_message(text="I encountered an error while analyzing your symptoms. Please try again later.")
            return events


class ActionProvideHealthInfo(Action):
    def name(self) -> Text:
        return "action_provide_health_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract the symptom or condition the user is asking about
        entities = tracker.latest_message.get("entities", [])
        symptom = None
        
        for entity in entities:
            if entity["entity"] == "symptom":
                symptom = entity["value"]
                break
        
        if not symptom:
            dispatcher.utter_message(text="I'm not sure what health information you're looking for. Could you specify a symptom or condition?")
            return []
        
        # Basic health information for common symptoms
        health_info = {
            "headache": "Headaches can be caused by stress, dehydration, lack of sleep, or more serious conditions. For occasional headaches, rest, hydration, and over-the-counter pain relievers may help. If headaches are severe or persistent, consult a doctor.",
            
            "fever": "Fever is often a sign that your body is fighting an infection. Rest, stay hydrated, and take fever reducers if needed. Seek medical attention if fever is very high (above 103°F/39.4°C), lasts more than three days, or is accompanied by severe symptoms.",
            
            "cough": "Coughs can be caused by viral infections, allergies, or irritants. Stay hydrated and use cough drops for relief. See a doctor if your cough lasts more than two weeks, produces thick discolored mucus, or is accompanied by high fever.",
            
            "sore throat": "Sore throats are often caused by viral infections. Gargling with salt water, drinking warm liquids, and using throat lozenges may help. If your sore throat is severe, lasts longer than a week, or is accompanied by difficulty swallowing, seek medical attention.",
            
            "chest pain": "Chest pain can be serious and may indicate heart problems. If you're experiencing chest pain, especially if it's severe or accompanied by shortness of breath, sweating, or nausea, seek emergency medical attention immediately.",
            
            "abdominal pain": "Abdominal pain can have many causes, from gas and indigestion to more serious conditions. If pain is severe, persistent, or accompanied by fever, vomiting, or blood in stool, consult a healthcare provider.",
            
            "nausea": "Nausea can be caused by digestive issues, motion sickness, or infections. Stay hydrated, eat small bland meals, and rest. If nausea persists or is accompanied by severe vomiting, seek medical attention.",
            
            "rash": "Rashes can be caused by allergies, infections, or skin conditions. Keep the area clean and avoid scratching. If a rash is widespread, painful, or accompanied by fever, consult a healthcare provider.",
            
            "joint pain": "Joint pain can be caused by injury, arthritis, or overuse. Rest, ice, and over-the-counter pain relievers may help. If pain is severe, persistent, or accompanied by swelling and redness, see a doctor.",
            
            "difficulty breathing": "Difficulty breathing is a serious symptom that requires immediate medical attention, especially if it comes on suddenly or is severe."
        }
        
        # Provide information if available, or a generic response
        response = health_info.get(
            symptom.lower(),
            f"I don't have specific information about {symptom}. It's best to consult with a healthcare professional for accurate advice."
        )
        
        dispatcher.utter_message(text=response)
        
        return [] 