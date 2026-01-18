# Terminal Experiment Logs

This document contains the raw terminal output captures from the key successful experiments, serving as verification of the results.

## 1. The Learning Consensus Experiment
**Command**: `python research_sandbox/multi_agent_consensus.py`
**Objective**: Prove that the Judge learns to resolve conflict faster (Reduction in ticks).

```text
--- PROTOCOL: MULTI-AGENT CONSENSUS (TRIBE DYNAMICS) ---
>>> [INIT] Spawning 3 Swarms: Conservative (A), Radical (B), Judge (C)
>>> [INIT] Beginning Interaction Loop...

>>> [GOD MODE] Injecting CHAOS at Tick 200...
Tick 200 | Div: 31.623 | JudgeMem: 0.000 [HARMONY]
Tick 250 | Div: 52.008 | JudgeMem: 0.000 [HARMONY]
Tick 300 | Div: 0.769 | JudgeMem: 0.054 [CONFLICT]
Tick 350 | Div: 0.001 | JudgeMem: 0.154 [CONFLICT]
...
>>> [JUDGE] Conflict Resolved in 49 ticks. Memory updated to 0.248

>>> [GOD MODE] Injecting CHAOS at Tick 600...
Tick 600 | Div: 31.623 | JudgeMem: 0.654 [CONFLICT]
>>> [JUDGE] Conflict Resolved in 1 ticks. Memory updated to 0.656

--- LEARNING RESULTS ---
Conflict 1 Duration: 49
Conflict Last Duration: 1
>>> SUCCESS: System learned to resolve conflict faster! (Learning Verified)
--- EXPERIMENT COMPLETE ---
```

## 2. The Semantic Council Experiment (LLM Governance)
**Command**: `python research_sandbox/semantic_consensus.py`
**Objective**: Prove that the system can consult an LLM for governance decisions.

```text
--- PROTOCOL: SEMANTIC CONSENSUS (LLM GOVERNANCE) ---
>>> [INIT] Council Assembled. Waiting for conflict...
Tick 000 | Div: 0.000 | JudgeMem: 0.000 [HARMONY]

>>> [EVENT] Political Schism Injected at Tick 150...
Tick 150 | Div: 31.623 | JudgeMem: 0.000 [HARMONY]
Tick 200 | Div: 49.484 | JudgeMem: 0.000 [HARMONY]

>>> [JUDGE] Conflict Detected (Div: 14.53). Consulting Mimo...
>>> [MIMO VERDICT] Action: ALLOW | Reason: Low divergence with no history, exploration is safe.

Tick 300 | Div: 4.232 | JudgeMem: 0.000 [CONFLICT]
...
--- COUNCIL ADJOURNED ---
```

## 3. How to Run
To reproduce these results inside the `research_sandbox`:

```bash
# 1. Compile the Core
# (Assuming main.ci exists)
python src/compiler.py research_sandbox/main.ci

# 2. Run Learning Experiment
python research_sandbox/multi_agent_consensus.py

# 3. Run Semantic Experiment (Requires API Key)
python research_sandbox/semantic_consensus.py
```
