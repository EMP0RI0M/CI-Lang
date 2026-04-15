import sys
import os
import time
import numpy as np
import pickle
from swarms.engine import SwarmManager
from swarms.monitor import StabilityMonitor

# Ensure CI-Lang modules are importable
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

def run_consensus_engine():
    # 1. Compile consensus.ci
    print("[INIT] Compiling consensus.ci...")
    # Using the system's cic compiler logic (mocked here for brevity, assuming already compiled or using external call)
    os.system("python src/cic.py consensus.ci -o consensus.bc")
    
    with open("consensus.bc", "rb") as f:
        bytecode = pickle.load(f)

    # 2. Setup Swarm and Monitor
    # We use a memory-augmented SwarmManager (already implemented)
    manager = SwarmManager(bytecode, agent_count=50)
    monitor = StabilityMonitor()
    
    print("\n" + "="*50)
    print("  CI-LANG CONSENSUS ENGINE: RE-STABILIZATION TEST")
    print("="*50)

    ticks = 100
    for t in range(ticks):
        # [INJECTION] At Tick 40, we simulate a 'Hallucination' or 'Chaos Pulse'
        # We push all agents to a random divergent value
        if t == 40:
            print(f"\n[ALERT] Tick {t}: Injecting Chaos Pulse (Hallucination Simulation)!")
            for agent in manager.agents:
                agent.mailbox = 150.0  # Force agents away from consensus (50.0)
        
        # [STEP] Execute swarm iteration
        outputs = manager.step()
        
        # Clear mailboxes after processing to allow natural stabilizing pull
        if t == 41:
            for agent in manager.agents:
                agent.mailbox = 0.0

        # [LOG] Update monitor
        monitor.log_step(t, manager.global_entropy, outputs, memory=manager.memory)

        if t % 5 == 0:
            avg = np.mean([o for o in outputs if isinstance(o, (int, float))])
            print(f"Tick {t:02d} | Entropy: {manager.global_entropy:.3f} | Memory: {manager.memory:.3f} | Swarm Mean: {avg:.2f}")

    # 3. Final Report
    print("\n" + "="*50)
    monitor.report()
    print("="*50 + "\n")

if __name__ == "__main__":
    run_consensus_engine()
