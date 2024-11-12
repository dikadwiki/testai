from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS
app.secret_key = os.urandom(24)

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

@app.route('/')
def home():
    if 'chat_history' not in session:
        session['chat_history'] = []
        welcome_message = {
            'role': 'assistant',
            'content': 'Hallo Saya adalah Dwiki BOT, saya akan menjawab pertanyaan apapun dari kalian :)',
            'timestamp': datetime.now().strftime("%H:%M")
        }
        session['chat_history'].append(welcome_message)
    return render_template('index.html', messages=session['chat_history'])

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    session['chat_history'].append({
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now().strftime("%H:%M")
    })
    messages = [
        {"role": "system", "content": "anything"}
    ]
    recent_messages = session['chat_history'][-7:]
    for msg in recent_messages:
        messages.append({
            "role": "user" if msg['role'] == 'user' else "assistant",
            "content": msg['content']
        })
    
    messages.append({"role": "user", "content": user_message})
    
    completion = client.chat.completions.create(
        model="grok-beta",
        messages=messages
    )
    
    bot_response = completion.choices[0].message.content
    timestamp = datetime.now().strftime("%H:%M")
    
    session['chat_history'].append({
        'role': 'assistant',
        'content': bot_response,
        'timestamp': timestamp
    })
    session.modified = True
    
    return jsonify({
        "response": bot_response,
        "timestamp": timestamp
    })

@app.route('/clear', methods=['POST'])
def clear_chat():
    session['chat_history'] = []
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
