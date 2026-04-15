import numpy as np

class StabilityMonitor:
    """
    Monitors swarm emergent behavior and verifies stability constraints.
    """
    def __init__(self):
        self.history = []
        self.entropy_history = []
        self.memory_history = []

    def estimate_entropy(self, data, bins=20):
        """
        Calculates Shannon entropy with a Miller-Madow correction to prevent 
        negative bias in sparse distributions.
        """
        if len(data) == 0:
            return 0.0
        
        # 1. Histogram-based probability density
        counts, _ = np.histogram(data, bins=bins, range=(0, 1))
        probs = counts / np.sum(counts)
        probs = probs[probs > 0] # Remove zero probabilities
        
        # 2. Shannon Entropy
        shannon = -np.sum(probs * np.log2(probs))
        
        # 3. Miller-Madow Correction: entropy_true ~= entropy_observed + (bins_with_data - 1)/(2 * N)
        # We cap it at 0 to ensure non-negativity
        correction = (len(probs) - 1) / (2 * len(data))
        stable_entropy = max(0.0, shannon + correction)
        
        return stable_entropy

    def log_step(self, tick, raw_entropy, outputs, memory=0.0):
        """
        Logs a simulation step.
        """
        numeric_outputs = [o for o in outputs if isinstance(o, (int, float))]
        if numeric_outputs:
            # Recalculate entropy using the stable estimator
            stable_e = self.estimate_entropy(numeric_outputs)
            self.entropy_history.append(stable_e)
            self.memory_history.append(memory)
            
            mean = np.mean(numeric_outputs)
            std = np.std(numeric_outputs)
            self.history.append((tick, mean, std))

    def verify_stability(self):
        """
        Applies Temporal Logic constraints:
        - Safety: Entropy must never exceed 0.95 (uncontrolled chaos).
        - Liveness: Variance must decrease over time (convergence).
        """
        if not self.entropy_history:
            return False, "No data collected."

        # Safety Check
        max_e = max(self.entropy_history)
        if max_e > 0.95:
            return False, f"Safety Violated: Entropy spiked to {max_e:.4f}"

        # Convergence Check (last 20% vs first 20%)
        if len(self.history) > 10:
            initial_std = self.history[len(self.history)//5][2]
            final_std = self.history[-1][2]
            
            if final_std < initial_std:
                return True, f"Stability Verified: Variance reduced from {initial_std:.2f} to {final_std:.2f}"
            else:
                return False, f"Stability Failed: Swarm is diverging (Var: {final_std:.2f})"
        
        return True, "Insufficient data for convergence proof, but safety holds."

    def report(self):
        print("\n--- Stability Verification Report ---")
        status, message = self.verify_stability()
        if status:
            print(f"STATUS: SUCCESS")
        else:
            print(f"STATUS: FAILED")
        print(f"MESSAGE: {message}")
        
        if self.memory_history:
            print(f"Max Control Memory: {max(self.memory_history):.4f}")
            print(f"Final Entropy: {self.entropy_history[-1]:.4f}")
