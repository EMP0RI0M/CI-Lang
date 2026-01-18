import numpy as np
import pickle
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))
from fluxvm_core import FluxVM

def test():
    # Load bytecode
    with open("examples/matrix_test.bc", "rb") as f:
        code = pickle.load(f)

    # Initialize VM with dummy weights and states
    weights = np.array([[1.0, 0.1], [0.2, 0.9]])
    states = np.array([0.5, 0.8])
    
    vm = FluxVM(weights=weights, states=states)
    vm.load_bytecode(code)
    
    print("--- Running Matrix VM Test ---")
    vm.run()
    print("--- Test Complete ---")

if __name__ == "__main__":
    test()
