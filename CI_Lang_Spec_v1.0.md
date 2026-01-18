# CI-Lang Specification v1.0
**A Formal Grammar and Runtime Specification for the Chaos Programming Language**

## 1. Introduction
CI-Lang (Chaos Programming Language) is a next-generation, entropy-aware programming language designed to transcend the limitations of traditional imperative and functional paradigms. It integrates chaos theory, adaptive parsing, and a novel virtual machine (FluxVM).

## 2. Lexical Structure
CI-Lang uses **SentencePiece** for tokenization.

### 2.1 Tokens
- **Identifiers**: Unicode-aware names (e.g., `x`, `chaos_func`, `αβ`).
- **Literals**: `int`, `float`, `string` (`"..."`), `boolean` (`true`/`false`).
- **Operators**: 
    - Arithmetic: `+`, `-`, `*`, `/`, `%`, `**`
    - Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
    - Logical: `&&`, `||`, `!`
    - Chaos: `≈` (probabilistic equality), `→` (entropy flow)
- **Delimiters**: `( )`, `{ }`, `[ ]`, `⟨ ⟩` (chaos brackets).

## 3. Syntax (BNF)
The formal grammar is defined in `grammar/cilang.bnf`.

### 3.1 Program Structure
```bnf
<program>       ::= { <statement> | <chaos-directive> }*
<statement>     ::= <declaration> | <expression> | <control-flow> | <chaos-statement>
<declaration>   ::= "let" <identifier> [ ":" <type> ] "=" <expression> ";"
                   | "chaos" <identifier> "=" <chaos-expression> ";"
```

## 4. Semantics & FluxVM
CI-Lang executes on **FluxVM**, a stack-based virtual machine with:
1. **Chaos Stack**: Tracks probabilistic branches.
2. **Entropy Register**: Measure of disorder (0.0 to 1.0).
3. **Adaptive Dispatcher**: Dynamic bytecode rewriting.

### 4.1 Instruction Set (Partial)
- `PUSH <val>`: Push value to stack.
- `CHAOS`: Enter probabilistic branch.
- `ENTROPIZE`: Modify value based on entropy.
- `FLUX`: Adaptively rewrite next instruction.

## 5. Example Programs
See the `examples/` directory for validated code samples.
