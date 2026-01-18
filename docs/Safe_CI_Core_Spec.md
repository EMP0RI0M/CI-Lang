# Safe CI Core Spec: Semantic Emergence (Codename: Proto-L)

This document defines the high-level architecture and safety constraints for the Phase 14 English Learning Prototype.

## 1. Core Primitives
- **Activation**: Agents use a threshold + decay function (`A_t = decay * A_t-1 + sum(inputs)`).
- **Association (Hebbian)**: Links between co-active agents are strengthened: `W_ij += alpha * A_i * A_j`.
- **Repulsion/Decay**: Global weight decay and local inhibition to prevent saturate/clipping.
- **Volatility modulation**: The `EntropyController` continues to stabilize the "Edge of Chaos" by adjusting noise injection.

## 2. Shared+Specialist Architecture
- **Core Agents (Shared)**: Represent universal semantic primitives (e.g., temporal order, negation, intensity).
- **Word Agents (Specialist)**: Seeded with pre-trained embeddings (300-d Word2Vec/FastText).
- **Context Router**: A simple classifier (or top-k activation gating) to activate relevant pools.

## 3. Data Pipeline
- **Input**: Text -> Tokenizer -> Embeddings -> Agent Stimulation.
- **Readout**: Swarm State (A_vector) -> MLP/Template Mapper -> Text.

## 4. Safety Constraints
- **Air-Gapped Training**: No outbound network calls.
- **Bounded Volatility**: `volatility` clipped to `[0.01, 1.0]`.
- **Anomaly Monitor**: Automatic kill-switch if entropy crashes to 0 (collapse) or spikes to max (noise).
- **Immutable Logic**: Core update rules are read-only; only parameters are tunable.

## 5. Storage
- **persistent_state**: `agents.npy` (state vectors).
- **memory_vault**: Vector DB (FAISS/Annoy) for long-term pattern retrieval.
- **logs**: JSON metrics for entropy, sigma, and reward traces.
