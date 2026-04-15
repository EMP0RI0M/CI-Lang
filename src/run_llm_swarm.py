import sys
import os
import time
import pickle
from fluxvm_core import FluxVM
from swarms.llm_bridge import OpenRouterBridge

# Set PYTHONPATH to include 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

class LLMSwarmRunner:
    def __init__(self, bytecode_path):
        self.bridge = OpenRouterBridge()
        self.vm = FluxVM(print_callback=self.handle_output)
        
        with open(bytecode_path, 'rb') as f:
            self.vm.load_bytecode(pickle.load(f))
            
        self.last_api_call = 0
        self.api_cooldown = 10 # Seconds between LLM requests

    def handle_output(self, msg):
        print(f"[FluxVM]: {msg}")
        
        # Detect the LLM interaction tag
        if isinstance(msg, str) and ">>> LLM_TEACHER_PROMPT:" in msg:
            now = time.time()
            if now - self.last_api_call > self.api_cooldown:
                prompt = msg.split(">>> LLM_TEACHER_PROMPT:")[1].strip()
                print(f"\n[HOST]: Intercepted Prompt. Consulting LLM Teacher...")
                
                advice = self.bridge.chat(prompt)
                
                print(f"[HOST]: LLM Advice Received: {advice}")
                self.vm.mailbox = float(advice)
                self.last_api_call = now
            else:
                print(f"[HOST]: API Cooldown Active. Skipping request.")

    def run(self, steps=500):
        print("--- CI-Lang / LLM Hybrid Loop started ---")
        for i in range(steps):
            # We run one block of 'ticks'
            self.vm.step()
            time.sleep(0.01) # Small delay for observation

if __name__ == "__main__":
    if not os.path.exists("llm_test.bc"):
        print("Error: llm_test.bc not found. Please compile llm_test.ci first.")
        sys.exit(1)
        
    runner = LLMSwarmRunner("llm_test.bc")
    runner.run()
