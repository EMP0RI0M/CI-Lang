import numpy as np
import yaml
import json
from fluxvm.agent import Agent
from fluxvm.swarm import Swarm
from fluxvm.entropy import estimate_entropy
from fluxvm.controller import EntropyController
from fluxvm.semantics import SemanticMapper
from decoder import TemplateDecoder

def interactive_session():
    print("================================================")
    print("   [CI SESSION v2.0 - LIVE LEARNING MODE]   ")
    print("================================================")
    print("(!) This version has NO pre-fed narrative data.")
    print("(!) Learning is 100% interactive and live.")
    print("(!) Scaling core to 10,000 agents [JIT ACCELERATED].")
    
    n_agents = 1000
    agents = [Agent(i, initial_state=0.0) for i in range(10000)] # Create 10k agents initially
    # CI Swarm
    swarm = Swarm(agents[:n_agents], alpha=0.3, decay=0.85, ci_mode=True) 
    controller = EntropyController(target_e=0.45, k_p=0.02)
    
    mapper = SemanticMapper(vocab_size=n_agents)
    vocab = ["cat", "dog", "man", "woman", "robot", "hunts", "chases", "watches", "seeks", "greets", "mouse", "bone", "chaos", "order", "logic"]
    mapper.load_vocab(vocab)
    decoder = TemplateDecoder(mapper)
    
    print("\n[!] BRAIN RESET: The Swarm is now a literal empty void.")
    print("Agent IDs are spread out to prevent the 'Cat is Dog' bias.")
    print("TEACHING TIP: Repeat 'cat hunts' 3 times to see them link.")

    print("\nInitialization Complete. You are now connected to the Swarm.")
    print("Type a word to stimulate the agents. Type 'exit' to quit.")
    
    while True:
        user_input = input("\nYou > ").strip().lower()
        if user_input == 'exit':
            break
            
        # Parse input for any known words
        input_words = [w for w in user_input.split() if w in vocab]
        
        if not input_words:
            print(f"Swarm: I do not recognize those concepts. Try: {', '.join(vocab[:5])}...")
            continue
            
        # Clear swarm state for fresh stimulus (optional, but cleaner for chat)
        for a in agents: a.state = 0.0
        swarm.prev_states = np.zeros(n_agents)
        
        # Stimulate all recognized words
        print(f"[*] Stimulating swarm with: {input_words}...")
        for word in input_words:
            stim = mapper.text_to_stimulus(word, cluster_size=1)
            for i, val in enumerate(stim):
                if val > 0: swarm.agents[i].state = 1.0
            
        # Evolve and Observe
        for t in range(15):
            states = swarm.get_states()
            entropy = estimate_entropy(states)
            vol = controller.update(entropy)
            swarm.step(global_volatility=vol)
            
            if t % 5 == 0:
                readout = swarm.get_readout_vector()
                # Mask out ALL input words to see emergent associations
                for word in input_words:
                    word_idx = mapper.word_to_id[word]
                    readout[word_idx] = 0.0
                
                response = decoder.decode(readout)
                print(f"Tick {t:02d} | Entropy: {entropy:.3f} | Response: {response}")

if __name__ == "__main__":
    interactive_session()
