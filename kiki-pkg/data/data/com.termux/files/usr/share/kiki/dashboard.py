#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import subprocess
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kiki-ai-secret-key'
CORS(app)

db_path = os.path.expanduser('~/.kiki/kiki.db')
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS conversations
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   timestamp DATETIME,
                   question TEXT,
                   answer TEXT,
                   mode TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS settings
                  (key TEXT PRIMARY KEY,
                   value TEXT)''')
conn.commit()

default_settings = {
    'theme': 'glass',
    'personality': 'friendly',
    'response_length': 'medium',
    'current_mode': 'standard'
}
for key, value in default_settings.items():
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, value))
conn.commit()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question', '')
    cursor.execute('SELECT key, value FROM settings')
    settings = dict(cursor.fetchall())
    mode = settings.get('current_mode', 'standard')
    prompts = {
        'standard': "You are KIKI, a helpful AI assistant.",
        'coding': "You are KIKI, a coding expert.",
        'creative': "You are KIKI, a creative writer.",
        'educational': "You are KIKI, a patient teacher.",
        'technical': "You are KIKI, a technical expert.",
        'fun': "You are KIKI, fun and energetic."
    }
    prompt = prompts.get(mode, prompts['standard'])
    try:
        result = subprocess.run(['tgpt', f"{prompt}\n\nUser: {question}\nKIKI:"],
                                capture_output=True, text=True, timeout=60)
        answer = result.stdout.strip() or f"Error: {result.stderr}"
        cursor.execute('INSERT INTO conversations (timestamp, question, answer, mode) VALUES (?, ?, ?, ?)',
                      (datetime.now(), question, answer, mode))
        conn.commit()
        return jsonify({'success': True, 'answer': answer})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/history', methods=['GET'])
def get_history():
    cursor.execute('SELECT id, timestamp, question, answer, mode FROM conversations ORDER BY timestamp DESC LIMIT 50')
    history = [{'id': row[0], 'timestamp': row[1], 'question': row[2], 'answer': row[3], 'mode': row[4]} for row in cursor.fetchall()]
    return jsonify(history)

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        cursor.execute('SELECT key, value FROM settings')
        return jsonify(dict(cursor.fetchall()))
    else:
        for key, value in request.json.items():
            cursor.execute('UPDATE settings SET value = ? WHERE key = ?', (value, key))
        conn.commit()
        return jsonify({'success': True})

@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    cursor.execute('DELETE FROM conversations')
    conn.commit()
    return jsonify({'success': True})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    cursor.execute('SELECT COUNT(*) FROM conversations')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT value FROM settings WHERE key = "current_mode"')
    mode = cursor.fetchone()
    return jsonify({'total': total, 'current_mode': mode[0] if mode else 'standard'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
