from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import json

app = Flask(__name__)

# Groq API configuration
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GROQ_API_KEY}"
}

# Read system prompt from system.txt
try:
    with open("system.txt", "r") as file:
        SYSTEM_PROMPT = file.read().strip()
except FileNotFoundError:
    SYSTEM_PROMPT = "You are a concise assistant, keep replies under 500 chars."  # Fallback
    print("Warning: system.txt not found, using default prompt")

def get_groq_response(message):
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        "max_tokens": 100  # Adjusted for ~500 chars (assuming ~5 chars/token)
    }
    try:
        response = requests.post(GROQ_API_URL, headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        reply = result["choices"][0]["message"]["content"].strip()
        print(f"Groq Response: {reply}")
        return reply[:500]  # Enforce 500-character limit
    except requests.exceptions.RequestException as e:
        error_msg = f"API Error: {str(e)}"
        print(error_msg)
        return error_msg[:500]

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')

    print(f"Incoming Message from {from_number}: {incoming_msg}")

    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg:
        groq_reply = get_groq_response(incoming_msg)
        msg.body(groq_reply)
    else:
        default_reply = "Send a message!"
        print(f"Default Response: {default_reply}")
        msg.body(default_reply)

    print(f"Sending to WhatsApp: {msg.body}")
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, port=4000)