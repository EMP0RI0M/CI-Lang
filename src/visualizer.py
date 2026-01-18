import numpy as np
import matplotlib.pyplot as plt
import os

def generate_heatmap(agent_states, entropy, filename="thermodynamic_heatmap.png"):
    """
    Generates a visualization of swarm 'heat' (variance/entropy).
    """
    plt.figure(figsize=(10, 6))
    
    # Each agent represents a cell in a grid
    size = int(np.ceil(np.sqrt(len(agent_states))))
    grid = np.zeros((size, size))
    
    for i, val in enumerate(agent_states):
        row, col = divmod(i, size)
        grid[row, col] = val
        
    plt.imshow(grid, cmap='hot', interpolation='nearest')
    plt.colorbar(label='State Value (Thermodynamic Potential)')
    plt.title(f"CI-Lang 2.0 Thermodynamic Heat Map (Global Entropy: {entropy:.3f})")
    
    filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    plt.savefig(filepath)
    plt.close()
    print(f"Heat map saved to {filepath}")

if __name__ == "__main__":
    # Mock data for demonstration
    mock_states = np.random.rand(100)
    generate_heatmap(mock_states, 0.508)
