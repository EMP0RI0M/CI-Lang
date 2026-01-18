from fluxtorch.bridge import FluxTorchBridge
from fluxtorch.tensor import FluxTensor
from fluxtorch.optim import ChaosOptimizer
import os

def run_demo():
    # Path to the compiled bytecode
    bc_path = os.path.join(os.path.dirname(__file__), "chaos_learning.bc")
    
    # Target value we want the 'complex_process' to reach
    # (In the .ci file, result = 5 * 2 + 10 + noise = 20 + noise)
    # Let's try to optimize an external parameter (e.g., initial entropy)
    # For this demo, we'll just show the bridge loop converging.
    
    bridge = FluxTorchBridge(bc_path)
    
    # Optimize a 'weight' that simulates an atmospheric factor
    weight = FluxTensor(1.0, chaos=0.1)
    optimizer = ChaosOptimizer([weight], lr=0.05)
    
    print("--- FluxTorch Optimization Demo ---")
    bridge.train_step(optimizer, target_val=25.0, epochs=10)
    print("--- Optimization Finished ---")

if __name__ == "__main__":
    run_demo()
