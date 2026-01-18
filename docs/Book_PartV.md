# PART V: FLUX-VM: THE CHAOS VIRTUAL MACHINE

## Chapter 14: Architecture Overview

### 14.1 VM Design Goals: Speed, Noise, and Scale
The **FluxVM** is not a general-purpose processor. It is a **High-Density Chaos Accelerator**. Its primary goals are:
1. **Parallel Execution**: Managing $10^5+$ agents simultaneously.
2. **Native Stochasticity**: Injecting noise at the hardware/opcode level with zero latency.
3. **Entropy Regulation**: Maintaining a global thermodynamic state as a first-class register.

### 14.2 The Tick Engine
The heart of the VM is the **Tick Engine**. It operates on a discrete-time basis, where every "Tick" represents a universal update of the world state. The engine is optimized for **Double-Buffering**: reading from the current state and writing to a "future" buffer to ensure perfect synchronicity across the parallel population.

### 14.3 Memory Layout: MemoryCell Arrays
Memory in FluxVM is not a flat array of bytes. It is an array of **MemoryCell** objects. 
- Each cell contains a floating-point `value` and a `volatility` float.
- This "fat memory" allows the VM to apply the **Drift Formula** to every cell during the Drift Phase without needing to re-fetch metadata.

### 14.4 The Scheduler: Cooperative Chaos
Instead of traditional preemptive multitasking, FluxVM uses a **Cooperative Swarm Scheduler**. Each agent update is a lightweight fiber. The scheduler groups agents into "Buckets" based on their topology (e.g., all agents in a specific grid row) to maximize cache locality and GPU vectorization.

---
## Chapter 15: Bytecode Specification

### 15.1 Registers and Stack
FluxVM 2.0 uses a hybrid architecture:
- **Value Stack**: For standard arithmetic and logic.
- **Chaos Registers**: Dedicated registers that hold the current entropy seed and local volatility.

### 15.2 Instruction Set (Minimal Subset)
- **PUSH_VOL / STORE_VOL**: Interacts with the volatility component of memory.
- **DRIFT**: Explicitly applies one step of the thermodynamic drift formula.
- **CHAOS_SAMPLE**: Pulls a value from the agent's current probability distribution.
- **COUPLE_FETCH**: Reads a neighbor's state through the adjacency matrix.

### 15.3 Examples of Bytecode
An agent's update of `s = s + noise(0.1)` compiles to:
```asm
LOAD_CELL s
PUSH_CONST 0.1
NOISE
ADD
STORE_CELL s
```

---
## Chapter 16: Runtime Internals

### 16.1 The Entropy Engine
The Entropy Engine is a high-performance statistics module. Every N ticks, it gathers a subset of agent states, computes a 100-bin histogram, and derives the Shannon Entropy. This value is then broadcast to the global `E` register.

### 16.2 The Noise Engine (Xorshift+ with Gaussian Mapping)
To avoid the overhead of standard RNGs, FluxVM uses a vectorized **Xorshift+** generator. It maps these uniform bits to a Gaussian distribution using a precomputed Look-Up Table (LUT), providing "free" thermodynamic noise for every agent update.

### 16.3 The Neighbor Graph (Adjacency Matrix)
Connectivity is stored in a CSR (Compressed Sparse Row) format. This allows for rapid iteration over an agent's neighbors, ensuring that `coupling_sum()` operations are memory-bandwidth limited rather than compute-bound.

---
> "The machine does not just think; it vibrates with the rhythm of the code." — The Founder
---
