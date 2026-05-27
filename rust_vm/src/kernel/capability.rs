#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CapRight {
    ExecuteBasic,
    SemanticEscalation,
    SpawnAgent,
    ModifyEntropy,
}

#[derive(Debug, Clone)]
pub struct CapabilityToken {
    // Array of rights to avoid HashSet in no_std
    rights: [bool; 4], 
}

impl CapabilityToken {
    pub fn new(execute: bool, semantic: bool, spawn: bool, entropy: bool) -> Self {
        Self {
            rights: [execute, semantic, spawn, entropy],
        }
    }

    pub fn untrusted() -> Self {
        Self::new(true, false, false, false)
    }

    pub fn root() -> Self {
        Self::new(true, true, true, true)
    }

    pub fn has_right(&self, right: &CapRight) -> bool {
        match right {
            CapRight::ExecuteBasic => self.rights[0],
            CapRight::SemanticEscalation => self.rights[1],
            CapRight::SpawnAgent => self.rights[2],
            CapRight::ModifyEntropy => self.rights[3],
        }
    }
}
