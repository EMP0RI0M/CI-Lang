import os
import sys
import pickle
import hashlib

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from swarms.engine import SwarmManager

def run_simulation_and_get_hash(bytecode, seed, steps=100):
    manager = SwarmManager(bytecode, seed=seed)
    full_trace = []
    
    for _ in range(steps):
        outputs = manager.step()
        full_trace.append(tuple(outputs))
    
    # Hash the resulting trace
    trace_bytes = pickle.dumps(full_trace)
    return hashlib.sha256(trace_bytes).hexdigest()

def test_determinism():
    bc_path = "tests/stress/industrial_stress.bc"
    if not os.path.exists(bc_path):
        print("Error: Compile tests/stress/industrial_stress.ci first.")
        return

    with open(bc_path, 'rb') as f:
        bytecode = pickle.load(f)

    seed = 42
    print(f"Running Simulation 1 (Seed: {seed})...")
    hash1 = run_simulation_and_get_hash(bytecode, seed)
    
    print(f"Running Simulation 2 (Seed: {seed})...")
    hash2 = run_simulation_and_get_hash(bytecode, seed)
    
    print(f"\nHash 1: {hash1}")
    print(f"Hash 2: {hash2}")
    
    if hash1 == hash2:
        print("\n[SUCCESS] DETERMINISM VERIFIED: Bit-for-bit identical results over 100,000 operations.")
    else:
        print("\n[FAILURE] NONDETERMINISM DETECTED: Results diverged despite identical seeds.")
        sys.exit(1)

if __name__ == "__main__":
    test_determinism()
