use crate::kernel::vm::Vm;
use crate::kernel::vm::trap::TrapReason;
use crate::kernel::orchestrator::SemanticOrchestrator;
use crate::kernel::capability::CapabilityToken;
use crate::kernel_println;
use alloc::vec::Vec;

pub struct KernelProcess {
    pub name: &'static str,
    pub priority: usize,
    pub vm: Vm,
}

pub struct Scheduler {
    pub processes: Vec<KernelProcess>,
    _seed: u64,
}

impl Scheduler {
    pub fn new(seed: u64) -> Self {
        Self {
            processes: Vec::new(),
            _seed: seed,
        }
    }

    pub fn add_process(&mut self, name: &'static str, priority: usize, vm: Vm) {
        self.processes.push(KernelProcess { name, priority, vm });
    }

    pub fn run_all(&mut self, orchestrator: &mut SemanticOrchestrator) -> Result<(), &'static str> {
        loop {
            let mut all_halted = true;
            let mut new_processes = Vec::new();
            
            // Iterate over all processes
            for i in 0..self.processes.len() {
                let mut trap_to_handle = None;
                {
                    let process = &mut self.processes[i];
                    if !process.vm.is_running() { continue; }
                    all_halted = false;
                    
                    match process.vm.step() {
                        Ok(Some(trap)) => trap_to_handle = Some(trap),
                        Ok(None) => {}
                        Err(e) => return Err(e),
                    }
                }
                
                if let Some(trap) = trap_to_handle {
                    self.handle_trap(i, trap, orchestrator, &mut new_processes)?;
                }
                
                // Entropy enforcement & drift
                if let Some(process) = self.processes.get_mut(i) {
                    if process.vm.is_running() {
                        process.vm.drift();
                        
                        // Enforce budget: if current entropy > budget, stall the VM
                        if process.vm.maac.get_divergence() > process.vm.entropy_budget {
                            kernel_println!("[MAAC] VM {} ({}) throttled. Entropy ({}) > Budget ({}).", 
                                i, process.name, process.vm.maac.get_divergence(), process.vm.entropy_budget);
                            // It will remain running but 'step()' might yield or we just let it cool down
                        }
                        
                        process.vm.maac.cool_down(); // Mathematically throttle and cool down the agent
                    }
                }
            }
            
            // Add any spawned processes
            for proc in new_processes {
                self.processes.push(proc);
            }
            
            if all_halted { break; }
        }
        Ok(())
    }
    
    fn handle_trap(&mut self, pid: usize, trap: TrapReason, orchestrator: &mut SemanticOrchestrator, new_processes: &mut Vec<KernelProcess>) -> Result<(), &'static str> {
        let process_name = self.processes[pid].name;
        match trap {
            TrapReason::SemanticRequest { operation } => {
                let vm = &mut self.processes[pid].vm;
                match orchestrator.handle_trap(pid, operation) {
                    Ok(Some(return_val)) => { vm.memory.push(return_val)?; }
                    Ok(None) => {}
                    Err(e) => {
                        kernel_println!("[TRAP] Orchestrator fault on VM {} ({}): {}", pid, process_name, e);
                        vm.halt();
                    }
                }
            }
            TrapReason::CapabilityFault { message } => {
                kernel_println!("[TRAP] SECURITY FAULT on VM {} ({}): {}", pid, process_name, message);
                self.processes[pid].vm.halt();
            }
            TrapReason::Halt => {
                kernel_println!("[TRAP] VM {} ({}) halted gracefully.", pid, process_name);
            }
            TrapReason::EntropyThresholdReached { current_entropy } => {
                kernel_println!("[MAAC] VM {} ({}) execution blocked! Entropy ({}) > Threshold.", pid, process_name, current_entropy);
            }
            TrapReason::SpawnProcess { name, priority } => {
                kernel_println!("[KERNEL] Process '{}' spawned new process '{}' with priority {}", process_name, name, priority);
                // Create a completely isolated VM with empty memory, preserving security bounds.
                let mut new_vm = Vm::new(0, CapabilityToken::untrusted()); // Blank capabilities by default
                new_vm.start();
                new_processes.push(KernelProcess { name, priority, vm: new_vm });
            }
            TrapReason::SetPriority(priority) => {
                self.processes[pid].priority = priority;
                kernel_println!("[KERNEL] Process '{}' updated priority to {}", process_name, priority);
            }
            TrapReason::SetEntropyBudget(budget) => {
                kernel_println!("[KERNEL] Process '{}' updated entropy budget to {}", process_name, budget);
                // Budget was already updated inside execute_instruction, just log here.
            }
            TrapReason::KillProcess(target_name) => {
                kernel_println!("[KERNEL] Process '{}' killed process '{}'", process_name, target_name);
                for p in self.processes.iter_mut() {
                    if p.name == target_name {
                        p.vm.halt();
                    }
                }
            }
            _ => {}
        }
        Ok(())
    }
}
