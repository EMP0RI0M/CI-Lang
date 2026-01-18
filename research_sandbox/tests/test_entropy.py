import numpy as np
import pytest
from fluxvm.entropy import entropy_histogram, entropy_ksg

def test_entropy_distribution():
    # Setup: 1000 samples of uniform noise [0, 1]
    # Maximum entropy for uniform is ~log2(range/cell_size), but let's check non-negative stability
    rng = np.random.RandomState(42)
    data = rng.rand(1000)
    
    h_hist = entropy_histogram(data)
    h_ksg = entropy_ksg(data)
    
    print(f"Hist: {h_hist:.4f} | KSG: {h_ksg:.4f}")
    
    assert h_hist > 0
    assert h_ksg > 0
    # KSG is generally more accurate, let's ensure it doesn't return NaN
    assert not np.isnan(h_ksg)

def test_entropy_convergence():
    # Setup: 1000 samples of almost identical value (delta function)
    # Entropy should be near zero
    data = np.ones(1000) * 0.5 + np.random.normal(0, 1e-6, 1000)
    
    h_hist = entropy_histogram(data)
    h_ksg = entropy_ksg(data)
    
    print(f"Delta Hist: {h_hist:.4f} | Delta KSG: {h_ksg:.4f}")
    
    # Delta function entropy should be significantly lower than uniform
    assert h_ksg < 1.0 
