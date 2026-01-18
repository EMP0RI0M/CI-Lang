import numpy as np

class EntropyController:
    """
    Thermodynamic Governor (PID-like) to maintain the system at the Edge of Chaos.
    """
    def __init__(self, target_e=0.45, k_p=0.01, k_i=0.001):
        self.target_e = target_e
        self.k_p = k_p
        self.k_i = k_i
        self.integral_error = 0.0
        self.volatility = 0.1

    def update(self, current_e):
        """
        Adjusts global volatility based on the delta from target entropy.
        """
        error = self.target_e - current_e
        self.integral_error += error
        
        # Adjust volatility: if e is too high, lower volatility; if too low, raise it.
        adjustment = (self.k_p * error) + (self.k_i * self.integral_error)
        self.volatility += adjustment
        
        # Clamp volatility to operational range [0.01, 0.9]
        self.volatility = max(0.01, min(0.9, self.volatility))
        return self.volatility
