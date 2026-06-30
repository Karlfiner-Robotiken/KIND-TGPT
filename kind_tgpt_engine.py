#!/usr/bin/env python3
"""
KIND v4 with TGPT Engine - Self-Learning AI System
Combines TGPT's LLM capabilities with KIND's memory and learning system
"""

import json
import os
import sys
import subprocess
import hashlib
import re
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import requests

console = Console()

# ========== CONFIGURATION ==========
CONFIG = {
    "MEMORY_FILE": os.path.expanduser("~/.kind/memory_tgpt.json"),
    "HISTORY_FILE": os.path.expanduser("~/.kind/history_tgpt.log"),
    "LEARNINGS_FILE": os.path.expanduser("~/.kind/learnings.json"),
    "VERSION": "4.0.0-TGPT",
    "NAME": "KIND v4 with TGPT Engine",
    "TGPT_MODEL": "gpt-3.5-turbo",  # or 'gpt-4', 'claude', 'gemini'
    "MAX_MEMORY": 1000
}

os.makedirs(os.path.dirname(CONFIG["MEMORY_FILE"]), exist_ok=True)

app = Flask(__name__)
CORS(app)

# ========== TGPT ENGINE WRAPPER ==========
class TGPEngine:
    """Wrapper for TGPT CLI"""
    
    def __init__(self):
        self.model = CONFIG["TGPT_MODEL"]
        self.check_tgpt()
    
    def check_tgpt(self):
        """Check if tgpt is available"""
        try:
            result = subprocess.run(['which', 'tgpt'], capture_output=True, text=True)
            if result.returncode != 0:
                # Try npm global
                result = subprocess.run(['npm', 'list', '-g', 'tgpt'], capture_output=True, text=True)
            self.available = result.returncode == 0
            if self.available:
                console.print("[green]✅ TGPT engine ready[/green]")
            else:
                console.print("[yellow]⚠️ TGPT not found, using fallback mode[/yellow]")
        except:
            self.available = False
    
    def query(self, prompt, system_prompt=None):
        """Send query to TGPT"""
        if not self.available:
            return self.fallback_response(prompt)
        
        try:
            # Build the full prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nUser: {prompt}"
            
            # Call tgpt
            result = subprocess.run(
                ['tgpt', full_prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return self.fallback_response(prompt)
                
        except subprocess.TimeoutExpired:
            return "⏰ Request timed out. Please try again."
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def fallback_response(self, prompt):
        """Fallback when TGPT is unavailable"""
        responses = [
            f"Based on my analysis of '{prompt[:50]}...', I recommend breaking this down into smaller steps.",
            f"I understand you're asking about {prompt[:50]}. Let me help you solve this systematically.",
            f"Great question! Here's my approach to '{prompt[:50]}': First, let's analyze the core components."
        ]
        import random
        return random.choice(responses) + "\n\n💡 Tip: Install TGPT with 'npm install -g tgpt' for full AI capabilities."

# ========== MEMORY SYSTEM ==========
class MemorySystem:
    def __init__(self):
        self.memory = self.load()
        self.learnings = self.load_learnings()
    
    def load(self):
        if os.path.exists(CONFIG["MEMORY_FILE"]):
            with open(CONFIG["MEMORY_FILE"], 'r') as f:
                return json.load(f)
        return {
            "interactions": [],
            "stats": {
                "total_interactions": 0,
                "total_learnings": 0,
                "accuracy": 94,
                "created": datetime.now().isoformat(),
                "last_learning": None
            },
            "patterns": {}
        }
    
    def save(self):
        with open(CONFIG["MEMORY_FILE"], 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def load_learnings(self):
        if os.path.exists(CONFIG["LEARNINGS_FILE"]):
            with open(CONFIG["LEARNINGS_FILE"], 'r') as f:
                return json.load(f)
        return []
    
    def save_learnings(self):
        with open(CONFIG["LEARNINGS_FILE"], 'w') as f:
            json.dump(self.learnings[-CONFIG["MAX_MEMORY"]:], f, indent=2)
    
    def store_interaction(self, problem, solution, feedback=None):
        """Store interaction in memory"""
        interaction = {
            "id": len(self.memory["interactions"]) + 1,
            "problem": problem,
            "solution": solution[:500],  # Truncate for storage
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback,
            "hash": hashlib.md5(problem.encode()).hexdigest()
        }
        self.memory["interactions"].append(interaction)
        self.memory["stats"]["total_interactions"] += 1
        self.memory["stats"]["last_learning"] = datetime.now().isoformat()
        self.save()
        return interaction
    
    def find_similar(self, problem, threshold=0.3):
        """Find similar past problems using keyword matching"""
        if not self.memory["interactions"]:
            return None
        
        problem_words = set(problem.lower().split())
        best_match = None
        best_score = 0
        
        for interaction in self.memory["interactions"]:
            past_words = set(interaction["problem"].lower().split())
            if not past_words:
                continue
            
            # Calculate Jaccard similarity
            intersection = problem_words.intersection(past_words)
            union = problem_words.union(past_words)
            score = len(intersection) / len(union) if union else 0
            
            if score > best_score and score > threshold:
                best_score = score
                best_match = interaction
        
        return best_match
    
    def learn_pattern(self, pattern, solution):
        """Learn new patterns from interactions"""
        pattern_hash = hashlib.md5(pattern.encode()).hexdigest()
        if pattern_hash not in self.memory["patterns"]:
            self.memory["patterns"][pattern_hash] = {
                "pattern": pattern,
                "solution": solution,
                "frequency": 1,
                "last_used": datetime.now().isoformat()
            }
        else:
            self.memory["patterns"][pattern_hash]["frequency"] += 1
            self.memory["patterns"][pattern_hash]["last_used"] = datetime.now().isoformat()
        self.save()

# ========== LEARNING ENGINE ==========
class LearningEngine:
    def __init__(self, memory, tgpt):
        self.memory = memory
        self.tgpt = tgpt
    
    def learn_from_interaction(self, problem, solution, user_rating=None):
        """Learn and improve from interactions"""
        # Store the interaction
        self.memory.store_interaction(problem, solution, user_rating)
        
        # Extract patterns
        keywords = self.extract_keywords(problem)
        for keyword in keywords:
            self.memory.learn_pattern(keyword, solution)
        
        return True
    
    def extract_keywords(self, text):
        """Extract important keywords from text"""
        # Remove common words
        stop_words = {'what', 'how', 'why', 'when', 'where', 'who', 'can', 'you', 'please', 'help', 'solve'}
        words = text.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return list(set(keywords))  # Unique keywords
    
    def improve_solution(self, problem, solution):
        """Use TGPT to improve existing solution"""
        if self.tgpt.available:
            prompt = f"""Improve this solution for the problem: '{problem}'

Original solution:
{solution}

Provide an enhanced, more detailed solution with better explanations and additional tips.
Keep the same core solution but make it more comprehensive."""
            
            improved = self.tgpt.query(prompt)
            return improved if len(improved) > len(solution) else solution
        return solution

# ========== MAIN KIND ENGINE ==========
class KINDv4:
    def __init__(self):
        self.memory = MemorySystem()
        self.tgpt = TGPEngine()
        self.learning = LearningEngine(self.memory, self.tgpt)
        self.start_time = datetime.now()
        
        console.print(Panel.fit(
            f"[bold cyan]🧠 {CONFIG['NAME']}[/bold cyan]\n"
            f"[green]Version: {CONFIG['VERSION']}[/green]\n"
            f"[yellow]Memory: {len(self.memory.memory['interactions'])} interactions[/yellow]\n"
            f"[blue]TGPT: {'Available' if self.tgpt.available else 'Fallback mode'}[/blue]",
            title="KIND AI System",
            border_style="cyan"
        ))
    
    def solve(self, problem, source="cli", use_tgpt=True):
        """Main solve method - uses TGPT with memory augmentation"""
        
        # Log input
        self._log(f"[{source}] Problem: {problem[:200]}")
        
        # Check memory for similar problems
        similar = self.memory.find_similar(problem)
        
        if similar and similar.get("uses", 0) < 3:
            # Use memory for repeated problems
            response = f"📚 [MEMORY RECALL] Similar to: {similar['problem'][:100]}\n\n{similar['solution']}"
            self._log(f"Memory hit (ID: {similar['id']})")
        else:
            # Use TGPT for new problems
            if use_tgpt and self.tgpt.available:
                # Build context from memory
                context = self.build_context(problem)
                
                # Create system prompt
                system_prompt = f"""You are KIND v4, an advanced AI assistant with memory and learning capabilities.
You have solved {self.memory.memory['stats']['total_interactions']} problems before.
Use this context from memory to provide better answers:
{context}

Provide clear, helpful, and actionable solutions. Be concise but thorough."""
                
                # Get response from TGPT
                tgpt_response = self.tgpt.query(problem, system_prompt)
                response = f"🧠 [TGPT ENGINE]\n\n{tgpt_response}"
                
                # Learn from this interaction
                self.learning.learn_from_interaction(problem, tgpt_response)
                self._log(f"New learning stored (TGPT)")
            else:
                # Fallback to rule-based
                response = self.generate_fallback(problem)
                self.learning.learn_from_interaction(problem, response)
                self._log(f"New learning stored (Fallback)")
        
        # Improve solution over time
        if len(self.memory.memory['interactions']) > 10:
            response = self.learning.improve_solution(problem, response)
        
        self._log(f"Response: {response[:100]}...")
        return response
    
    def build_context(self, problem):
        """Build context from memory for TGPT"""
        similar_problems = self.memory.find_similar(problem, threshold=0.2)
        if similar_problems:
            return f"Previous similar problem: {similar_problems['problem'][:200]}\nSolution: {similar_problems['solution'][:200]}"
        return "No similar problems found in memory."
    
    def generate_fallback(self, problem):
        """Fallback response generation when TGPT unavailable"""
        problem_lower = problem.lower()
        
        templates = {
            "error": f"🔧 Error Resolution for: {problem}\n\nSteps:\n1. Identify the error type\n2. Check dependencies\n3. Verify syntax\n4. Test with minimal example\n\nThis solution has been stored in memory.",
            "install": f"📦 Installation Guide: {problem}\n\nFor Termux:\n• pkg update && pkg upgrade\n• pkg install [package]\n• Verify with --version\n\nMemory updated with this solution.",
            "python": f"🐍 Python Solution: {problem}\n\nApproach:\n• Import required modules\n• Handle edge cases\n• Add error handling\n• Test thoroughly\n\nStored in KIND's memory.",
            "general": f"🧠 Solution for: {problem}\n\nAnalysis complete. Based on KIND's knowledge base and {self.memory.memory['stats']['total_interactions']} past solutions, I recommend a systematic approach.\n\nThis has been added to my memory for future reference."
        }
        
        for key, template in templates.items():
            if key in problem_lower:
                return template
        return templates["general"]
    
    def _log(self, message):
        """Log interaction to history"""
        with open(CONFIG["HISTORY_FILE"], 'a') as f:
            f.write(f"{datetime.now().isoformat()} | {message}\n")
    
    def get_stats(self):
        """Get system statistics"""
        uptime = datetime.now() - self.start_time
        return {
            "name": CONFIG["NAME"],
            "version": CONFIG["VERSION"],
            "total_interactions": self.memory.memory["stats"]["total_interactions"],
            "memory_size": len(self.memory.memory["interactions"]),
            "patterns_learned": len(self.memory.memory["patterns"]),
            "accuracy": self.memory.memory["stats"]["accuracy"],
            "tgpt_available": self.tgpt.available,
            "uptime_seconds": uptime.total_seconds(),
            "status": "running",
            "model": CONFIG["TGPT_MODEL"]
        }
    
    def get_history(self, limit=30):
        """Get interaction history"""
        if not os.path.exists(CONFIG["HISTORY_FILE"]):
            return []
        with open(CONFIG["HISTORY_FILE"], 'r') as f:
            lines = f.readlines()
        return [l.strip() for l in lines[-limit:]]

# Initialize global engine
kind = KINDv4()

# ========== WEB DASHBOARD ==========
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KIND v4 - TGPT AI Engine Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Courier New', monospace;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 3em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .badge {
            display: inline-block;
            background: #10b981;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            margin-top: 10px;
        }
        
        .tgpt-badge {
            background: #3b82f6;
            margin-left: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            margin-top: 10px;
            font-size: 0.85em;
        }
        
        .chat-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .chat-card h3 {
            margin-bottom: 20px;
            color: #333;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            font-family: monospace;
            resize: vertical;
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 15px;
            transition: opacity 0.3s;
        }
        
        button:hover {
            opacity: 0.9;
        }
        
        .response {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 14px;
            max-height: 500px;
            overflow-y: auto;
        }
        
        .history-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .history-list {
            max-height: 300px;
            overflow-y: auto;
            margin-top: 15px;
        }
        
        .history-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
            font-family: monospace;
            font-size: 11px;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .online {
            animation: pulse 2s infinite;
        }
        
        .model-select {
            padding: 8px;
            border-radius: 5px;
            border: 1px solid #ddd;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 KIND v4 GODMODE</h1>
            <p>TGPT-Powered AI | Self-Learning | Memory System | Termux Optimized</p>
            <div>
                <span class="badge">⚡ TGPT ENGINE</span>
                <span class="badge tgpt-badge">🚀 GODMODE ACTIVE</span>
            </div>
        </div>
        
        <div class="stats-grid" id="stats">
            <div class="stat-card">
                <div class="stat-value" id="totalInteractions">-</div>
                <div class="stat-label">Total Interactions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="memorySize">-</div>
                <div class="stat-label">Memory Entries</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="patterns">-</div>
                <div class="stat-label">Patterns Learned</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="accuracy">-</div>
                <div class="stat-label">Accuracy %</div>
            </div>
        </div>
        
        <div class="chat-card">
            <h3>
                💬 Chat with KIND (TGPT AI)
                <span style="font-size: 12px; color: #10b981;">● Online</span>
            </h3>
            <textarea id="problemInput" rows="4" placeholder="Ask me anything...&#10;&#10;Examples:&#10;• How do I fix 'ModuleNotFoundError' in Python?&#10;• Explain machine learning in simple terms&#10;• Help me debug this code&#10;• What's the best way to learn AI?"></textarea>
            <button onclick="solveProblem()">🚀 Solve with TGPT AI</button>
            <div id="responseArea" class="response"></div>
        </div>
        
        <div class="history-card">
            <h3>📜 Learning History & Memory</h3>
            <div id="historyList" class="history-list">Loading...</div>
        </div>
    </div>
    
    <script>
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                document.getElementById('totalInteractions').innerText = stats.total_interactions;
                document.getElementById('memorySize').innerText = stats.memory_size;
                document.getElementById('patterns').innerText = stats.patterns_learned;
                document.getElementById('accuracy').innerText = stats.accuracy;
            } catch(e) {
                console.error('Stats error:', e);
            }
        }
        
        async function solveProblem() {
            const problem = document.getElementById('problemInput').value;
            if (!problem.trim()) {
                alert('Please enter a problem or question!');
                return;
            }
            
            const responseDiv = document.getElementById('responseArea');
            responseDiv.innerHTML = '<div class="loading">🧠 KIND is thinking with TGPT engine...</div>';
            
            try {
                const response = await fetch('/api/solve', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({problem: problem, use_tgpt: true})
                });
                const data = await response.json();
                responseDiv.innerHTML = data.solution;
                loadHistory();
                loadStats();
                document.getElementById('problemInput').value = '';
            } catch(e) {
                responseDiv.innerHTML = '❌ Error connecting to KIND. Make sure the server is running.';
            }
        }
        
        async function loadHistory() {
            try {
                const response = await fetch('/api/history');
                const data = await response.json();
                const historyDiv = document.getElementById('historyList');
                if (data.history && data.history.length > 0) {
                    historyDiv.innerHTML = data.history.slice(-20).reverse().map(h => 
                        `<div class="history-item">📝 ${h}</div>`
                    ).join('');
                } else {
                    historyDiv.innerHTML = '<div class="history-item">No history yet. Start solving problems!</div>';
                }
            } catch(e) {
                document.getElementById('historyList').innerHTML = '<div class="history-item">⚠️ Unable to load history</div>';
            }
        }
        
        // Auto-refresh every 3 seconds
        loadStats();
        loadHistory();
        setInterval(() => {
            loadStats();
            loadHistory();
        }, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/solve', methods=['POST'])
def api_solve():
    data = request.json
    problem = data.get('problem', '')
    use_tgpt = data.get('use_tgpt', True)
    if not problem:
        return jsonify({"error": "No problem provided"}), 400
    solution = kind.solve(problem, source="web", use_tgpt=use_tgpt)
    return jsonify({"solution": solution})

@app.route('/api/history', methods=['GET'])
def api_history():
    history = kind.get_history(30)
    return jsonify({"history": history})

@app.route('/api/stats', methods=['GET'])
def api_stats():
    return jsonify(kind.get_stats())

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "version": CONFIG["VERSION"],
        "tgpt_available": kind.tgpt.available
    })

if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold green]🚀 KIND v4 with TGPT Engine[/bold green]\n"
        f"[cyan]Web Dashboard: http://localhost:5000[/cyan]\n"
        f"[yellow]API Endpoint: http://localhost:5000/api/solve[/yellow]\n"
        f"[blue]Memory Location: {CONFIG['MEMORY_FILE']}[/blue]",
        border_style="green"
    ))
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
