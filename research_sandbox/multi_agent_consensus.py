import numpy as np
import pickle
import sys
import os
import time
import json
import threading
import queue

# Add src to path
sys.path.append(os.path.abspath("src"))
from fluxvm_core import FluxVM

# Configuration
STEPS = 1000
SWARM_SIZE = 120

class AgentSwarm:
    def __init__(self, name, bias_entropy, color_code):
        self.name = name
        self.bias = bias_entropy
        self.color = color_code
        self.weights = np.random.randn(SWARM_SIZE, SWARM_SIZE) * 0.01
        self.states = np.zeros(SWARM_SIZE)
        self.prev_states = np.zeros(SWARM_SIZE)
        self.states[0:5] = 1.0 # Spark
        self.entropy_history = []
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
            # Calculate Entropy
            counts, _ = np.histogram(self.vm.states, bins=10, range=(-1, 1))
            probs = counts / np.sum(counts)
            probs = probs[probs > 0]
            ent = -np.sum(probs * np.log2(probs))
            self.entropy_history.append(ent)
            return ent
        return 0.0

def run_consensus_experiment():
    print(f"--- PROTOCOL: MULTI-AGENT CONSENSUS (TRIBE DYNAMICS) ---")
    
    bc_path = "research_sandbox/main.bc"
    if not os.path.exists(bc_path):
        print("Error: Bytecode not found.")
        return

    with open(bc_path, 'rb') as f:
        bytecode = pickle.load(f)

    # Initialize Tribes
    tribe_a = AgentSwarm("CONSERVATIVE", 0.2, "Blue") 
    tribe_a.setup_vm(bytecode)
    
    tribe_b = AgentSwarm("RADICAL", 0.8, "Red")
    tribe_b.setup_vm(bytecode)
    
    judge = AgentSwarm("JUDGE", 0.5, "Green")
    judge.setup_vm(bytecode)

    print(">>> [INIT] Spawning 3 Swarms: Conservative (A), Radical (B), Judge (C)")
    print(">>> [INIT] Beginning Interaction Loop...")
    
    judge_memory = 0.0
    conflict_start_tick = -1
    resolution_times = []
    
    for t in range(STEPS):
        ent_a = tribe_a.step()
        ent_b = tribe_b.step()

        # MANUAL PERTURBATION (Inject Conflict twice)
        if t == 200 or t == 600:
             print(f"\n>>> [GOD MODE] Injecting CHAOS at Tick {t}...")
             tribe_a.vm.states[0:10] = 5.0 # Milder injection
             tribe_b.vm.states[0:10] = -5.0 
             
        # Measure Divergence
        divergence = np.linalg.norm(tribe_a.vm.states - tribe_b.vm.states)
        
        # Judge Observes
        judge.vm.states[0] = divergence * 0.5 
        
        # Judge Observes
        judge.vm.states[0] = divergence * 0.5 
            
        ent_j = judge.step()
        
        # [GAVEL] Court Adjourned (Force Reset if peaceful)
        if divergence < 0.05:
            ent_j = 0.0
        
        # Interaction
        consensus_signal = 0.0
        status = "HARMONY"
        
        # Lower Threshold for faster reaction (0.4)
        if ent_j > 0.4: 
            # CONFLICT DETECTED
            status = "CONFLICT"
            if conflict_start_tick == -1:
                conflict_start_tick = t
            
            # Stronger Base Damping (-0.1) and Memory Effect
            damping_strength = -0.1 * (1.0 + (judge_memory * 2.0))
            consensus_signal = damping_strength 
            
            # Memory Accumulation
            judge_memory += 0.002 
        
        else:
            # RESOLVED
            if conflict_start_tick != -1:
                duration = t - conflict_start_tick
                resolution_times.append(duration)
                print(f">>> [JUDGE] Conflict Resolved in {duration} ticks. Memory updated to {judge_memory:.3f}")
                conflict_start_tick = -1
                
            consensus_signal = 0.01 # Allow Drift
            
        # Apply Signal
        tribe_a.vm.states *= (1.0 + consensus_signal)
        tribe_b.vm.states *= (1.0 + consensus_signal)
        
        if t % 50 == 0:
            print(f"Tick {t:03d} | Div: {divergence:.3f} | JudgeMem: {judge_memory:.3f} [{status}]")
            
    print("\n--- LEARNING RESULTS ---")
    if len(resolution_times) >= 2:
        t1 = resolution_times[0]
        t2 = resolution_times[-1] 
        
        print(f"Conflict 1 Duration: {t1}")
        print(f"Conflict Last Duration: {t2}")
        
        if t2 < t1:
            print(">>> SUCCESS: System learned to resolve conflict faster! (Learning Verified)")
        else:
            print(">>> NEUTRAL: No speedup detected.")
    else:
        print("Not enough conflict events to measure learning.")

    print("--- EXPERIMENT COMPLETE ---")

if __name__ == "__main__":
    run_consensus_experiment()
