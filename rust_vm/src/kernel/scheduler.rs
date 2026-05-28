use crate::kernel::vm::Vm;
use crate::kernel::vm::trap::TrapReason;
use crate::kernel::orchestrator::SemanticOrchestrator;
use crate::kernel_println;

pub struct Scheduler {
    // Limited to 4 VMs for MVP to avoid dynamic allocation via Vec
    vms: [Option<Vm>; 4],
    seed: u64,
}

impl Scheduler {
    pub fn new(seed: u64) -> Self {
        Self {
            vms: [None, None, None, None],
            seed,
        }
    }

    pub fn add_vm(&mut self, vm: Vm) {
        for slot in self.vms.iter_mut() {
            if slot.is_none() {
                *slot = Some(vm);
                return;
            }
        }
        kernel_println!("[SCHEDULER] Error: VM Slots full!");
    }

    pub fn run_all(&mut self, orchestrator: &mut SemanticOrchestrator) -> Result<(), &'static str> {
        loop {
            let mut all_halted = true;
            for i in 0..4 {
                let mut trap_to_handle = None;
                if let Some(vm) = &mut self.vms[i] {
                    if !vm.is_running() { continue; }
                    all_halted = false;
                    
                    match vm.step() {
                        Ok(Some(trap)) => trap_to_handle = Some(trap),
                        Ok(None) => {}
                        Err(e) => return Err(e),
                    }
                }
                
                if let Some(trap) = trap_to_handle {
                    self.handle_trap(i, trap, orchestrator)?;
                }
                
                if let Some(vm) = &mut self.vms[i] {
                    if vm.is_running() {
                        vm.drift();
                        vm.maac.cool_down(); // Mathematically throttle and cool down the agent
                    }
                }
            }
            if all_halted { break; }
        }
        Ok(())
    }
    
    fn handle_trap(&mut self, vm_id: usize, trap: TrapReason, orchestrator: &mut SemanticOrchestrator) -> Result<(), &'static str> {
        match trap {
            TrapReason::SemanticRequest { operation } => {
                if let Some(vm) = &mut self.vms[vm_id] {
                    match orchestrator.handle_trap(vm_id, operation) {
                        Ok(Some(return_val)) => { vm.memory.push(return_val)?; }
                        Ok(None) => {}
                        Err(e) => {
                            kernel_println!("[TRAP] Orchestrator fault on VM {}: {}", vm_id, e);
                            vm.halt();
                        }
                    }
                }
            }
            TrapReason::CapabilityFault { message } => {
                kernel_println!("[TRAP] SECURITY FAULT on VM {}: {}", vm_id, message);
                if let Some(vm) = &mut self.vms[vm_id] { vm.halt(); }
            }
            TrapReason::Halt => {
                kernel_println!("[TRAP] VM {} halted gracefully.", vm_id);
            }
            TrapReason::EntropyThresholdReached { current_entropy } => {
                kernel_println!("[MAAC] VM {} execution blocked! Entropy ({}) > Threshold.", vm_id, current_entropy);
                // The VM is kept running, but its PC is frozen until maac.cool_down() drops the entropy.
            }
            _ => {}
        }
        Ok(())
    }
}
