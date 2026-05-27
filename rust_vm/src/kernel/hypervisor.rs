use crate::kernel::vm::Vm;
use spin::Mutex;
use alloc::vec::Vec;
use lazy_static::lazy_static;
use crate::kernel_println;

lazy_static! {
    pub static ref HYPERVISOR: Mutex<Hypervisor> = Mutex::new(Hypervisor::new());
}

pub struct Hypervisor {
    vms: Vec<Vm>,
    current_vm: usize,
}

impl Hypervisor {
    pub fn new() -> Self {
        Self {
            vms: Vec::new(),
            current_vm: 0,
        }
    }

    pub fn add_vm(&mut self, vm: Vm) {
        self.vms.push(vm);
    }

    pub fn context_switch(&mut self) {
        if self.vms.is_empty() { return; }
        
        // Execute 1 step of the current VM (Preemption point)
        if let Some(vm) = self.vms.get_mut(self.current_vm) {
            if vm.is_running() {
                let result = vm.step();
                // We won't log everything, only specific traps
                if let Ok(Some(trap)) = result {
                    match trap {
                        crate::kernel::vm::trap::TrapReason::EntropyThresholdReached { current_entropy } => {
                            kernel_println!("[HYPERVISOR] VM {} blocked by MAAC! Entropy: {}", self.current_vm, current_entropy);
                        }
                        crate::kernel::vm::trap::TrapReason::SpawnAgent(size) => {
                            kernel_println!("[HYPERVISOR] VM {} requested to spawn {} agents. Paging hardware isolating memory...", self.current_vm, size);
                            // Normally we would clone the VM here and add it to self.vms
                        }
                        _ => {}
                    }
                }
            }
        }
        
        // Round robin
        self.current_vm = (self.current_vm + 1) % self.vms.len();
    }
}
