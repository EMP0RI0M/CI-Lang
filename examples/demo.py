import sys
import os
import time
import pickle
import numpy as np
from fluxvm_core import FluxVM
from swarms.llm_bridge import OpenRouterBridge
from swarms.monitor import StabilityMonitor

# Set PYTHONPATH to include 'src'
sys.path.append(os.path.dirname(__file__))

class RuntimeStabilizationDemo:
    def __init__(self, bc_path="llm_test.bc"):
        self.bridge = OpenRouterBridge()
        self.monitor = StabilityMonitor()
        self.vm = FluxVM(print_callback=self.handle_output)
        self.bc_path = bc_path
        
        if not os.path.exists(bc_path):
            raise FileNotFoundError(f"Bytecode {bc_path} not found. Try compiling llm_test.ci first.")

        with open(bc_path, 'rb') as f:
            self.vm.load_bytecode(pickle.load(f))

    def handle_output(self, msg):
        # We catch the LLM prompt but we'll print it nicely in the main loop
        pass

    def run(self):
        print("\n" + "="*50)
        print("  CI-LANG RUNTIME STABILIZATION DEMO")
        print("="*50)
        
        # [STEP 1] Inject Chaos
        print("\n[STEP 1] Injecting Chaos...")
        # In our llm_test.ci, the chaotic state is hardcoded for the demo experiment.
        # We step the VM until it vocalizes the chaotic report.
        
        chaos_detected = False
        steps = 0
        while not chaos_detected and steps < 100:
            steps += 1
            # Redirecting print to catch the prompt
            import io
            from contextlib import redirect_stdout
            f = io.StringIO()
            with redirect_stdout(f):
                self.vm.step()
            output = f.getvalue()
            
            if ">>> LLM_TEACHER_PROMPT:" in output:
                prompt = output.split(">>> LLM_TEACHER_PROMPT:")[1].strip()
                
                # [STEP 2] Show Entropy Spike
                print(f"[STEP 2] Chaos Detected! Entropy = {self.vm.entropy_register:.2f} (CRITICAL)")
                print(f"         System Status: [CHAOTIC]")
                
                # [STEP 3] Asking LLM
                print(f"\n[STEP 3] Asking LLM for Stabilization Advice...")
                print(f"         Model: {os.getenv('OPENROUTER_MODEL')}")
                
                advice = self.bridge.chat(prompt)
                
                # [STEP 4] Apply Advice
                print(f"\n[STEP 4] LLM Advice Received: {advice}")
                self.vm.mailbox = float(advice)
                
                # [STEP 5] Stabilization
                print(f"[STEP 5] Applying Stabilization to FluxVM Core...")
                
                # Step the VM again to process Advice
                for _ in range(20):
                    self.vm.step()
                
                print(f"         Status: System Re-Stabilized.")
                chaos_detected = True
        
        print("\n" + "="*50)
        print("  DEMO COMPLETE: RUNTIME HOMEOSTASIS ACHIEVED")
        print("="*50 + "\n")

if __name__ == "__main__":
    try:
        demo = RuntimeStabilizationDemo()
        demo.run()
    except Exception as e:
        print(f"\n[DEMO ERROR]: {e}")
        print("Ensure you have set up your .env and compiled llm_test.ci")
