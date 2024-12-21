import socket
import time
import struct
import logging
import argparse
from datetime import datetime
import netifaces

class MiioDiscovery:
    def __init__(self, interface='0.0.0.0', port=54321):
        self.interface = interface
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(2.0)
        
    def create_discovery_packet(self):
        """Create a discovery packet"""
        # Magic + Length + Reserved
        packet = bytearray([
            0x21, 0x31,  # Magic
            0x00, 0x20,  # Length (32 bytes)
        ])
        packet.extend([0xff] * 28)  # Fill with 0xFF
        return bytes(packet)
    
    def discover(self, timeout=10):
        """Discover devices on the network"""
        print(f"Starting discovery (timeout: {timeout}s)...")
        
        # Focus on the known working interface
        target_interface = '192.168.1.5'
        target_device = '192.168.1.45'
        
        print(f"Using interface: {target_interface}")
        print(f"Target device: {target_device}")
        
        devices = {}
        
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(2.0)
            
            try:
                # Bind to the specific interface
                sock.bind((target_interface, 0))
                _, port = sock.getsockname()
                print(f"Bound to {target_interface}:{port}")
                
                # Create discovery packet
                packet = self.create_discovery_packet()
                
                start_time = time.time()
                while (time.time() - start_time) < timeout:
                    try:
                        # Try both broadcast and direct
                        print("\nSending discovery packets...")
                        sock.sendto(packet, ('255.255.255.255', self.port))
                        sock.sendto(packet, (target_device, self.port))
                        
                        # Try to receive multiple times
                        receive_until = time.time() + 2.0
                        while time.time() < receive_until:
                            try:
                                data, addr = sock.recvfrom(1024)
                                print(f"Received response from {addr}")
                                
                                if len(data) >= 32:
                                    device_info = self.parse_response(data, addr)
                                    if device_info and self.is_valid_device(device_info):
                                        devices[addr[0]] = device_info
                                        print(f"\nFound device at {addr[0]}:")
                                        print(f"  * Device ID: {device_info['device_id']}")
                                        print(f"  * Device Type: {device_info['device_type']}")
                                        print(f"  * Response: {device_info['raw_response']}")
                                        
                                        if device_info['device_id'] == '08f83588':
                                            print("Found target device!")
                                            return devices
                                            
                            except socket.timeout:
                                continue
                                
                    except Exception as e:
                        print(f"Error during discovery: {e}")
                    
                    time.sleep(1)  # Wait before next attempt
                    
            finally:
                sock.close()
                
        except Exception as e:
            print(f"Error setting up socket: {e}")
        
        if not devices:
            print("No devices found")
        
        return devices
    
    def parse_response(self, data, addr):
        """Parse device response"""
        if len(data) < 32:
            return None
        
        try:
            # Extract basic information
            magic = data[0:2].hex()
            length = int.from_bytes(data[2:4], 'big')
            device_type = data[4:8].hex()
            device_id = data[8:12].hex()
            stamp = int.from_bytes(data[12:16], 'big')
            
            # Only accept valid magic number
            if magic != '2131':
                return None
            
            device_info = {
                'ip': addr[0],
                'port': addr[1],
                'magic': magic,
                'length': length,
                'device_type': device_type,
                'device_id': device_id,
                'stamp': stamp,
                'raw_response': data.hex()
            }
            
            return device_info
            
        except Exception as e:
            print(f"Error parsing response from {addr}: {e}")
            return None
    
    def is_valid_device(self, device_info):
        """Check if the device response is valid"""
        # Ignore responses with all 0xFF
        if device_info['device_id'] == 'ffffffff':
            return False
        
        # Ignore responses with all 0x00
        if device_info['device_id'] == '00000000':
            return False
        
        # Check for known device ID
        if device_info['device_id'] == '08f83588':  # Our known device ID
            return True
        
        return True  # Accept other potential devices
    
    def get_local_ips(self):
        """Get all local IP addresses"""
        ips = set(['0.0.0.0'])  # Always include default
        
        try:
            # Try using netifaces
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        if 'addr' in addr:
                            ips.add(addr['addr'])
        except Exception as e:
            print(f"Error getting interfaces: {e}")
        
        # Add known good interfaces
        ips.update([
            '192.168.1.5',    # Your local IP
            '172.25.80.1'     # Another interface
        ])
        
        # Filter out localhost and invalid IPs
        return [ip for ip in ips if not ip.startswith('127.') and ip != '0.0.0.0']

def main():
    parser = argparse.ArgumentParser(description='Discover Xiaomi devices')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--timeout', type=int, default=10, help='Discovery timeout in seconds')
    parser.add_argument('--interface', default='0.0.0.0', help='Network interface to use')
    args = parser.parse_args()
    
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    discovery = MiioDiscovery(interface=args.interface)
    devices = discovery.discover(timeout=args.timeout)
    
    if not devices:
        print("No devices found")
        return
    
    print("\nFound devices:")
    for ip, device in devices.items():
        print(f"\nDevice at {ip}:")
        print(f"  * Device ID: {device['device_id']}")
        print(f"  * Device Type: {device['device_type']}")
        print(f"  * Response: {device['raw_response']}")

if __name__ == "__main__":
    main()
