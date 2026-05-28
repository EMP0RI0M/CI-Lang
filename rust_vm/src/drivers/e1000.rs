#![allow(dead_code)]
use alloc::vec::Vec;
use core::alloc::Layout;
use x86_64::VirtAddr;
use smoltcp::phy::{Device, DeviceCapabilities, RxToken, TxToken, ChecksumCapabilities, Medium};
use smoltcp::time::Instant;
use crate::kernel_println;
use crate::drivers::pci;
use crate::mm::paging::get_physical_memory_offset;

// E1000 Registers
const REG_CTRL: u32 = 0x0000;
const REG_STATUS: u32 = 0x0008;
const REG_EECD: u32 = 0x0010;
const REG_ICR: u32 = 0x00C0;
const REG_IMS: u32 = 0x00D0;
const REG_IMC: u32 = 0x00D8;
const REG_RCTL: u32 = 0x0100;
const REG_TCTL: u32 = 0x0400;
const REG_TIPG: u32 = 0x0410;
const REG_RDBAL: u32 = 0x2800;
const REG_RDBAH: u32 = 0x2804;
const REG_RDLEN: u32 = 0x2808;
const REG_RDH: u32 = 0x2810;
const REG_RDT: u32 = 0x2818;
const REG_TDBAL: u32 = 0x3800;
const REG_TDBAH: u32 = 0x3804;
const REG_TDLEN: u32 = 0x3808;
const REG_TDH: u32 = 0x3810;
const REG_TDT: u32 = 0x3818;
const REG_MTA: u32 = 0x5200; // Multicast Table Array (128 registers)
const REG_RAL: u32 = 0x5400; // Receive Address Low
const REG_RAH: u32 = 0x5404; // Receive Address High

// RCTL bits
const RCTL_EN: u32 = 1 << 1;
const RCTL_SBP: u32 = 1 << 2;
const RCTL_UPE: u32 = 1 << 3;
const RCTL_MPE: u32 = 1 << 4;
const RCTL_LPE: u32 = 1 << 5;
const RCTL_BAM: u32 = 1 << 15;
const RCTL_BSIZE_2048: u32 = 0 << 16;
const RCTL_SECRC: u32 = 1 << 26;

// TCTL bits
const TCTL_EN: u32 = 1 << 1;
const TCTL_PSP: u32 = 1 << 3;
const TCTL_CT_SHIFT: u32 = 4;
const TCTL_COLD_SHIFT: u32 = 12;

// E1000 Constants
const NUM_RX_DESC: usize = 128;
const NUM_TX_DESC: usize = 128;
const BUFFER_SIZE: usize = 2048;

#[repr(C, packed)]
#[derive(Clone, Copy, Default)]
pub struct RxDescriptor {
    pub addr: u64,
    pub length: u16,
    pub checksum: u16,
    pub status: u8,
    pub errors: u8,
    pub special: u16,
}

#[repr(C, packed)]
#[derive(Clone, Copy, Default)]
pub struct TxDescriptor {
    pub addr: u64,
    pub length: u16,
    pub cso: u8,
    pub cmd: u8,
    pub status: u8,
    pub css: u8,
    pub special: u16,
}

pub struct E1000Device {
    mmio_base: VirtAddr,
    mac_addr: [u8; 6],
    
    // DMA structures
    rx_ring: &'static mut [RxDescriptor],
    tx_ring: &'static mut [TxDescriptor],
    
    // Virtual buffers
    rx_buffers: Vec<*mut u8>,
    tx_buffers: Vec<*mut u8>,
    
    // Ring indices
    rx_cur: usize,
    tx_cur: usize,
}

unsafe impl Send for E1000Device {}
unsafe impl Sync for E1000Device {}

impl E1000Device {
    pub unsafe fn write_reg(&self, offset: u32, val: u32) {
        core::ptr::write_volatile((self.mmio_base.as_u64() + offset as u64) as *mut u32, val);
    }

    pub unsafe fn read_reg(&self, offset: u32) -> u32 {
        core::ptr::read_volatile((self.mmio_base.as_u64() + offset as u64) as *const u32)
    }

