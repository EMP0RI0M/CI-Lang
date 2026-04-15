import os
import sys
import time
import pickle
import numpy as np

# Try to import psutil for memory tracking
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from swarms.engine import SwarmManager
from swarms.monitor import StabilityMonitor

def memory_usage():
    if HAS_PSUTIL:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024 # MB
    return 0

def run_industrial_stress(bc_path, agents=1000, steps=1000):
    print(f"--- STARTING INDUSTRIAL STRESS TEST ---")
    print(f"Target: {agents} Agents | {steps} Steps | ~1,000,000 Ops")
    
    with open(bc_path, 'rb') as f:
        bytecode = pickle.load(f)
        
    start_mem = memory_usage()
    manager = SwarmManager(bytecode, agent_count=agents)
    monitor = StabilityMonitor()
    
    start_time = time.time()
    
    for t in range(steps):
        manager.step()
        
        if t % 1000 == 0:
            cur_mem = memory_usage()
            # Calculate current mean from all agents
            all_vals = []
            for a in manager.agents:
                if 'val' in a.variables:
                    all_vals.append(a.variables['val'].value)
            
            mean_val = np.mean(all_vals) if all_vals else 0
            print(f"Step {t:5d} | RAM: {cur_mem:6.2f}MB | Swarm Mean: {mean_val:6.2f} | Entropy: {manager.global_entropy:.4f}")
            
            # Leak detection (rough)
            if t > 0 and cur_mem > start_mem + 50:
                 print("WARNING: COMPONENT MEMORY GROWTH DETECTED")

    end_time = time.time()
    end_mem = memory_usage()
    
    print("\n--- STRESS TEST COMPLETE ---")
    print(f"Total Runtime: {end_time - start_time:.2f}s")
    print(f"Throughput: {int((agents * steps) / (end_time - start_time))} ops/sec")
    print(f"Memory Delta: {end_mem - start_mem:.2f} MB")
    
    # Final Verification
    final_vals = [a.variables['val'].value for a in manager.agents if 'val' in a.variables]
    final_mean = np.mean(final_vals)
    if 99.0 <= final_mean <= 101.0:
        print("STABILITY SUCCESS: Swarm converged to target 100.0")
    else:
        print(f"STABILITY FAILURE: Swarm converged to {final_mean}")

if __name__ == "__main__":
    bc = "tests/stress/industrial_10M.bc"
    if os.path.exists(bc):
        run_industrial_stress(bc, agents=10000, steps=10000)
    else:
        print(f"Error: {bc} not found. Compile it first.")
