import sys
import os
import time
import numpy as np
import pickle
import matplotlib.pyplot as plt
from swarms.engine import SwarmManager

# Ensure CI-Lang modules are importable
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

def run_experiment(use_memory=True):
    with open("consensus.bc", "rb") as f:
        bytecode = pickle.load(f)

    # Initialize Manager
    manager = SwarmManager(bytecode, agent_count=50)
    
    # Disable memory if needed for baseline
    if not use_memory:
        manager.k = 0.0 # Control sensitivity = 0 (No feedback from memory to lambda)
        manager.gamma = 0.0 # No memory retention

    history = []
    ticks = 500
    
    for t in range(ticks):
        # Inject Pulse at Tick 100
        if t == 100:
            for agent in manager.agents:
                agent.mailbox = 150.0 # Chaos Pulse
        
        # Step: Perform multiple VM steps to complete the CI-Lang loop
        outputs = []
        for _ in range(25):
            outputs = manager.step()
        
        # Clear mailbox after one tick of injection
        if t == 101:
            for agent in manager.agents:
                agent.mailbox = 0.0

        # Data collection
        numeric_outputs = [o for o in outputs if isinstance(o, (int, float))]
        if numeric_outputs:
            mean = np.mean(numeric_outputs)
            history.append(mean)
        else:
            history.append(50.0) # Default

    return history

def plot_comparison(baseline, macs):
    plt.figure(figsize=(12, 6))
    
    # Plot data
    plt.plot(baseline, label="Baseline (Naive Consensus)", color='gray', linestyle='--')
    plt.plot(macs, label="MACS (Memory-Augmented)", color='#2ecc71', linewidth=2)
    
    # Annotations
    plt.axvline(x=30, color='red', alpha=0.3, label="Chaos Pulse (Injection)")
    plt.axhline(y=50, color='blue', alpha=0.1, linestyle='-')
    
    plt.title("MACS vs Naive Consensus: Recovery Curve Under Chaos")
    plt.xlabel("Time (Ticks)")
    plt.ylabel("Consensus Mean")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save the result
    plt.savefig("consensus_comparison.png")
    print("\n[SUCCESS] Comparison Plot saved as 'consensus_comparison.png'")

if __name__ == "__main__":
    print("[1/3] Compiling MACS logic...")
    os.system("python src/cic.py consensus.ci -o consensus.bc")
    
    print("[2/3] Running Experiments...")
    print("      Running Baseline (No Memory)...")
    baseline_history = run_experiment(use_memory=False)
    
    print("      Running MACS (Adaptive Damping)...")
    macs_history = run_experiment(use_memory=True)
    
    print("[3/3] Generating Proof (Plotting)...")
    try:
        plot_comparison(baseline_history, macs_history)
        print("\n--- Summary ---")
        # Calc recovery (ticks to get back within 5% of 50.0)
        def get_recovery_time(hist):
            pulse_tick = 100
            for i, val in enumerate(hist[pulse_tick:]):
                if abs(val - 50.0) < 2.5: # 5% threshold
                    return i
            return len(hist) - pulse_tick

        r_base = get_recovery_time(baseline_history)
        r_macs = get_recovery_time(macs_history)
        
        print(f"Baseline Recovery Time: {r_base} ticks")
        print(f"MACS Recovery Time:     {r_macs} ticks")
        print(f"Improvement:           {((r_base - r_macs) / r_base * 100):.1f}% faster convergence.")
        
    except Exception as e:
        print(f"[PLOT ERROR]: {e}")
        print("Data Summary (First 5 ticks after pulse):")
        print(f"Baseline: {baseline_history[30:35]}")
        print(f"MACS:     {macs_history[30:35]}")
