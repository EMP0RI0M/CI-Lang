import numpy as np
from numba import njit

@njit
def physics_step(states, weights, volatility, global_inhibition_rate):
    """
    Pure thermodynamic update (The 'Physics' of the swarm).
    Weights are now READ-ONLY for this step.
    """
    n = states.shape[0]
    
    # 1. State Update (Vectorized)
    influence_vec = np.dot(weights.T, states)
    
    mean_state = np.mean(states)
    inhibition = global_inhibition_rate * mean_state
    
    # Generate noise for all agents at once
    noise_vec = np.random.normal(0, 1.0, n)
    
    # Vectorized state update
    # dt = 0.7 decay factor
    new_states = (states * 0.7) + influence_vec - inhibition + (volatility * noise_vec)
    
    # Clamp results to [0, 1]
    return np.maximum(0.0, np.minimum(1.0, new_states))

@njit
def hebbian_logic_step(states, prev_states, weights, alpha, decay):
    """
    Python-based learning fallback (The 'Logic' being replaced by CI).
    """
    pre_active_idx = np.where(prev_states > 0.3)[0]
    post_active_idx = np.where(states > 0.3)[0]
    
    for i in pre_active_idx:
        for j in post_active_idx:
            if i != j:
                weights[i, j] += alpha * prev_states[i] * states[j]
        weights[i, :] *= decay
    return weights
