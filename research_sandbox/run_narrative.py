import numpy as np
import yaml
import json
import time
from fluxvm.agent import Agent
from fluxvm.swarm import Swarm
from fluxvm.entropy import estimate_entropy
from fluxvm.controller import EntropyController
from fluxvm.semantics import SemanticMapper
from decoder import TemplateDecoder

def run_narrative_experiment(config_path):
    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    n_agents = config.get('n_agents', 1000)
    steps = config.get('steps', 2000)
    target_e = config.get('target_e', 0.45)
    seed = config.get('seed', 42)
    
    np.random.seed(seed)
    
    # 1. Initialize Components
    agents = [Agent(i, initial_state=0.0) for i in range(n_agents)]
    swarm = Swarm(agents, alpha=0.01, decay=0.98) # Lower alpha for slower, cleaner association
    controller = EntropyController(target_e=target_e, k_p=0.02)
    
    mapper = SemanticMapper(vocab_size=n_agents)
    vocab = ["cat", "dog", "man", "woman", "robot", "hunts", "chases", "watches", "seeks", "greets", "mouse", "bone", "chaos", "order", "logic"]
    mapper.load_vocab(vocab)
    
    decoder = TemplateDecoder(mapper)
    
    # 2. Load Narrative Corpus
    with open("data/svo_corpus.txt", "r") as f:
        sentences = f.read().splitlines()
    
    print(f"Starting Phase 15 Narrative Experiment: {len(sentences)} sentences.")
    
    # 3. Training Loop (Exposure to Sequences)
    for epoch in range(3):
        print(f"--- Epoch {epoch+1} ---")
        for sentence in sentences[:30]: # Smaller subset for clear results
            words = sentence.split()
            # For each word in the sequence
            for word in words:
                stim = mapper.text_to_stimulus(word, cluster_size=1)
                # Stimulate for 3 ticks
                for t_word in range(3):
                    for i, val in enumerate(stim):
                        if val > 0:
                            swarm.agents[i].state = 1.0
                    
                    states = swarm.get_states()
                    curr_e = estimate_entropy(states)
                    swarm.step(global_volatility=controller.update(curr_e))
                
                # Intra-sentence pause (allow trace to persist but word to decay)
                for _ in range(5):
                    swarm.step(global_volatility=controller.update(estimate_entropy(swarm.get_states())))
            
            # Long inter-sentence rest to clear context completely
            for _ in range(30):
                swarm.step(global_volatility=controller.update(estimate_entropy(swarm.get_states())))

    # 4. Verification: Prediction Test
    print("\n--- Narrative Prediction Test ---")
    test_words = ["cat", "dog", "woman"]
    for test_word in test_words:
        print(f"\nFeeding: '{test_word}'...")
        # Clear swarm state
        for a in agents: a.state = 0.0
        swarm.prev_states = np.zeros(n_agents)
        
        stim = mapper.text_to_stimulus(test_word, cluster_size=1) # Pinpoint stim
        for i, val in enumerate(stim):
            if val > 0: swarm.agents[i].state = 1.0
            
        # Run a few ticks to propagate through weights
        for _ in range(5):
            states = swarm.get_states()
            swarm.step(global_volatility=0.01)
            
        readout = swarm.get_readout_vector()
        # Mask out the stim word and its small cluster
        word_idx = mapper.word_to_id[test_word]
        readout[max(0, word_idx-1):word_idx+2] = 0.0
        
        # Check top 5 predictions
        top_indices = np.argsort(readout)[-5:][::-1]
        print(f"Top predictions after '{test_word}':")
        for idx in top_indices:
            word = mapper.id_to_word.get(idx, f"agent_{idx}")
            print(f"  -> {word}: {readout[idx]:.4f}")

    # 5. Check Asymmetry: W(cat -> hunts) vs W(hunts -> cat)
    cat_idx = mapper.word_to_id["cat"]
    hunts_idx = mapper.word_to_id["hunts"]
    w_ch = swarm.weights[cat_idx].get(hunts_idx, 0.0)
    w_hc = swarm.weights[hunts_idx].get(cat_idx, 0.0)
    print(f"\n--- Asymmetry Check ---")
    print(f"W(cat -> hunts): {w_ch:.4f}")
    print(f"W(hunts -> cat): {w_hc:.4f}")
    if w_ch > w_hc:
        print("TEMPORAL ASYMMETRY VERIFIED: The Arrow of Time is established.")

if __name__ == "__main__":
    run_narrative_experiment("configs/demo.yaml")
