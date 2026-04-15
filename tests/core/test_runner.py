import os
import sys
import subprocess
import glob

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

def run_test(path, expected_status="PASS"):
    print(f"[CORE TEST] {os.path.basename(path)}... ", end="")
    bc_file = path.replace(".ci", ".bc")
    
    # Compile
    comp = subprocess.run(["python", "src/cic.py", path, "-o", bc_file], capture_output=True, text=True)
    if comp.returncode != 0:
        if expected_status == "FAIL_COMP":
            print("GOT EXPECTED COMPILATION FAILURE.")
            return True
        print(f"COMPILATION FAILED:\n{comp.stderr}")
        return False

    # Run
    # Use run_swarm in a minimal mode or just pure VM
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    run = subprocess.run(["python", "src/run_swarm.py", "--bytecode", bc_file, "--steps", "10"], capture_output=True, text=True, env=env)
    
    if run.returncode != 0:
        if expected_status == "FAIL_RUN":
            print("GOT EXPECTED RUNTIME FAILURE.")
            return True
        print(f"RUNTIME FAILED:\n{run.stderr}")
        return False
    
    if expected_status == "PASS":
        print("PASSED.")
        return True
    else:
        print(f"EXPECTED FAILURE BUT IT PASSED.")
        return False

if __name__ == "__main__":
    tests = [
        ("tests/core/1_arithmetic.ci", "PASS"),
        ("tests/core/2_flow.ci", "PASS"),
        ("tests/core/3_chaos.ci", "PASS"),
        ("tests/core/4_type_fail.ci", "FAIL_RUN"),
        ("tests/core/5_div_zero.ci", "FAIL_RUN"),
        ("tests/core/6_constants.ci", "PASS"),
    ]
    
    all_passed = True
    for t_path, t_status in tests:
        if not run_test(t_path, t_status):
            all_passed = False
            
    if all_passed:
        print("\n[SUCCESS] CORE SYSTEM IS STABLE")
        sys.exit(0)
    else:
        print("\n[FAILURE] CORE SYSTEM IS FRAGILE - FIX REQUIRED")
        sys.exit(1)