    pub fn new(bus: u8, slot: u8, func: u8) -> Option<Self> {
        let bar0_phys = pci::pci_get_bar0(bus, slot, func);
        if bar0_phys == 0 {
            return None;
        }

        pci::pci_enable_bus_mastering(bus, slot, func);

        let phys_offset = get_physical_memory_offset().as_u64();
        let mmio_base = VirtAddr::new(bar0_phys as u64 + phys_offset);

        kernel_println!("E1000 MMIO mapped at: {:?}", mmio_base);

        // Allocate RX and TX descriptors with 16-byte alignment as required by E1000
        let rx_ring_layout = Layout::from_size_align(core::mem::size_of::<RxDescriptor>() * NUM_RX_DESC, 4096).unwrap();
        let tx_ring_layout = Layout::from_size_align(core::mem::size_of::<TxDescriptor>() * NUM_TX_DESC, 4096).unwrap();

        let rx_ring_ptr = unsafe { alloc::alloc::alloc_zeroed(rx_ring_layout) as *mut RxDescriptor };
        let tx_ring_ptr = unsafe { alloc::alloc::alloc_zeroed(tx_ring_layout) as *mut TxDescriptor };

        let rx_ring = unsafe { core::slice::from_raw_parts_mut(rx_ring_ptr, NUM_RX_DESC) };
        let tx_ring = unsafe { core::slice::from_raw_parts_mut(tx_ring_ptr, NUM_TX_DESC) };

        let mut rx_buffers = Vec::with_capacity(NUM_RX_DESC);
        let mut tx_buffers = Vec::with_capacity(NUM_TX_DESC);

        for _ in 0..NUM_RX_DESC {
            let buf_layout = Layout::from_size_align(BUFFER_SIZE, 4096).unwrap();
            let buf_ptr = unsafe { alloc::alloc::alloc_zeroed(buf_layout) };
            rx_buffers.push(buf_ptr);
        }

        for _ in 0..NUM_TX_DESC {
            let buf_layout = Layout::from_size_align(BUFFER_SIZE, 4096).unwrap();
            let buf_ptr = unsafe { alloc::alloc::alloc_zeroed(buf_layout) };
            tx_buffers.push(buf_ptr);
        }

        let mut dev = Self {
            mmio_base,
            mac_addr: [0; 6],
            rx_ring,
            tx_ring,
            rx_buffers,
            tx_buffers,
            rx_cur: 0,
            tx_cur: 0,
        };

        unsafe { dev.init_hardware(); }

        Some(dev)
    }

    unsafe fn init_hardware(&mut self) {
        // 1. Read MAC address
        let mac_low = self.read_reg(REG_RAL);
        let mac_high = self.read_reg(REG_RAH);
        self.mac_addr[0] = (mac_low & 0xFF) as u8;
        self.mac_addr[1] = ((mac_low >> 8) & 0xFF) as u8;
        self.mac_addr[2] = ((mac_low >> 16) & 0xFF) as u8;
        self.mac_addr[3] = ((mac_low >> 24) & 0xFF) as u8;
        self.mac_addr[4] = (mac_high & 0xFF) as u8;
        self.mac_addr[5] = ((mac_high >> 8) & 0xFF) as u8;

        // If MAC address is 0 (QEMU sometimes has it unprogrammed or we need to read from EEPROM/reset), set a default
        if self.mac_addr.iter().all(|&x| x == 0) {
            self.mac_addr = [0x52, 0x54, 0x00, 0x12, 0x34, 0x56];
            self.write_reg(REG_RAL, 0x12005452);
            self.write_reg(REG_RAH, 0x80005634); // Bit 31 enables the filter
        }

        kernel_println!("E1000 Hardware MAC Address: {:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}",
            self.mac_addr[0], self.mac_addr[1], self.mac_addr[2],
            self.mac_addr[3], self.mac_addr[4], self.mac_addr[5]
        );

        // 2. Initialize Multicast Table Array to 0
        for i in 0..128 {
            self.write_reg(REG_MTA + (i * 4), 0);
        }

        // 3. Setup RX Descriptors
        let phys_offset = get_physical_memory_offset().as_u64();
        for i in 0..NUM_RX_DESC {
            let virtual_buf_addr = self.rx_buffers[i] as u64;
            let physical_buf_addr = virtual_buf_addr - phys_offset;
            self.rx_ring[i].addr = physical_buf_addr;
            self.rx_ring[i].status = 0;
        }

        let rx_ring_phys = (self.rx_ring.as_ptr() as u64) - phys_offset;
        self.write_reg(REG_RDBAL, (rx_ring_phys & 0xFFFFFFFF) as u32);
        self.write_reg(REG_RDBAH, (rx_ring_phys >> 32) as u32);
        self.write_reg(REG_RDLEN, (NUM_RX_DESC * core::mem::size_of::<RxDescriptor>()) as u32);
        self.write_reg(REG_RDH, 0);
        self.write_reg(REG_RDT, (NUM_RX_DESC - 1) as u32);

        // Enable receiver
        let rctl = RCTL_EN | RCTL_SBP | RCTL_UPE | RCTL_MPE | RCTL_BAM | RCTL_BSIZE_2048 | RCTL_SECRC;
        self.write_reg(REG_RCTL, rctl);

        // 4. Setup TX Descriptors
        for i in 0..NUM_TX_DESC {
            let virtual_buf_addr = self.tx_buffers[i] as u64;
            let physical_buf_addr = virtual_buf_addr - phys_offset;
            self.tx_ring[i].addr = physical_buf_addr;
            self.tx_ring[i].status = 0;
        }

        let tx_ring_phys = (self.tx_ring.as_ptr() as u64) - phys_offset;
        self.write_reg(REG_TDBAL, (tx_ring_phys & 0xFFFFFFFF) as u32);
        self.write_reg(REG_TDBAH, (tx_ring_phys >> 32) as u32);
        self.write_reg(REG_TDLEN, (NUM_TX_DESC * core::mem::size_of::<TxDescriptor>()) as u32);
        self.write_reg(REG_TDH, 0);
        self.write_reg(REG_TDT, 0);

        // Enable transmitter
        let tctl = TCTL_EN | TCTL_PSP | (15 << TCTL_CT_SHIFT) | (64 << TCTL_COLD_SHIFT);
        self.write_reg(REG_TCTL, tctl);

        // Transmit IPG (Inter Packet Gap)
        self.write_reg(REG_TIPG, 0x0060200A);

        // Disable interrupts for polling mode
        self.write_reg(REG_IMC, 0xFFFFFFFF);
    }

