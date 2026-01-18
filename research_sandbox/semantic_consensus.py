import numpy as np
import pickle
import sys
import os
import time
import json
import threading
import queue
import requests

# Add src to path
sys.path.append(os.path.abspath("src"))
from fluxvm_core import FluxVM

# Configuration
STEPS = 500
SWARM_SIZE = 120
API_KEY = "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"
MODEL = "xiaomi/mimo-v2-flash:free"

class AgentSwarm:
    def __init__(self, name, bias_entropy, color_code):
        self.name = name
        self.bias = bias_entropy
        self.color = color_code
        self.weights = np.random.randn(SWARM_SIZE, SWARM_SIZE) * 0.01
        self.states = np.zeros(SWARM_SIZE)
        self.prev_states = np.zeros(SWARM_SIZE)
        self.states[0:5] = 1.0 # Spark
        self.vm = None

    def setup_vm(self, bytecode):
        self.vm = FluxVM(
            weights=self.weights, 
            states=self.states, 
            prev_states=self.prev_states, 
            print_callback=self.log_callback
        )
        self.vm.load_bytecode(bytecode)
        self.vm.mailbox = self.bias 

    def log_callback(self, msg):
        pass

    def step(self):
        if self.vm:
            self.vm.step()
            counts, _ = np.histogram(self.vm.states, bins=10, range=(-1, 1))
            probs = counts / np.sum(counts)
            probs = probs[probs > 0]
            ent = -np.sum(probs * np.log2(probs))
            return ent
        return 0.0

def ask_mimo_resolution(divergence, memory):
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
                    {"role": "system", "content": "You are a Conflict Resolution Algorithm (The Judge). Input: Divergence Score (0-100) and History (Memory). Task: Decide to 'DAMPEN' (force stability) or 'ALLOW' (let them explore). Higher divergence usually requires damping. Return JSON: {'action': 'DAMPEN'|'ALLOW', 'reason': 'short phrase'}."},
                    {"role": "user", "content": f"Divergence: {divergence:.2f}. Memory Level: {memory:.2f}."}
                ]
            }),
            timeout=5
        )
        
        result = response.json()
        if 'choices' in result:
            content = result['choices'][0]['message']['content'].strip()
            # Clean json
            content = content.replace("```json", "").replace("```", "")
            data = json.loads(content)
            return data.get("action", "DAMPEN"), data.get("reason", "Unknown")
            
    except Exception as e:
        print(f"LLM Error: {e}")
    return "DAMPEN", "Fallback"

def run_semantic_council():
    print(f"--- PROTOCOL: SEMANTIC CONSENSUS (LLM GOVERNANCE) ---")
    
    bc_path = "research_sandbox/main.bc"
    if not os.path.exists(bc_path):
        print("Error: Bytecode not found.")
        return

    with open(bc_path, 'rb') as f:
        bytecode = pickle.load(f)

    tribe_a = AgentSwarm("CONSERVATIVE", 0.2, "Blue") 
    tribe_a.setup_vm(bytecode)
    
    tribe_b = AgentSwarm("RADICAL", 0.8, "Red")
    tribe_b.setup_vm(bytecode)
    
    judge = AgentSwarm("JUDGE", 0.5, "Green")
    judge.setup_vm(bytecode)

    print(">>> [INIT] Council Assembled. Waiting for conflict...")
    
    judge_memory = 0.0
    conflict_active = False
    
    for t in range(STEPS):
        ent_a = tribe_a.step()
        ent_b = tribe_b.step()

        # MANUAL PERTURBATION
        if t == 150:
             print(f"\n>>> [EVENT] Political Schism Injected at Tick {t}...")
             tribe_a.vm.states[0:10] = 5.0 
             tribe_b.vm.states[0:10] = -5.0 
             
        divergence = np.linalg.norm(tribe_a.vm.states - tribe_b.vm.states)
        
        judge.vm.states[0] = divergence * 0.5 
        ent_j = judge.step()
        
        consensus_signal = 0.0
        status = "HARMONY"
        
        # Judge Observation
        if ent_j > 0.4: 
            status = "CONFLICT"
            if not conflict_active:
                print(f"\n>>> [JUDGE] Conflict Detected (Div: {divergence:.2f}). Consulting Mimo...")
                conflict_active = True
                
                # CALL LLM
                action, reason = ask_mimo_resolution(divergence, judge_memory)
                print(f">>> [MIMO VERDICT] Action: {action} | Reason: {reason}")
                
                if action == "DAMPEN":
                    # Strong damping based on memory
                    consensus_signal = -0.1 * (1.0 + judge_memory)
                    judge_memory += 0.5 # Fast learn
                else:
                    consensus_signal = 0.05 # Encourage chaos
            else:
                 # Maintain previous decision's decay
                 consensus_signal = -0.05 # Default continuous damping during conflict
        else:
            if conflict_active:
                print(f">>> [JUDGE] Peace Restored. Memory: {judge_memory:.2f}")
                conflict_active = False
                
            # Post-Conflict Cooling
            if divergence < 0.05:
                judge.vm.states *= 0.5 
                
            consensus_signal = 0.01 
            
        # Apply Signal
        tribe_a.vm.states *= (1.0 + consensus_signal)
        tribe_b.vm.states *= (1.0 + consensus_signal)
        
        if t % 50 == 0:
            print(f"Tick {t:03d} | Div: {divergence:.3f} | JudgeMem: {judge_memory:.3f} [{status}]")

    print("--- COUNCIL ADJOURNED ---")

if __name__ == "__main__":
    run_semantic_council()
