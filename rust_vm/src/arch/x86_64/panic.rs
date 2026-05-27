use core::panic::PanicInfo;
use crate::arch::cpu;

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    // We would use kernel_println! here, but panic handler must be extremely safe
    cpu::halt();
}
