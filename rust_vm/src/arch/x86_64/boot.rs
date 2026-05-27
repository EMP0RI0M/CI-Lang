use crate::kernel::scheduler::Scheduler;
use crate::kernel::orchestrator::SemanticOrchestrator;
use crate::kernel_println;

/// System boot configuration
pub struct BootConfig {
    pub max_memory_mb: usize,
    pub deterministic_seed: u64,
}

/// The initialized bare-metal context
pub struct KernelContext {
    pub scheduler: Scheduler,
    pub orchestrator: SemanticOrchestrator,
}

pub fn boot_system(config: BootConfig) -> KernelContext {
    kernel_println!("[BOOT] Initializing Microkernel Environment...");
    kernel_println!("[BOOT] Memory Bound: {} MB", config.max_memory_mb);
    kernel_println!("[BOOT] Entropy Seed: {}", config.deterministic_seed);
    
    let scheduler = Scheduler::new(config.deterministic_seed);
    let orchestrator = SemanticOrchestrator::new();
    
    kernel_println!("[BOOT] Transferring control to Scheduler.");
    KernelContext {
        scheduler,
        orchestrator,
    }
}
