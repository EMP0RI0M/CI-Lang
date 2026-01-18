import numpy as np
from typing import Dict

class TemplateDecoder:
    def __init__(self, vocab_mapper):
        self.vocab_mapper = vocab_mapper
        self.templates = {
            "cat": "The feline pattern is stabilized.",
            "dog": "Canine association detected.",
            "robot": "Mechanical intelligence is active.",
            "chaos": "Entropy is rising. Order is elusive.",
            "logic": "Syllogistic structures are forming.",
            "order": "The swarm is entering a low-entropy crystal state.",
            "hunts": "A predatory sequence is emerging.",
            "chases": "Kinetic pursuit in progress.",
            "watches": "Passive observation mode.",
            "seeks": "Goal-oriented search state.",
            "greets": "Proximity-based interaction.",
            "mouse": "Small-scale biological target.",
            "bone": "Resource-based semantic marker.",
            "man": "Humanoid presence identified.",
            "woman": "Humanoid presence identified.",
            "unknown": "I am sensing an emergent pattern I cannot yet name."
        }

    def decode(self, readout_vector: np.ndarray):
        """
        Interprets swarm activation. Uses a soft-competition to find the word
        agent most likely represented.
        """
        # Filter for agents we actually have words for
        vocab_activations = {word: readout_vector[idx] for word, idx in self.vocab_mapper.word_to_id.items()}
        
        if not vocab_activations:
            return "No vocabulary loaded."
            
        # Find the winner among known words
        winner = max(vocab_activations.items(), key=lambda x: x[1])
        
        if winner[1] < 0.2:
            return "Swarm state is in a low-information 'Resting' state."
            
        return self.templates.get(winner[0], f"Emergent concept: '{winner[0]}'.")
