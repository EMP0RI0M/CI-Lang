use smoltcp::iface::{InterfaceBuilder, NeighborCache};
use smoltcp::phy::{Loopback, Medium};
use smoltcp::wire::{EthernetAddress, IpCidr};
use alloc::vec;
use alloc::collections::BTreeMap;
use crate::kernel_println;
use smoltcp::socket::{SocketSet, TcpSocket, TcpSocketBuffer};
use smoltcp::time::Instant;

pub fn init() {
    kernel_println!("Initializing Virtual Loopback Network Interface...");
    
    // Create a loopback device
    let mut device = Loopback::new(Medium::Ethernet);
    
    // Set up network interface
    let hw_addr = EthernetAddress([0x02, 0x00, 0x00, 0x00, 0x00, 0x01]);
    let neighbor_cache = NeighborCache::new(BTreeMap::new());
    
    let mut iface = InterfaceBuilder::new()
        .hardware_addr(hw_addr.into())
        .neighbor_cache(neighbor_cache)
        .ip_addrs(vec![IpCidr::new(smoltcp::wire::IpAddress::v4(127, 0, 0, 1), 8)])
        .finalize(&mut device);
        
    // Set up a SocketSet
    let mut sockets = SocketSet::new(vec![]);
    
    let tcp_rx_buffer = TcpSocketBuffer::new(vec![0; 1024]);
    let tcp_tx_buffer = TcpSocketBuffer::new(vec![0; 1024]);
    let tcp_socket = TcpSocket::new(tcp_rx_buffer, tcp_tx_buffer);
    
    let _tcp_handle = sockets.add(tcp_socket);

    // Initial poll
    match iface.poll(&mut device, &mut sockets, Instant::from_millis(0)) {
        Ok(_) => kernel_println!("Loopback Interface Polled Successfully."),
        Err(e) => kernel_println!("Network Poll Error: {:?}", e),
    }

    kernel_println!("smoltcp Network Stack initialized internally.");
}
