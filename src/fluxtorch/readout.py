from fluxtorch.tensor import FluxTensor, Module
from fluxtorch.optim import ChaosOptimizer
import numpy as np

class ChaosReadout(Module):
    """
    The interpretative layer for a Chaos Reservoir.
    It takes the high-dimensional chaotic states of a swarm and 
    reduces them to a purposeful output.
    """
    def __init__(self, swarm_size, output_dim=1):
        super().__init__()
        # Initial weight for each agent in the swarm
        self.weights = [FluxTensor(np.random.randn() * 0.1, chaos=0.01) for _ in range(swarm_size)]
        self.bias = FluxTensor(0.0, chaos=0.01)
        self.parameters = self.weights + [self.bias]

    def forward(self, swarm_states):
        """
        swarm_states: list of floats from agent data stacks
        """
        output = sum(w.value * s for w, s in zip(self.weights, swarm_states)) + self.bias.value
        return output

    def compute_loss(self, prediction, target):
        return (prediction - target)**2

    def backprop_chaos(self, loss, swarm_states):
        """
        Manual 'Chaos Gradient' for the readout layer.
        Since we don't backprop through the swarm, we only tune the weights.
        """
        for i, w in enumerate(self.weights):
            # Simple heuristic gradient
            grad = 2 * (sum(self.weights[j].value * swarm_states[j] for j in range(len(self.weights))) + self.bias.value - loss) * swarm_states[i]
            w.backward(grad)
        
        bias_grad = 2 * (sum(self.weights[j].value * swarm_states[j] for j in range(len(self.weights))) + self.bias.value - loss)
        self.bias.backward(bias_grad)
