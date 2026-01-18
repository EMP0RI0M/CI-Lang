# FluxVM Architecture and Instruction Set Specification

## 1. Overview
FluxVM is a stack-based virtual machine designed to execute CI-Lang bytecode. It differs from traditional VMs by incorporating native support for entropy-driven probabilistic execution and runtime code adaptation.

## 2. Components
1. **Chaos Stack (CS)**: A secondary stack used for tracking probabilistic execution state and branch history.
2. **Entropy Register (ER)**: A 64-bit float register representing the current system disorder (0.0 to 1.0).
3. **Adaptive Dispatcher (AD)**: A runtime component that can dynamically swap implementation pointers for specialized instructions.
4. **Data Stack (DS)**: The primary stack for operand storage and manipulation.

## 3. Instruction Set Architecture (ISA)

### 3.1 Stack Operations
| Mnemonic | Opcode | Description |
|----------|--------|-------------|
| `PUSH`   | 0x01   | Push a constant to the Data Stack. |
| `POP`    | 0x02   | Pop a value from the Data Stack. |
| `DUP`    | 0x03   | Duplicate the top value of the Data Stack. |

### 3.2 Arithmetic & Logic
| Mnemonic | Opcode | Description |
|----------|--------|-------------|
| `ADD`    | 0x10   | Add top two values. |
| `SUB`    | 0x11   | Subtract top two values. |
| `MUL`    | 0x12   | Multiply top two values. |
| `DIV`    | 0x13   | Divide top two values. |
| `EQ`     | 0x14   | Check equality. |
| `AND`    | 0x15   | Logical AND. |

### 3.3 Chaos & Entropy
| Mnemonic    | Opcode | Description |
|-------------|--------|-------------|
| `CHAOS_EQ`  | 0x20   | Probabilistic equality (≈). Uses ER to determine match probability. |
| `GET_E`     | 0x21   | Push current Entropy Register value to DS. |
| `SET_E`     | 0x22   | Pop a value from DS and set it as the new ER. |
| `ENTROPIZE` | 0x23   | Apply entropy-based noise to the top DS value. |

### 3.4 Control Flow & Adaptation
| Mnemonic | Opcode | Description |
|----------|--------|-------------|
| `JMP`    | 0x30   | Unconditional jump. |
| `JMP_IF` | 0x31   | Jump if top DS value is true. |
| `ADAPT`  | 0x32   | Invoke the Adaptive Dispatcher to rewrite following instructions. |
| `CALL`   | 0x33   | Function call. |
| `RET`    | 0x34   | Return from function. |

## 4. Memory Model
FluxVM manages three primary memory regions:
1. **Instruction Space**: Read-only bytecode (except when AD is active).
2. **Data Space**: Global and local variables.
3. **Entropy Space**: Volatile region affected by the `ENTROPIZE` operation.

## 5. Execution Cycle
1. **Fetch**: Read next instruction from the PC.
2. **Dispatch**:AD checks if a mutation is required.
3. **Decode**: Resolve operands.
4. **Execute**: Perform operation on DS/CS.
5. **Entropy Update**: Occasionally jitter ER based on execution patterns.
