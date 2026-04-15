import os
import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from swarms.engine import SwarmManager
from swarms.monitor import StabilityMonitor

def generate_impact_graph():
    bc_path = "tests/stress/industrial_10M.bc"
    if not os.path.exists(bc_path):
        print("Compile tests/stress/industrial_10M.ci first.")
        return

    with open(bc_path, 'rb') as f:
        bytecode = pickle.load(f)

    # Launch Swarm
    manager = SwarmManager(bytecode, agent_count=1000, seed=42)
    entropy_history = []
    memory_history = []
    
    print("Running Simulation for Graph Generation...")
    for t in range(500):
        manager.step()
        entropy_history.append(manager.global_entropy)
        memory_history.append(manager.memory)
    
    # Plotting
    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = 'tab:red'
    ax1.set_xlabel('Time (Ticks)')
    ax1.set_ylabel('System Entropy (\u03bb)', color=color)
    ax1.plot(entropy_history, color=color, linewidth=2, label='Entropy \u03bb')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Control Memory (M)', color=color)
    ax2.plot(memory_history, color=color, linewidth=2, linestyle='--', label='Memory M')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('Homeostatic Regulation: Entropy Reduction vs Control Memory')
    fig.tight_layout()
    
    output_path = "docs/entropy_convergence.png"
    plt.savefig(output_path)
    print(f"Graph Saved to {output_path}")

if __name__ == "__main__":
    generate_impact_graph()
