import socket
import time
import argparse
import struct
import logging

class MiSpeaker:
    def __init__(self, ip='192.168.1.45', port=54321):
        self.ip = ip
        self.port = port
        self.device_id = bytes.fromhex('08f83588')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5.0)
        self.counter = 1
        
    def create_hello_packet(self):
        """Create a hello packet to try to get token"""
        magic = b'\x21\x31'  # Magic number for the protocol
        packet_length = b'\x00\x20'  # 32 bytes length
        device_type = b'\xff\xff\xff\xff'  # Special type for token request
        stamp = b'\x00\x00\x00\x01'  # Initial handshake
        
        # Create the initial handshake packet
        packet = bytearray(magic + packet_length + device_type + self.device_id + stamp)
        packet.extend([0xff] * (32 - len(packet)))
        
        # Create the info request packet
        info_packet = bytearray(magic + packet_length + b'\x00\x00\x00\x02' + self.device_id + stamp)
        info_packet.extend([0x00] * (32 - len(info_packet)))
        
        return [bytes(packet), bytes(info_packet)]
    
    def analyze_response(self, data, verbose=False):
        """Analyze response data in detail"""
        if len(data) < 32:
            return None
        
        analysis = {
            'magic': data[0:2].hex(),
            'length': data[2:4].hex(),
            'device_type': data[4:8].hex(),
            'device_id': data[8:12].hex(),
            'stamp': data[12:16].hex(),
            'checksum': data[16:32].hex() if len(data) >= 32 else None
        }
        
        if verbose:
            print("\nResponse Analysis:")
            for key, value in analysis.items():
                print(f"  * {key}: {value}")
            
            # Look for potential token patterns
            if len(data) >= 32:
                # Check for token in different positions
                for i in range(0, len(data)-16):
                    chunk = data[i:i+16]
                    # Token usually has a good mix of values
                    if all(x != 0 and x != 0xff for x in chunk):
                        print(f"\nPotential token at position {i}: {chunk.hex()}")
                        
                # Check if this might be an info response
                if data[4:8] == b'\x00\x00\x00\x02':
                    print("\nThis appears to be an info response")
                    if len(data) > 32:
                        print(f"Extra data: {data[32:].hex()}")
        
        return analysis
    
    def try_get_token(self):
        """Attempt to get device token through direct communication"""
        print("\nAttempting to get device token...")
        
        packets = self.create_hello_packet()
        for i, packet in enumerate(packets):
            try:
                print(f"\nSending packet {i+1}: {packet.hex()}")
                self.sock.sendto(packet, (self.ip, self.port))
                
                # Try to receive multiple responses
                for _ in range(3):
                    try:
                        data, addr = self.sock.recvfrom(1024)
                        print(f"\nReceived from {addr}: {data.hex()}")
                        self.analyze_response(data, verbose=True)
                    except socket.timeout:
                        continue
                    
            except Exception as e:
                print(f"Error: {e}")
            
            time.sleep(1)  # Wait between packets
    
    def send_command(self, command=None, retries=3):
        """Send a command to the device with retries"""
        packet = self.create_hello_packet()[0]  # Use first packet type
        
        for attempt in range(retries):
            try:
                print(f"\nAttempt {attempt + 1}/{retries}:")
                print(f"Sending packet: {packet.hex()}")
                
                # Send packet
                self.sock.sendto(packet, (self.ip, self.port))
                
                # Wait for response
                data, addr = self.sock.recvfrom(1024)
                print(f"Received from {addr}: {data.hex()}")
                
                # Parse response
                analysis = self.analyze_response(data, verbose=True)
                if analysis:
                    print(f"Response Device ID: {analysis['device_id']}")
                    print(f"Response Stamp: {analysis['stamp']}")
                    return data
                    
            except socket.timeout:
                print(f"Attempt {attempt + 1} timed out")
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {e}")
        
        print("All attempts failed")
        return None

def main():
    parser = argparse.ArgumentParser(description='Xiaomi Speaker Controller')
    parser.add_argument('--ip', default='192.168.1.45', help='Speaker IP address')
    parser.add_argument('--port', type=int, default=54321, help='Speaker port')
    parser.add_argument('--monitor', action='store_true', help='Monitor mode')
    parser.add_argument('--verbose', action='store_true', help='Show detailed communication data')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--get-token', action='store_true', help='Try to obtain device token')
    args = parser.parse_args()
    
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    speaker = MiSpeaker(args.ip, args.port)
    print(f"Starting communication with Mi Speaker at {args.ip}:{args.port}...")
    
    if args.get_token:
        speaker.try_get_token()
    else:
        while True:
            try:
                print("\nSending discovery packet...")
                response = speaker.send_command()
                if response:
                    print("\nSuccessful communication!")
                time.sleep(2)  # Wait before next attempt
                
            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Error: {e}")
                break

if __name__ == "__main__":
    main()