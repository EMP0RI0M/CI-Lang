import numpy as np
import pickle
import sys
import os
import time
import requests
import json
from flask import Flask, Response, render_template_string
import threading
import queue

app = Flask(__name__)
log_queue = queue.Queue()

# Thread-safe logging
def safe_print(msg):
    log_queue.put(msg)
    print(msg)

# Load .env manually for simplicity
API_KEY = "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"
MODEL = "xiaomi/mimo-v2-flash:free"
SEARXNG_URL = "http://34.16.85.155:8080/search"

# Add src to path
sys.path.append(os.path.abspath("src"))
from fluxvm_core import FluxVM

def search_web(query):
    try:
        params = {"q": query, "format": "json"}
        resp = requests.get(SEARXNG_URL, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])[:3] # Get top 3
            snippets = [r.get("content", "") for r in results]
            return " ".join(snippets)
    except Exception as e:
        safe_print(f"Search Error: {e}")
    return None

# Global state for dashboard
active_vm = None
current_concept = "UNKNOWN"
current_target = 0.45

def run_meta_orchestrator():
    global active_vm, current_target
    safe_print("--- CI-Lang Meta-Evolution Engine (Phase 28: Internet-Augmented Cognition) ---")
    
    # 1. Initialize Large Swarm (100 Primary + 20 Meta neurons)
    n = 120
    weights = np.random.randn(n, n) * 0.01
    states = np.zeros(n)
    prev_states = np.zeros(n)
    
    # 2. Stimulate some agents
    states[0:5] = 1.0
    
    # 3. Load Meta-Bytecode
    bc_path = "research_sandbox/main.bc"
    if not os.path.exists(bc_path):
        safe_print(f"Error: {bc_path} not found. Compile main.ci first.")
        return

    with open(bc_path, 'rb') as f:
        bytecode = pickle.load(f)

    # 4. Instantiate VM with a 'Teacher' callback
    def teacher_callback(msg):
        global current_concept, current_target
        
        # Mirror to web queue
        log_queue.put(f"[FluxVM]: {msg}")
        print(f"[FluxVM Output]: {msg}")
        
        if "CI_CORE_STATE" in str(msg):
            log_queue.put(f"DATA: {msg}")
            
        if "Meta-Abstraction acquired conceptually as:" in str(msg):
             try:
                 current_concept = str(msg).split("as:")[1].strip()
             except: pass
        
        if "New Target Entropy:" in str(msg):
             try:
                current_target = float(str(msg).split(": ")[1].strip())
             except: pass

        # Knowledge Retrieval Mode (Augmented)
        if "REQUEST_KNOWLEDGE:" in str(msg):
            query = str(msg).split("REQUEST_KNOWLEDGE:")[1].strip()
            safe_print(f"\n>>> [HOST] Swarm Requesting Knowledge: '{query}'")
            safe_print(f">>> [HOST] Searching Live Web (SearXNG)...")
            
            # 1. Search Web
            context = search_web(query)
            if context:
                safe_print(f">>> [HOST] Retrieved Context: {context[:100]}...")
            else:
                context = "No external data found."
            
            safe_print(f">>> [HOST] Synthesizing Answer with Teacher Mimo...")
            
            try:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json",
                    },
                    data=json.dumps({
                        "model": MODEL,
                        "messages": [
                            {"role": "system", "content": "You are a Master Teacher. Output JSON ONLY. Fields: 'explanation' (max 30 words, dense, physics/neuro based), 'novelty_score' (float 0.1-1.0, how complex/new is this?)."},
                            {"role": "user", "content": f"Query: {query}\nSearch Context: {context}"}
                        ]
                    })
                )
                
                result = response.json()
                if 'choices' in result:
                    content = result['choices'][0]['message']['content'].strip()
                    # Clean potential markdown code blocks
                    content = content.replace("```json", "").replace("```", "")
                    
                    try:
                        data = json.loads(content)
                        knowledge = data.get("explanation", "No explanation")
                        score = float(data.get("novelty_score", 0.5))
                        
                        safe_print(f">>> [TEACHER MIMO] Explanation: {knowledge}")
                        safe_print(f">>> [TEACHER MIMO] Novelty Score: {score}")
                        
                        # Encode score into mailbox for the VM (Mapping 0.0-1.0 -> 2.0-3.0)
                        # Range 2.0 - 3.0 reserved for "Learning Modulation"
                        vm.mailbox = 2.0 + score 
                        
                    except json.JSONDecodeError:
                         safe_print(f">>> [HOST] JSON Parse Error: {content}")
                else:
                    safe_print(f">>> [HOST] OpenRouter Error: {json.dumps(result)}")

            except Exception as e:
                safe_print(f">>> [HOST] LLM Connectivity Error: {e}")

        # Standard Control Mode
        elif "LLM_TEACHER_PROMPT" in str(msg):
            safe_print("\n>>> [HOST] Intercepting Teacher Prompt...")
            safe_print(f">>> [HOST] Querying Teacher Mimo...")
            
            try:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json",
                    },
                    data=json.dumps({
                        "model": MODEL,
                        "messages": [
                            {"role": "system", "content": "You are the LLM Teacher for a Chaos Intelligence Swarm. Target Entropy: 0.45. If E is high, suggest low volatility. If E is low, suggest high volatility. Respond ONLY with a single float between 0.01 and 0.9."},
                            {"role": "user", "content": str(msg)}
                        ]
                    })
                )
                
                result = response.json()
                if 'choices' in result:
                    advice_str = result['choices'][0]['message']['content'].strip()
                    # Extract float
                    import re
                    match = re.search(r"[-+]?\d*\.\d+|\d+", advice_str)
                    if match:
                        advice = float(match.group())
                        safe_print(f">>> [HOST] Mimo Advice: Set Volatility to {advice}")
                        vm.mailbox = advice
                    else:
                        safe_print(f">>> [HOST] Error parsing LLM advice: {advice_str}")
                else:
                    safe_print(f">>> [HOST] OpenRouter Error: {json.dumps(result)}")

            except Exception as e:
                safe_print(f">>> [HOST] LLM Connectivity Error: {e}")

    vm = FluxVM(weights=weights, states=states, prev_states=prev_states, print_callback=teacher_callback)
    vm.load_bytecode(bytecode)
    active_vm = vm
    
    safe_print(">>> [HOST] Starting FluxVM Meta-Core...")
    vm.run()


@app.route('/')
def index():
    try:
        with open("research_sandbox/dashboard.html", "r") as f:
            return f.read()
    except:
        return "Dashboard HTML not found."

@app.route('/stream')
def stream():
    def generate():
        while True:
            try:
                msg = log_queue.get(timeout=1.0)
                yield f"data: {msg}\n\n"
            except queue.Empty:
                yield ": keepalive\n\n"
    return Response(generate(), mimetype='text/event-stream')

@app.route('/matrix_data')
def matrix_data():
    if active_vm:
        return json.dumps(active_vm.weights.tolist())
    return "[]"

@app.route('/swag_stats')
def swag_stats():
    return json.dumps({
        "concept": current_concept,
        "target": current_target
    })

if __name__ == "__main__":
    # Start VM in background
    sim_thread = threading.Thread(target=run_meta_orchestrator, daemon=True)
    sim_thread.start()
    
    # Start Web Server
    app.run(host='0.0.0.0', port=5000)
