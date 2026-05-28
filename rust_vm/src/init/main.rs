use bootloader_api::BootInfo;
use crate::drivers::display;
use crate::arch::x86_64::boot;
use crate::kernel::capability::CapabilityToken;
use crate::kernel::vm::Vm;
// Removed unused Instruction and Opcode imports
use crate::kernel_println;

pub fn kernel_main(boot_info: &'static mut BootInfo) -> ! {
    if let Some(framebuffer) = boot_info.framebuffer.as_mut() {
        let info = framebuffer.info();
        let buffer = framebuffer.buffer_mut();
        display::init(buffer, info);
    }
    
    kernel_println!("CI-Lang OS (Linux-style Directory Layout) Booting...");
    
    let phys_mem_offset = x86_64::VirtAddr::new(boot_info.physical_memory_offset.into_option().unwrap());
    let _mapper = unsafe { crate::mm::paging::init(phys_mem_offset) };
    let _frame_allocator = unsafe {
        crate::mm::paging::BootInfoFrameAllocator::init(&boot_info.memory_regions)
    };
    
    kernel_println!("Virtual Memory System (Paging) Initialized.");
    
    // Initialize the global static heap allocator
    crate::mm::allocator::init_heap(&crate::ALLOCATOR);
    
    // Initialize Hardware Abstraction Layer (GDT, IDT, PICs)
    crate::arch::init();
    kernel_println!("Hardware Abstraction Layer (HAL) Initialized.");
    
    kernel_println!("Scanning Hardware Bus...");
    crate::drivers::pci::enumerate_buses();
    
    kernel_println!("Initializing Network Subsystem...");
    crate::net::init();
    
    kernel_println!("Testing CPU Exception Handling (int3 Breakpoint)...");
    x86_64::instructions::interrupts::int3();
    
    kernel_println!("Testing Dynamic Memory Allocation...");
    let mut test_vec = alloc::vec::Vec::new();
    test_vec.push(42);
    kernel_println!("Successfully allocated Vec! First value: {}", test_vec[0]);
    
    let config = boot::BootConfig {
        max_memory_mb: 16,
        deterministic_seed: 42,
    };
    
    let _kernel = boot::boot_system(config);
    
    kernel_println!("Spawning Root VM Agent with CI-Lang compiler...");
    let root_caps = CapabilityToken::root();
    let mut vm_root = Vm::new(42, root_caps);
    
    // The raw string from 5_agent_homeostasis.ci
    let source_code = "
        agent Stabilizer:
            state:
                val = 50.0
            
            update(dt):
                let target = 100.0
                val = val → target
                push val
        
        spawn Stabilizer size = 50;
    ";
    
    kernel_println!("Compiling CI-Lang Source: \n{}", source_code);
    
    match crate::kernel::compiler::compile(source_code) {
        Ok(bytecode) => {
            kernel_println!("Compilation Successful! Loading bytecode into FluxVM...");
            vm_root.load_bytecode(bytecode);
        }
        Err(e) => {
            kernel_println!("Compilation Failed: {}", e);
        }
    }
    vm_root.start();
    
    // Add to Hypervisor for preemptive context switching
    crate::kernel::hypervisor::HYPERVISOR.lock().add_vm(vm_root);

    kernel_println!("Handing control to Hardware Interrupt Scheduler (RVirt)...");
    
    // Loop infinitely, letting the hardware timer trap and context-switch
    loop {
        x86_64::instructions::hlt();
    }
}
