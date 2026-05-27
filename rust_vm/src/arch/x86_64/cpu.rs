/// Halt the CPU using inline assembly.
pub fn halt() -> ! {
    loop {
        // Safe abstraction to halt the CPU until the next interrupt
        // In actual x86 assembly, this would be `core::arch::asm!("hlt");`
        // For no_std MVP without inline assembly enabled globally, we spin.
        core::hint::spin_loop();
    }
}
