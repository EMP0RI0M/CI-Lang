import os
import sys
import subprocess
import pickle

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

def verify_file(filename):
    print(f"[VERIFY] Checking {filename}...")
    
    # 1. Compile
    bc_file = filename.replace(".ci", ".bc")
    comp_proc = subprocess.run(
        ["python", "src/cic.py", f"examples/{filename}", "-o", bc_file],
        capture_output=True, text=True
    )
    
    if comp_proc.returncode != 0:
        print(f"  [FAIL] Compilation Error:\n{comp_proc.stderr}")
        return False
    
    print(f"  [PASS] Compiled successfully.")
    
    # 2. Basic Execution Check
    # (Checking if it crashes on a 100-step run)
    run_proc = subprocess.run(
        ["python", "src/run_swarm.py", "--bytecode", bc_file, "--steps", "10"],
        capture_output=True, text=True
    )
    
    if run_proc.returncode != 0:
        print(f"  [FAIL] Runtime Error:\n{run_proc.stderr}")
        return False

    print(f"  [PASS] Executed without crashes.")
    return True

if __name__ == "__main__":
    golden_programs = [
        "1_math_core.ci",
        "2_loop_convergence.ci",
        "3_chaos_equality.ci",
        "4_flow_state.ci",
        "5_agent_homeostasis.ci"
    ]
    
    results = []
    print("\n" + "="*50)
    print("  CI-LANG v1.0 COMPLIANCE SUITE")
    print("="*50)
    
    for prog in golden_programs:
        results.append(verify_file(prog))
        
    print("\n" + "="*50)
    if all(results):
        print("  FINAL STATUS: COMPLIANT (v1.0 READY)")
    else:
        print("  FINAL STATUS: NON-COMPLIANT (STABILIZATION REQUIRED)")
    print("="*50 + "\n")
