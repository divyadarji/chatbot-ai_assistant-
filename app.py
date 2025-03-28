import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from time import time

app = Flask(__name__)

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyAEBgrMIe8iT1K9RnodUgOqyq3sm1KVujA"  # Replace with your actual Gemini API key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Load website context
with open("website_info.txt", "r") as f:
    website_info = f.read()

# Predefined Q&A for suggested questions
predefined_qa = {
    "what is your website about?": "TechNova Solutions helps users with technology services, careers, and technical support.",
    "how can i contact support?": "You can reach us via this chatbot or email at support@technova.com. Want to raise a ticket?",
    "what are your hours?": "We provide 24/7 support through our chatbot and email."
}

# Store conversation history
conversation_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message').lower().strip()
    conversation_history.append({"role": "user", "text": user_input})

    # Check predefined Q&A
    for question, answer in predefined_qa.items():
        if question.lower() in user_input or user_input in question.lower():
            response = answer
            conversation_history.append({"role": "bot", "text": response})
            return jsonify({"response": response})

    # Detect intent to contact the owner
    contact_intent = ["contact", "reach", "talk to", "owner", "team", "support", "email", "message"]
    if any(intent in user_input for intent in contact_intent):
        response = "Would you like to raise a ticket to contact the owner? Say 'yes' or provide your name, email, and issue directly."
        conversation_history.append({"role": "bot", "text": response})
        return jsonify({"response": response})

    # Handle ticket confirmation
    if "yes" in user_input and any(intent in " ".join([msg["text"] for msg in conversation_history[-2:]]) for intent in contact_intent):
        response = "Please fill out the form with your name, email, phone number, and issue description."
        conversation_history.append({"role": "bot", "text": response})
        return jsonify({"response": response, "collect_details": True})

    # Process direct contact details from chat
    if "my name is" in user_input or "email" in user_input or "issue" in user_input:
        response = process_direct_contact(user_input)
        if response:
            conversation_history.append({"role": "bot", "text": response})
            return jsonify({"response": response})

    # Use Gemini API with website context
    prompt = f"You are a chatbot for the TechNova Solutions website. Here is the website info: {website_info}\n\nAnswer the user's query concisely based on this info if relevant: {user_input}\nIf unrelated to the website, provide a short, helpful response."
    chat_session = model.start_chat(history=[{"role": "user", "parts": [prompt]}])
    response = chat_session.send_message(user_input).text.strip()
    conversation_history.append({"role": "bot", "text": response})
    return jsonify({"response": response})

def process_direct_contact(user_input):
    name, email, issue = None, None, None
    words = user_input.split()
    for i, word in enumerate(words):
        if "name" in word and i + 2 < len(words):
            name = words[i + 2]
        if "email" in word and i + 1 < len(words):
            email = words[i + 1]
        if "issue" in word or "problem" in word:
            issue = " ".join(words[i + 1:])
    if name and email and issue:
        sentiment = analyze_sentiment(issue)
        ticket_id = f"TICKET-{int(time())}"
        ticket = f"Ticket Raised:\nID: {ticket_id}\nName: {name}\nEmail: {email}\nIssue: {issue}\nSentiment: {sentiment}"
        print(ticket)
        conversation_history.clear()
        return f"Thank you! Ticket {ticket_id} raised. We’ll contact you at {email} soon."
    elif name or email or issue:
        return "Please provide all details: name, email, and issue."
    return None

def analyze_sentiment(text):
    prompt = f"Analyze the sentiment of this text: '{text}'. Return only 'positive', 'negative', or 'neutral'."
    chat_session = model.start_chat(history=[{"role": "user", "parts": [prompt]}])
    response = chat_session.send_message(text).text.strip().lower()
    return response if response in ["positive", "negative", "neutral"] else "neutral"

@app.route('/submit_details', methods=['POST'])
def submit_details():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    number = data.get('number')
    issue = data.get('issue')

    sentiment = analyze_sentiment(issue)
    ticket_id = f"TICKET-{int(time())}"
    ticket = f"Ticket Raised:\nID: {ticket_id}\nName: {name}\nEmail: {email}\nNumber: {number}\nIssue: {issue}\nSentiment: {sentiment}"
    print(ticket)

    conversation_history.clear()
    response = f"Thank you! Ticket {ticket_id} raised. We’ll contact you at {email} soon."
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)