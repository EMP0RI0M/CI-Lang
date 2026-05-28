

#[derive(Debug)]
pub enum TrapReason {
    SemanticRequest {
        operation: &'static str,
    },
    CapabilityFault {
        message: &'static str,
    },
    Yield,
    Halt,
    Fault(&'static str),
    EntropyThresholdReached {
        current_entropy: f64,
    },
    SpawnAgent(usize),
    ProcYield,
    StallOnDiv,
    
    // Phase 1 Kernel OS Extensions
    SpawnProcess { name: &'static str, priority: usize },
    SetPriority(usize),
    SetEntropyBudget(f64),
    KillProcess(&'static str),
}

pub struct HardwareContext {
    pub pc: usize,
}
