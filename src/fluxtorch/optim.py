import random

class ChaosOptimizer:
    """
    The ChaosOptimizer leverages entropy to escape local minima.
    It performs 'Entropy Spikes' when progress stalls.
    """
    def __init__(self, parameters, lr=0.01, temp=0.1):
        self.parameters = parameters
        self.lr = lr
        self.temp = temp
        self.loss_history = []

    def step(self, loss, global_entropy):
        """
        Updates parameters. Higher global_entropy increases 
        the 'search radius' of the adjustment.
        """
        self.loss_history.append(loss)
        
        # Detect stalling
        is_stalled = len(self.loss_history) > 5 and abs(self.loss_history[-1] - self.loss_history[-5]) < 0.001
        
        spike = 1.0 if is_stalled else global_entropy
        
        for p in self.parameters:
            # Gradient clipping to prevent thermodynamic explosion
            grad = max(-1.0, min(1.0, p.grad))
            
            # Gradient update + stochastic kick
            kick = (random.random() - 0.5) * spike * self.temp
            p.value -= (self.lr * grad) + kick
            
            # Dampen local chaos as we converge
            # p.chaos *= 0.99 
