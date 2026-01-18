import numpy as np
from fluxvm.agent import Agent
from fluxvm.swarm import Swarm
import time

def test_bootstrapping():
    print("--- CI-Lang Bootstrapping Verification ---")
    
    # 1. Initialize Swarm (100 agents)
    agents = [Agent(i) for i in range(100)]
    swarm = Swarm(agents, alpha=0.5, decay=0.9, ci_mode=True)
    
    # 2. Stimulate Agent 0 and then Agent 1
    # This should create an asymmetric link 0 -> 1
    print("Step 1: Stimulating Agent 0...")
    agents[0].state = 1.0
    swarm.step(global_volatility=0.0) # No noise
    
    print("Step 2: Stimulating Agent 1...")
    agents[1].state = 1.0
    swarm.step(global_volatility=0.0)
    
    # 3. Check Weight W[0, 1]
    weight = swarm.weights[0, 1]
    print(f"Weight W[0, 1] after association: {weight:.4f}")
    
    if weight > 0:
        print("SUCCESS: CI-Lang Meta-Core updated the weights!")
    else:
        print("FAILURE: Weights remained zero. Meta-Core logic didn't fire.")

if __name__ == "__main__":
    test_bootstrapping()
