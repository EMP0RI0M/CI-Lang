import numpy as np
import yaml
import json
import os
import time
from fluxvm.agent import Agent
from fluxvm.swarm import Swarm
from fluxvm.entropy import estimate_entropy
from fluxvm.controller import EntropyController
from fluxvm.semantics import SemanticMapper
from decoder import TemplateDecoder

def run_experiment(config_path):
    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    n_agents = config.get('n_agents', 1000)
    steps = config.get('steps', 1000)
    target_e = config.get('target_e', 0.45)
    seed = config.get('seed', 42)
    entropy_method = config.get('entropy_method', 'histogram')
    
    np.random.seed(seed)
    
    # 1. Initialize Components
    agents = [Agent(i, initial_state=0.0) for i in range(n_agents)]
    swarm = Swarm(agents, alpha=config.get('alpha', 0.02), decay=config.get('decay', 0.98))
    controller = EntropyController(target_e=target_e, k_p=config.get('k_p', 0.01))
    
    mapper = SemanticMapper(vocab_size=n_agents)
    # Load a small sample vocabulary
    sample_words = ["cat", "animal", "logic", "chaos", "order", "entropy", "mind", "machine"]
    mapper.load_vocab(sample_words)
    
    decoder = TemplateDecoder(mapper)
    
    history = {
        'tick': [],
        'entropy': [],
        'volatility': [],
        'mean_state': []
    }
    
    print(f"Starting Phase 14 Experiment: {config.get('name', 'Proto-L')}")
    
    # Simulation Loop
    for t in range(steps):
        # Every 200 ticks, inject a semantic stimulus
        if t % 200 == 0:
            word = sample_words[ (t // 200) % len(sample_words) ]
            print(f"Stimulating Swarm with concept: '{word}'")
            stim = mapper.text_to_stimulus(word)
            # Apply stimulus to agent states with persistence
            for i, val in enumerate(stim):
                if val > 0:
                    swarm.agents[i].state = max(swarm.agents[i].state, val)
        
        states = swarm.get_states()
        
        # 1. Measure Entropy
        current_e = estimate_entropy(states, method=entropy_method)
        
        # 2. Update Governor
        vol = controller.update(current_e)
        
        # 3. Step Swarm (Hebbian Learning happens here)
        swarm.step(global_volatility=vol)
        
        # 4. Readout and Decode occasionally
        if t % 100 == 0:
            readout = swarm.get_readout_vector()
            response = decoder.decode(readout)
            mean_s = np.mean(states)
            
            # Find top 5 active indices
            top_indices = np.argsort(readout)[-5:][::-1]
            top_vals = [f"{idx}:{readout[idx]:.2f}" for idx in top_indices]
            
            print(f"Tick {t:04d} | Entropy: {current_e:.4f} | Vol: {vol:.4f} | Top: {top_vals} | Response: {response}")
            
            # Write current metrics for safety monitor
            metrics = {'tick': t, 'entropy': float(current_e), 'volatility': float(vol)}
            with open('current_metrics.json', 'w') as f:
                json.dump(metrics, f)
            
            history['tick'].append(t)
            history['entropy'].append(float(current_e))
            history['volatility'].append(float(vol))
            history['mean_state'].append(float(mean_s))
            if t % 100 == 0:
                print(f"Tick {t:04d} | Entropy: {current_e:.4f} | Vol: {vol:.4f}")

    # Save results
    timestamp = int(time.time())
    output_path = f"d:/ci lang/research_sandbox/results/run_{timestamp}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump({'config': config, 'history': history}, f, indent=2)
    
    print(f"Experiment complete. Results saved to {output_path}")

if __name__ == "__main__":
    # Create a default config if none exists
    default_config = "d:/ci lang/research_sandbox/configs/demo.yaml"
    os.makedirs(os.path.dirname(default_config), exist_ok=True)
    
    if not os.path.exists(default_config):
        with open(default_config, 'w') as f:
            yaml.dump({
                'name': 'Edge of Chaos Baseline',
                'n_agents': 200,
                'steps': 1000,
                'target_e': 0.45,
                'seed': 42
            }, f)
            
    run_experiment(default_config)
