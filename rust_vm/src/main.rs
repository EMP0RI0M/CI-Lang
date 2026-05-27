#![no_std]
#![no_main]
#![feature(abi_x86_interrupt)]

extern crate alloc;

// Export the OS modules
pub mod arch;
pub mod drivers;
pub mod init;
pub mod kernel;
pub mod mm;

use bootloader_api::entry_point;

#[global_allocator]
pub static ALLOCATOR: mm::allocator::Locked<mm::allocator::BumpAllocator> = mm::allocator::Locked::new(mm::allocator::BumpAllocator::empty());

// Route the bootloader entry point directly to init/main.rs
entry_point!(init::main::kernel_main);
