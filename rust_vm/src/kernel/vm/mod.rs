pub mod instruction;
pub mod trap;
pub mod maac;

use crate::mm::Memory;
use crate::kernel::vm::instruction::{Instruction, Opcode};
use crate::kernel::vm::trap::TrapReason;
use crate::kernel::vm::maac::MaacController;
use crate::kernel::capability::{CapabilityToken, CapRight};
use alloc::vec::Vec;

pub struct Vm {
    pub memory: Memory,
    code: Vec<Instruction>,
    pc: usize,
    running: bool,
    pub entropy_register: f64,
    pub capabilities: CapabilityToken,
    pub maac: MaacController,
}

impl Vm {
    pub fn new(_seed: u64, capabilities: CapabilityToken) -> Self {
        Self {
            memory: Memory::new(),
            code: Vec::new(),
            pc: 0,
            running: false,
            entropy_register: 0.5,
            capabilities,
            maac: MaacController::new(0.8, 0.1), // tau = 0.8, cooling = 10%
        }
    }

    pub fn load_bytecode(&mut self, code: Vec<Instruction>) {
        self.code = code;
        self.pc = 0;
    }

    pub fn is_running(&self) -> bool {
        self.running
    }

    pub fn start(&mut self) {
        if !self.code.is_empty() {
            self.running = true;
        }
    }

    pub fn halt(&mut self) {
        self.running = false;
    }

    pub fn drift(&mut self) {
        if self.entropy_register <= 0.0 { return; }
        // For no_std MVP without external rand crate easily available,
        // we comment out drift physics here.
        /*
        for cell in self.memory.variables.values_mut() {
            if cell.volatility > 0.0 {
                let std_dev = cell.volatility * self.entropy_register;
                let normal = Normal::new(0.0, std_dev).unwrap();
                let noise = normal.sample(&mut self.rng);
                if let Value::Float(f) = cell.value {
                    cell.value = Value::Float(f + noise);
                }
            }
        }
        */
    }

    pub fn step(&mut self) -> Result<Option<TrapReason>, &str> {
        if !self.running || self.pc >= self.code.len() {
            self.running = false;
            return Ok(Some(TrapReason::Halt));
        }

        if !self.capabilities.has_right(&CapRight::ExecuteBasic) {
            self.running = false;
            return Ok(Some(TrapReason::CapabilityFault { message: "No ExecuteBasic right" }));
        }

        // MAAC Runtime Governance:
        // Evaluate the semantic stability of this agent before letting it execute.
        let current_divergence = self.maac.evaluate_entropy(&self.memory);
        if self.maac.is_diverging() {
            return Ok(Some(TrapReason::EntropyThresholdReached { current_entropy: current_divergence }));
        }

        let instr = self.code[self.pc].clone();
        self.pc += 1;
        self.execute_instruction(&instr)
    }

    fn execute_instruction(&mut self, instr: &Instruction) -> Result<Option<TrapReason>, &str> {
        // Implementation stripped to the core MVP to ensure no_std compilation
        match &instr.op {
            Opcode::Lit(val) => { self.memory.push(Value::Float(*val))?; }
            Opcode::Store(name) => {
                let val = self.memory.pop()?;
                self.memory.store(name, val);
            }
            Opcode::Load(name) => {
                if let Some(val) = self.memory.load(name) {
                    self.memory.push(val)?;
                } else {
                    return Err("Variable not found");
                }
            }
            Opcode::Add => {
                let b = self.memory.pop()?;
                let a = self.memory.pop()?;
                if let (Value::Float(x), Value::Float(y)) = (a, b) {
                    self.memory.push(Value::Float(x + y))?;
                }
            }
            Opcode::SpawnAgent(size) => {
                return Ok(Some(TrapReason::SpawnAgent(*size)));
            }
            Opcode::Sub => {
                let b = self.memory.pop()?;
                let a = self.memory.pop()?;
                if let (Value::Float(x), Value::Float(y)) = (a, b) {
                    self.memory.push(Value::Float(x - y))?;
                }
            }
            Opcode::Mul => {
                let b = self.memory.pop()?;
                let a = self.memory.pop()?;
                if let (Value::Float(x), Value::Float(y)) = (a, b) {
                    self.memory.push(Value::Float(x * y))?;
                }
            }
            Opcode::Div => {
                let b = self.memory.pop()?;
                let a = self.memory.pop()?;
                if let (Value::Float(x), Value::Float(y)) = (a, b) {
                    self.memory.push(Value::Float(x / y))?;
                }
            }
            Opcode::Halt => {
                self.running = false;
                return Ok(Some(TrapReason::Halt));
            }
            Opcode::TrapSemantic(op_name, arg_count) => {
                if !self.capabilities.has_right(&CapRight::SemanticEscalation) {
                    return Ok(Some(TrapReason::CapabilityFault { message: "No SemanticEscalation right" }));
                }
                
                return Ok(Some(TrapReason::SemanticRequest {
                    operation: op_name,
                }));
            }
            Opcode::CheckDiv => {
                let div = self.maac.evaluate_entropy(&self.memory);
                self.memory.push(Value::Float(div))?;
            }
            Opcode::StabProbe(target) => {
                // In full OS, this probes ANOTHER agent. 
                // For this MVP, we just probe a local variable's volatility.
                if let Some(val) = self.memory.load(target) {
                    if let Value::Float(f) = val {
                        self.memory.push(Value::Float(f.abs()))?;
                    }
                }
            }
            Opcode::ProcYield => {
                return Ok(Some(TrapReason::ProcYield));
            }
            Opcode::EntropySample(name) => {
                let div = self.maac.get_divergence();
                self.memory.store(name, Value::Float(div));
            }
            Opcode::StallOnDiv(threshold) => {
                let div = self.maac.get_divergence();
                if div > *threshold {
                    self.running = false;
                    return Ok(Some(TrapReason::StallOnDiv));
                }
            }
            Opcode::AdaptGain(gain) => {
                self.maac.cooling_rate = *gain;
            }
            _ => return Ok(None) // Ignoring other ops in this stub
        }
        Ok(None)
    }
}
