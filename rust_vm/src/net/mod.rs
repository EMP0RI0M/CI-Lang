use smoltcp::iface::{Config, Interface, SocketSet};
use smoltcp::phy::{Loopback, Medium};
use smoltcp::wire::{EthernetAddress, HardwareAddress, IpCidr};
use alloc::vec;
use crate::kernel_println;
use crate::drivers::pci;
use crate::drivers::e1000::E1000Device;
use smoltcp::socket::tcp::{Socket as TcpSocket, SocketBuffer as TcpSocketBuffer};
use smoltcp::time::Instant;

fn find_e1000() -> Option<(u8, u8, u8)> {
    for bus in 0..=10 { // Scan the first few buses to find the device quickly
        for device in 0..32 {
            let vendor_id = pci::pci_config_read_word(bus as u8, device as u8, 0, 0);
            if vendor_id == 0x8086 {
                let device_id = pci::pci_config_read_word(bus as u8, device as u8, 0, 2);
                if device_id == 0x100E || device_id == 0x100e {
                    return Some((bus as u8, device as u8, 0));
                }
            }
        }
    }
    None
}

pub fn init() {
    // Attempt to locate E1000 on the PCI bus
    if let Some((bus, slot, func)) = find_e1000() {
        kernel_println!("Located Intel E1000 Network Card at PCI [{}:{}:{}]. Initializing...", bus, slot, func);
        if let Some(mut e1000_dev) = E1000Device::new(bus, slot, func) {
            let mac = e1000_dev.mac_address();
            kernel_println!("E1000 driver bound. MAC address: {:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}",
                mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
            
            let hw_addr = EthernetAddress(mac);
            let config = Config::new(HardwareAddress::Ethernet(hw_addr));
            
            let mut iface = Interface::new(config, &mut e1000_dev, Instant::from_millis(0));
            iface.update_ip_addrs(|ip_addrs| {
                let cidr = IpCidr::new(smoltcp::wire::IpAddress::v4(192, 168, 1, 100), 24);
                ip_addrs.push(cidr).unwrap();
            });
                
            let mut sockets = SocketSet::new(vec![]);
            let tcp_rx_buffer = TcpSocketBuffer::new(vec![0; 1024]);
            let tcp_tx_buffer = TcpSocketBuffer::new(vec![0; 1024]);
            let tcp_socket = TcpSocket::new(tcp_rx_buffer, tcp_tx_buffer);
            
            let _tcp_handle = sockets.add(tcp_socket);
            
            iface.poll(Instant::from_millis(0), &mut e1000_dev, &mut sockets);
            
            kernel_println!("smoltcp network stack successfully bound to physical E1000 hardware.");
            return;
        }
    }

    kernel_println!("No E1000 hardware detected. Falling back to Virtual Loopback Interface...");
    
    // Create a loopback device
    let mut device = Loopback::new(Medium::Ethernet);
    
    // Set up network interface
    let hw_addr = EthernetAddress([0x02, 0x00, 0x00, 0x00, 0x00, 0x01]);
    let config = Config::new(HardwareAddress::Ethernet(hw_addr));
    
    let mut iface = Interface::new(config, &mut device, Instant::from_millis(0));
    iface.update_ip_addrs(|ip_addrs| {
        let cidr = IpCidr::new(smoltcp::wire::IpAddress::v4(127, 0, 0, 1), 8);
        ip_addrs.push(cidr).unwrap();
    });
        
    // Set up a SocketSet
    let mut sockets = SocketSet::new(vec![]);
    
    let tcp_rx_buffer = TcpSocketBuffer::new(vec![0; 1024]);
    let tcp_tx_buffer = TcpSocketBuffer::new(vec![0; 1024]);
    let tcp_socket = TcpSocket::new(tcp_rx_buffer, tcp_tx_buffer);
    
    let _tcp_handle = sockets.add(tcp_socket);

    // Initial poll
    iface.poll(Instant::from_millis(0), &mut device, &mut sockets);

    kernel_println!("smoltcp Network Stack initialized internally.");
}


