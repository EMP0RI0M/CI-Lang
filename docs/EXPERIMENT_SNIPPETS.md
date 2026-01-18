# Chaos Intelligence: Experiment Code Snippets

This document contains the core executable logic for the key experiments conducted during the development of CI-Lang.

## 1. The Chaos MVP (Logistic Map Swarm)
The foundational experiment proving that a Python loop could sustain a population of chaotic agents.

```python
import numpy as np

# Parameters
N = 100
r_params = np.random.uniform(3.5, 4.0, N) # Chaotic regime
states = np.random.rand(N)

# The Logistic Map Update
for t in range(100):
    # vectorized update: x(t+1) = r * x(t) * (1 - x(t))
    states = r_params * states * (1.0 - states)
    print(f"Tick {t}: Mean {np.mean(states):.4f}")
```

## 2. Entropy Stabilization (Miller-Madow)
Moving from raw histogram entropy to a bias-corrected metric for small populations.

```python
def stabilized_entropy(states, bins=10):
    # 1. Compute Raw Histogram
    counts, _ = np.histogram(states, bins=bins, range=(-1, 1))
    
    # 2. Filter Zeros
    nonzero_counts = counts[counts > 0]
    total = np.sum(nonzero_counts)
    probs = nonzero_counts / total
    
    # 3. Raw Shannon Entropy
    raw_entropy = -np.sum(probs * np.log2(probs))
    
    # 4. Miller-Madow Correction
    # Compensation for finite sample size bias
    K = len(nonzero_counts)
    correction = (K - 1) / (2 * total)
    
    return raw_entropy + correction
```

## 3. The Consensus Mechanism (Judge Memory)
The logic that allowed a regulator to "learn" to resolve conflict faster.

```python
def judge_loop(divergence_history, memory):
    current_div = divergence_history[-1]
    
    # Conflict Detection Threshold
    if current_div > 0.4:
        # CONFLICT!
        
        # 1. Calculate Damping based on Memory
        # The more "trauma" (memory) we have, the harder we slam the brakes.
        damping_strength = -0.1 * (1.0 + (memory * 2.0))
        
        # 2. Update Memory (Learning)
        # We remember this instability.
        memory += 0.002 
        
        return damping_strength, memory, "CONFLICT"
        
    else:
        # PEACE
        return 0.01, memory, "HARMONY"
```

## 4. Semantic Distillation (LLM Council)
Connecting the chaotic core to an LLM via API to determine governance strategy.

```python
import requests
import json

def ask_semantic_council(divergence):
    prompt = f"System Divergence is {divergence:.2f}. Recommend strategy: 'DAMPEN' or 'ALLOW'."
    
    # Mocking standard OpenAI/OpenRouter API call
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": "Bearer SK-...", "Content-Type": "application/json"},
        data=json.dumps({
            "model": "xiaomi/mimo-v2-flash:free",
            "messages": [{"role": "user", "content": prompt}]
        })
    )
    
    reasoning = response.json()['choices'][0]['message']['content']
    
    if "DAMPEN" in reasoning:
        return -0.2 # Strong Negative Feedback
    else:
        return 0.05 # Positive Feedback (Exploration)
```

## 5. FluxVM Bytecode (Assembly)
Why we built a VM. This snippet illustrates how "Chaos" is an opcode.

```asm
# Agent Update Routine
LOAD_CELL 0       # Load current state
PUSH_CONST 0.1    # Push volatility
NOISE             # Generate unique thermodynamic noise
ADD               # s + noise
LOGISTIC_MAP      # Apply non-linearity
STORE_CELL 0      # Save state
```