    pub fn mac_address(&self) -> [u8; 6] {
        self.mac_addr
    }
}

pub struct E1000RxToken {
    buffer: &'static mut [u8],
}

impl RxToken for E1000RxToken {
    fn consume<R, F>(self, f: F) -> R
    where
        F: FnOnce(&mut [u8]) -> R,
    {
        f(self.buffer)
    }
}

pub struct E1000TxToken<'a> {
    device: &'a mut E1000Device,
}

impl<'a> TxToken for E1000TxToken<'a> {
    fn consume<R, F>(self, len: usize, f: F) -> R
    where
        F: FnOnce(&mut [u8]) -> R,
    {
        let tx_index = self.device.tx_cur;
        let buf_ptr = self.device.tx_buffers[tx_index];
        let buf = unsafe { core::slice::from_raw_parts_mut(buf_ptr, len) };
        let result = f(buf);

        // Program transmit size and mark it for execution
        self.device.tx_ring[tx_index].length = len as u16;
        self.device.tx_ring[tx_index].cmd = 0x09; // RS (Report Status) | EOP (End of Packet)
        self.device.tx_ring[tx_index].status = 0;

        unsafe {
            let next_tx = (tx_index + 1) % NUM_TX_DESC;
            self.device.tx_cur = next_tx;
            self.device.write_reg(REG_TDT, next_tx as u32);

            // Wait for transmission to complete (polling status bit 0 DD)
            while (core::ptr::read_volatile(core::ptr::addr_of!(self.device.tx_ring[tx_index].status)) & 1) == 0 {
                core::hint::spin_loop();
            }
        }

        result
    }
}

impl Device for E1000Device {
    type RxToken<'a> = E1000RxToken where Self: 'a;
    type TxToken<'a> = E1000TxToken<'a> where Self: 'a;

    fn receive(&mut self, _timestamp: Instant) -> Option<(Self::RxToken<'_>, Self::TxToken<'_>)> {
        let rx_index = self.rx_cur;
        let status = unsafe { core::ptr::read_volatile(core::ptr::addr_of!(self.rx_ring[rx_index].status)) };


        if (status & 1) != 0 {
            // Packet is available (DD bit set)
            let length = self.rx_ring[rx_index].length as usize;
            let buf_ptr = self.rx_buffers[rx_index];
            let buffer = unsafe { core::slice::from_raw_parts_mut(buf_ptr, length) };

            // Return tokens and advance index
            self.rx_ring[rx_index].status = 0;
            let next_rx = (rx_index + 1) % NUM_RX_DESC;
            self.rx_cur = next_rx;
            unsafe { self.write_reg(REG_RDT, rx_index as u32); }

            Some((
                E1000RxToken { buffer },
                E1000TxToken { device: self }
            ))
        } else {
            None
        }
    }

    fn transmit(&mut self, _timestamp: Instant) -> Option<Self::TxToken<'_>> {
        Some(E1000TxToken { device: self })
    }

    fn capabilities(&self) -> DeviceCapabilities {
        let mut caps = DeviceCapabilities::default();
        caps.medium = Medium::Ethernet;
        caps.max_transmission_unit = 1500;
        caps.checksum = ChecksumCapabilities::default();
        caps
    }
}
