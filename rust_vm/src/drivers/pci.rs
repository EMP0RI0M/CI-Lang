use x86_64::instructions::port::Port;
use crate::kernel_println;

const PCI_CONFIG_ADDRESS: u16 = 0xCF8;
const PCI_CONFIG_DATA: u16 = 0xCFC;

pub fn pci_config_read_dword(bus: u8, slot: u8, func: u8, offset: u8) -> u32 {
    let address = ((bus as u32) << 16)
        | ((slot as u32) << 11)
        | ((func as u32) << 8)
        | (offset as u32 & 0xFC)
        | 0x80000000;

    unsafe {
        let mut addr_port = Port::new(PCI_CONFIG_ADDRESS);
        addr_port.write(address);

        let mut data_port = Port::<u32>::new(PCI_CONFIG_DATA);
        data_port.read()
    }
}

pub fn pci_config_write_dword(bus: u8, slot: u8, func: u8, offset: u8, value: u32) {
    let address = ((bus as u32) << 16)
        | ((slot as u32) << 11)
        | ((func as u32) << 8)
        | (offset as u32 & 0xFC)
        | 0x80000000;

    unsafe {
        let mut addr_port = Port::new(PCI_CONFIG_ADDRESS);
        addr_port.write(address);

        let mut data_port = Port::<u32>::new(PCI_CONFIG_DATA);
        data_port.write(value);
    }
}

pub fn pci_config_read_word(bus: u8, slot: u8, func: u8, offset: u8) -> u16 {
    let dword = pci_config_read_dword(bus, slot, func, offset);
    ((dword >> ((offset & 2) * 8)) & 0xFFFF) as u16
}

pub fn pci_enable_bus_mastering(bus: u8, slot: u8, func: u8) {
    // Command register is at offset 0x04 (low 16 bits of dword 0x04)
    let dword = pci_config_read_dword(bus, slot, func, 0x04);
    // Bit 2 is Bus Master, Bit 1 is Memory Space (for MMIO)
    let new_dword = dword | 0x0006;
    pci_config_write_dword(bus, slot, func, 0x04, new_dword);
}

pub fn pci_get_bar0(bus: u8, slot: u8, func: u8) -> u32 {
    // BAR0 is at offset 0x10
    let bar = pci_config_read_dword(bus, slot, func, 0x10);
    if bar & 1 == 0 {
        bar & 0xFFFFFFF0 // Memory space address
    } else {
        bar & 0xFFFFFFFC // I/O space address
    }
}

pub fn check_device(bus: u8, device: u8) {
    let vendor_id = pci_config_read_word(bus, device, 0, 0);
    if vendor_id == 0xFFFF {
        return; // Device doesn't exist
    }

    let device_id = pci_config_read_word(bus, device, 0, 2);
    
    // Read class and subclass
    let class_word = pci_config_read_word(bus, device, 0, 0x0A);
    let base_class = (class_word >> 8) as u8;
    
    kernel_println!("PCI Device Found - Bus: {}, Device: {}, Vendor: {:#06x}, DeviceID: {:#06x}, Class: {:#04x}", 
        bus, device, vendor_id, device_id, base_class);

    if base_class == 0x02 {
        kernel_println!("    -> Network Controller Detected!");
    } else if base_class == 0x0C {
        kernel_println!("    -> Serial Bus Controller Detected!");
    }
}

pub fn enumerate_buses() {
    kernel_println!("Scanning PCI Buses...");
    for bus in 0..=255 {
        for device in 0..32 {
            check_device(bus as u8, device as u8);
        }
    }
    kernel_println!("PCI Scan Complete.");
}

