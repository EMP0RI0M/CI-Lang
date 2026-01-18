from .tensor import FluxTensor, Module
import numpy as np

class Linear(Module):
    """
    A chaotic linear layer. Weights are FluxTensors.
    """
    def __init__(self, in_features, out_features):
        super().__init__()
        self.weights = FluxTensor(np.random.randn() * 0.1, chaos=0.2)
        self.bias = FluxTensor(0.0, chaos=0.1)
        self.parameters = [self.weights, self.bias]

    def forward(self, x, entropy):
        # We sample weights based on entropy to simulate chaotic signal propagation
        w = self.weights.sample(entropy)
        b = self.bias.sample(entropy)
        return x * w + b

class EntropyRegulator(Module):
    """
    A layer that learns to control the system entropy.
    """
    def __init__(self):
        super().__init__()
        self.target_entropy = FluxTensor(0.5, chaos=0.05)
        self.parameters = [self.target_entropy]

    def forward(self, x, entropy):
        # Dampens signal if current entropy is higher than target
        reg = 1.0 - abs(entropy - self.target_entropy.value)
        return x * max(0.1, reg)
