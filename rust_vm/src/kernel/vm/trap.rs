use crate::mm::Value;

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
}

pub struct HardwareContext {
    pub pc: usize,
}
