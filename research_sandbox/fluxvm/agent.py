import numpy as np

class Agent:
    """
    Standard CI Agent with Alive Memory (State + Volatility).
    """
    def __init__(self, id, initial_state=0.5, volatility=0.1):
        self.id = id
        self.state = initial_state
        self.volatility = volatility
        self.history = [initial_state]

    def update(self, delta: float, volatility: float):
        """
        Updates the agent state based on incoming force (delta) and a 
        volatility-scaled noise component.
        """
        # Sync local volatility with global for this tick
        self.volatility = volatility
        
        # Thermodynamic update: new_state = old_state + force + randomness
        noise = np.random.normal(0, 1.0)
        self.state = self.state + delta + (self.volatility * noise)
        
        # Clamp to phase space boundary [0, 1]
        self.state = max(0.0, min(1.0, self.state))
        self.history.append(self.state)
        return self.state
