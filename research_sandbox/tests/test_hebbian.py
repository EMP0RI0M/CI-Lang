import numpy as np
import matplotlib.pyplot as plt
from fluxvm.swarm import Swarm
from fluxvm.agent import Agent

def test_hebbian_emergence():
    # Setup: 2 correlated concepts
    n = 100
    agents = [Agent(i, initial_state=0.0) for i in range(n)]
    swarm = Swarm(agents, alpha=0.1, decay=0.99)
    
    print("Testing Hebbian Emergence: 2 agents stimulated together...")
    
    # Stimulate agents 10 and 20 together for 50 steps
    for _ in range(50):
        swarm.agents[10].state = 1.0
        swarm.agents[20].state = 1.0
        swarm.step(global_volatility=0.01)
        
    weight_10_20 = swarm.weights[10].get(20, 0.0)
    print(f"Weight (10 -> 20): {weight_10_20:.4f}")
    
    assert weight_10_20 > 0.5
    print("Hebbian Test PASSED.")

if __name__ == "__main__":
    test_hebbian_emergence()
