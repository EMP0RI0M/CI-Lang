import json
import os
import sys
import numpy as np
import pickle
from swarms.engine import SwarmManager

# Load the real data
DATA_PATH = "research_sandbox/results/run_1768638124.json"

def run_real_data_test():
    with open(DATA_PATH, 'r') as f:
        data = json.load(f)
    
    historical_entropy = data['history']['entropy']
    print(f"[DATA] Loaded {len(historical_entropy)} real-world entropy data points.")

    # Load MACS bytecode
    with open("consensus.bc", "rb") as f:
        bytecode = pickle.load(f)

    # Initialize MACS Swarm
    manager = SwarmManager(bytecode, agent_count=50)
    target = 1.5 # We want to see if we can pull the historical 2.1 chaos down to 1.5
    
    macs_output = []
    
    print("\n" + "="*50)
    print("  CI-LANG REAL-DATA TESTING: HISTORICAL STABILIZATION")
    print("="*50)

    # We iterate through the historical data points
    for t, h_entropy in enumerate(historical_entropy):
        # Inject the historical 'chaos' into the mailbox
        for agent in manager.agents:
            agent.mailbox = h_entropy
            
        # Let MACS work for a few steps
        outputs = []
        for _ in range(10):
            outputs = manager.step()
            
        # Measure what MACS achieved
        numeric_outputs = [o for o in outputs if isinstance(o, (int, float))]
        if numeric_outputs:
            macs_output.append(np.mean(numeric_outputs))
        
        if t % 20 == 0:
            print(f"Tick {t:03d} | Historical E: {h_entropy:.3f} | MACS Corrected: {macs_output[-1]:.3f} | Memory: {manager.memory:.3f}")

    # Final Comparison
    print("\n" + "="*50)
    print(f"Historical Mean Entropy: {np.mean(historical_entropy):.3f}")
    print(f"MACS-Stabilized Mean:    {np.mean(macs_output):.3f}")
    improvement = (np.mean(historical_entropy) - np.mean(macs_output)) / np.mean(historical_entropy) * 100
    print(f"Entropy Reduction:       {improvement:.1f}%")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_real_data_test()
