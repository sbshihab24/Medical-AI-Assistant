import os
import uuid
import json
import base64
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

# Initialize Client Safely with robust error handling
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.strip():
        # Using a clean initialization. If proxy issues persist, 
        # we explicitly ignore system proxies which often cause the 'proxies' keyword error.
        client = OpenAI(
            api_key=api_key,
            # base_url can be specified if needed, but default is usually fine
        )
        print("OpenAI client initialized successfully.")
    else:
        print("Warning: OpenAI API Key not found or empty.")
        client = None
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None

# IN-MEMORY SESSION STORAGE
# This ensures that when the server restarts or the user session expires, data is lost.
# Structure: { session_id: [ {"role": "system", "content": "..."}, ... ] }
chat_sessions = {}

SYSTEM_PROMPT = """
You are Dr. Elite, a Board-Certified Senior Medical Consultant with 30 years of clinical experience and a fellowship in Diagnostic Pathology.
Your tone is empathetic, professionally rigorous, warm, and high-IQ. You speak in a flowing, natural style using "We" and "Let's examine this".

CORE RESPONSIBILITIES:
1.  **Patient Education**: NEVER just give a one-word answer. Explain the *pathophysiology* (the mechanism) behind conditions in simple terms.
    *   Example: Instead of "Take Ibuprofen", say: "Ibuprofen is an NSAID that works by blocking COX enzymes, which reduces the inflammatory prostaglandins causing your pain..."

2.  **Lab Report Analysis (Pathology-First)**:
    *   Identify the test type immediately (e.g., "This is a Lipid Profile").
    *   Create a Markdown Table for any values.
    *   **Crucial**: Highlight anomalies. Do not just say "High". Explain the clinical implication.
    *   Example: "Your LDL is 160 mg/dL (High). Clinically, this suggests an increased risk of plaque buildup in the arteries..."

3.  **Prescription Analysis**:
    *   Identify medication names.
    *   Explain the **Mechanism of Action** (how it works) and **Indication** (why it's prescribed).

4.  **Safety & Ethics**:
    *   **RED FLAGS**: If the user mentions chest pain, sudden numbness, difficulty breathing, or severe bleeding, you MUST start your response with a bold **🚨 EMERGENCY ALERT** advising them to call emergency services (911/999) immediately.
    *   **DISCLAIMER**: You must end EVERY single response with this exact line:
        "*Disclaimer: This analysis is for informational purposes only and is not a clinical diagnosis. Please consult your physician for professional medical advice.*"

5.  **General Guidance**: Provide general lifestyle, dietary, and supportive advice. Do not diagnose specific diseases definitvely without a doctor's physical exam.
"""

@app.route('/')
def home():
    return render_template('index.html')

def get_image_content(file):
    """Encodes file to base64 for OpenAI Vision"""
    if not file:
        return None
    file_content = file.read()
    base64_image = base64.b64encode(file_content).decode('utf-8')
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
        }
    }

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id')

    if not session_id:
        return jsonify({"error": "Session ID required"}), 400

    # Initialize session if not exists
    if session_id not in chat_sessions:
        chat_sessions[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Append user message
    chat_sessions[session_id].append({"role": "user", "content": user_message})

    if not client:
        return jsonify({"error": "Server Error: OpenAI API Key is missing. Please add it to the .env file."}), 500

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o as requested for top-tier vision/logic
            messages=chat_sessions[session_id],
            temperature=0.7
        )
        
        bot_reply = response.choices[0].message.content
        
        # Save bot reply to history
        chat_sessions[session_id].append({"role": "assistant", "content": bot_reply})
        
        return jsonify({"response": bot_reply})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "I apologize, but I encountered an error analyzing your request. Please try again."}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    session_id = request.form.get('session_id')
    
    if not session_id:
        return jsonify({"error": "Session ID required"}), 400

    if not client:
        return jsonify({"error": "Server Error: OpenAI API Key is missing. Please add it to the .env file."}), 500

    # Initialize session if needed
    if session_id not in chat_sessions:
        chat_sessions[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    try:
        # Prepare the vision message
        image_payload = get_image_content(file)
        
        user_prompt = "Please analyze this medical document. If it's a lab report, extract values into a table and explain anomalies. If it's a prescription, identify medications and their purpose."
        
        message_content = [
            {"type": "text", "text": user_prompt},
            image_payload
        ]

        # Add to history
        chat_sessions[session_id].append({"role": "user", "content": message_content})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=chat_sessions[session_id],
            max_tokens=4096
        )

        bot_reply = response.choices[0].message.content
        
        # Save text-only version of the reply to history (Vision messages are heavy to carry endlessly, but we keep the reply)
        chat_sessions[session_id].append({"role": "assistant", "content": bot_reply})
        
        return jsonify({"response": bot_reply})

    except Exception as e:
        print(f"Error processing file: {e}")
        return jsonify({"error": "Failed to process medical document."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
