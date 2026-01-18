import time
import random
from fluxvm import FluxVM

def benchmark_arithmetic(iterations=100000):
    print(f"--- Benchmarking Arithmetic ({iterations} iterations) ---")
    
    # Python Implementation
    start_time = time.time()
    x = 0
    for _ in range(iterations):
        x += 1
        x *= 2
        x -= 1
    py_time = time.time() - start_time
    print(f"Python Time: {py_time:.4f}s")

    # FluxVM Implementation
    vm = FluxVM()
    # Program: for i in iterations: result = (result + 1) * 2 - 1
    # We'll simulate a long sequence for the prototype.
    # Note: The prototype is much slower, so we'll reduce iterations for FluxVM.
    vm_iterations = iterations // 100
    bytecode = []
    bytecode.append(("PUSH", 0))
    bytecode.append(("STORE", "result"))
    for _ in range(vm_iterations):
        bytecode.append(("LOAD", "result"))
        bytecode.append(("PUSH", 1))
        bytecode.append(("ADD",))
        bytecode.append(("PUSH", 2))
        bytecode.append(("MUL",))
        bytecode.append(("PUSH", 1))
        bytecode.append(("SUB",))
        bytecode.append(("STORE", "result"))
    bytecode.append(("HALT",))

    start_time = time.time()
    vm.load_code(bytecode)
    vm.run()
    vm_time = time.time() - start_time
    print(f"FluxVM (Prototype) Time for {vm_iterations} iters: {vm_time:.4f}s")
    print(f"Scaled FluxVM Time for {iterations} iters (est): {vm_time * 100:.4f}s")

def test_chaos_resistance():
    print("\n--- Testing Chaos Resistance ---")
    vm = FluxVM()
    
    # Scenario: Finding a 'match' in a noisy environment.
    # We try to match '10' with '10' under varying entropy.
    
    entropies = [0.0, 0.2, 0.5, 0.8, 1.0]
    results = []

    for e in entropies:
        matches = 0
        trials = 100
        
        # Bytecode to check equality under entropy 'e'
        bytecode = [
            ("SET_E", e),
            ("PUSH", 10),
            ("PUSH", 10),
            ("CHAOS_EQ",),
            ("HALT",)
        ]
        
        # We'll modify PRINT to handle stats collection inside the test for efficiency
        # But for now, we'll just run VM multiple times.
        for _ in range(trials):
            vm.load_code(bytecode)
            # Capture output if possible, but FluxVM prints directly. 
            # I'll modify FluxVM class slightly to return the top stack value.
            vm.run()
            if vm.data_stack and vm.data_stack[-1] == True:
                matches += 1
            # Clean stack for next trial
            vm.data_stack = []

        results.append((e, matches))

    print("\nChaos Resistance Report (Match 10 == 10):")
    for e, m in results:
        print(f"Entropy {e:.1f}: {m}/{trials} matches successful")

if __name__ == "__main__":
    benchmark_arithmetic()
    test_chaos_resistance()
