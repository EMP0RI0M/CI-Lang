# FluxOS Architecture Overview

## The Cognitive Execution Substrate

FluxOS is a pure-Rust, bare-metal microkernel designed as a **cognitive execution substrate**. Unlike traditional POSIX systems where processes are just linear blocks of code, FluxOS treats execution stability and semantic coherence as the core primitives of the operating system.

### The Stack

| Layer                   | Technology      | Purpose |
|-------------------------|-----------------|---------|
| **Bootloader**          | Rust (`bootloader-main`) | Hardware initialization and memory map ingestion |
| **Microkernel**         | Rust (`#![no_std]`) | GDT, IDT, PIC Initialization, Physical Page Management |
| **Cognitive Hypervisor**| Rust (`hypervisor.rs`) | Context switching, hardware preemption |
| **FluxVM Core**         | Rust (`vm/`) | The bytecode runtime, deterministic sandbox |
| **MAAC Governor**       | Rust (`maac.rs`) | Real-time memory variance calculation ($D(t)$) |
| **CI-Lang Compiler**    | Rust (`compiler/`) | JIT compilation of CI-Lang text into FluxVM bytecode |

## Memory & Execution Isolation

1. **Virtual Memory Paging (`paging.rs`)**: 
   FluxOS uses the x86_64 `OffsetPageTable`. Agents do not share a global heap. When an agent is spawned via `spawn Stabilizer size = 50;`, the kernel maps distinct physical frames to the agent's Capability Token.
2. **MAAC Entropy Traps (`trap.rs`)**: 
   The hypervisor strictly monitors agent volatility. If an agent hallucinates and exceeds the entropy threshold ($\tau = 0.8$), the hardware clock traps the agent (`TrapReason::EntropyThresholdReached`) and the scheduler drops its CPU ticks to cool it down.

## FluxVM Instruction Set Architecture (ISA)

The FluxVM ISA includes standard mathematical opcodes alongside OS-level cognitive primitives:
- `Opcode::ProcYield`: Voluntarily yield the CPU back to the Hypervisor.
- `Opcode::EntropySample`: Read the current $D(t)$ variance metric directly into agent memory.
- `Opcode::StallOnDiv`: Voluntarily sleep the agent if its divergence exceeds a specified parameter.
- `Opcode::AdaptGain(f64)`: Adjust the MAAC cooling rate dynamically from user-space.

## Subsystem Roadmap (Phases 2-4)

Because FluxOS is a `#![no_std]` Rust architecture, we will avoid integrating C-libraries via FFI. Instead, we will aggressively integrate pure-Rust components:
- **Networking**: `smoltcp` (Phase 2)
- **USB**: `usb-device` (Phase 2)
- **Graphics**: Custom `alloc`-based Wayland compositor written natively in CI-Lang (Phase 3)
