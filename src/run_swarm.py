from swarms.engine import SwarmManager
from swarms.monitor import StabilityMonitor
import pickle
import os

def run_swarm_test():
    # Load compiled bytecode
    bc_path = os.path.join(os.path.dirname(__file__), "..", "stability_test.bc")
    with open(bc_path, 'rb') as f:
        bytecode = pickle.load(f)
    
    # 1. Initialize Swarm with 1,000 agents
    manager = SwarmManager(bytecode, agent_count=1000)
    monitor = StabilityMonitor()
    
    # 2. Run simulation for 100 ticks
    print("--- CI-Lang Swarm Stability Test ---")
    manager.run_simulation(ticks=100, monitor=monitor)
    
    # 3. Verify and Report
    monitor.report()

if __name__ == "__main__":
    run_swarm_test()
