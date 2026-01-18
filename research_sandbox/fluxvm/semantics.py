import numpy as np
from typing import Dict, List

class SemanticMapper:
    def __init__(self, vocab_size=2000, embedding_dim=300):
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        
        # Mock embeddings for prototype (normally you'd load pre-trained vectors)
        # Seeded for reproducibility
        np.random.seed(42)
        self.embeddings = np.random.normal(0, 0.1, (vocab_size, embedding_dim))
        
        self.word_to_id = {}
        self.id_to_word = {}

    def load_vocab(self, words: List[str]):
        """
        Spreads vocabulary across the agent space to reduce cross-talk.
        """
        step = self.vocab_size // (len(words) + 1)
        for i, word in enumerate(words):
            idx = (i + 1) * step
            self.word_to_id[word] = idx
            self.id_to_word[idx] = word

    def text_to_stimulus(self, text: str, cluster_size=5):
        """
        Converts text to stimulus by activating a neighborhood (cluster) 
        of agents for each word, allowing for inter-agent learning.
        """
        words = text.lower().split()
        stimulus = np.zeros(self.vocab_size)
        
        for word in words:
            if word in self.word_to_id:
                center_idx = self.word_to_id[word]
                # Activate a local cluster around the word index
                for i in range(-cluster_size // 2, cluster_size // 2 + 1):
                    idx = (center_idx + i) % self.vocab_size
                    # Falloff activation
                    activation = 1.0 / (abs(i) + 1)
                    stimulus[idx] = max(stimulus[idx], activation)
        
        return stimulus
