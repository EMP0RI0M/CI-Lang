#[derive(Debug, Clone, PartialEq)]
pub enum Opcode {
    Load(&'static str),
    Store(&'static str),
    Lit(f64),
    Print,
    Halt,
    Jmp(isize),
    JmpIf(isize),
    Add,
    Sub,
    Mul,
    Div,
    ChEq,
    Arrow,
    SetVolatility(&'static str),
    TrapSemantic(&'static str, usize),
    StabProbe(&'static str),
    CheckDiv,
    SpawnAgent(usize),
    ProcYield,
    EntropySample(&'static str),
    StallOnDiv(f64),
    AdaptGain(f64),
    NetSend(&'static str),
    NetRecv(&'static str),
    
    // Phase 1 Kernel OS Extensions
    SpawnProcess(&'static str, usize), // name, priority
    SetPriority(usize),
    SetEntropyBudget(f64),
    KillProcess(&'static str),
}

#[derive(Debug, Clone, PartialEq)]
pub struct Instruction {
    pub op: Opcode,
}

impl Instruction {
    pub fn new(op: Opcode) -> Self {
        Self { op }
    }
}
