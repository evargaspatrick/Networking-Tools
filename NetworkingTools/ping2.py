import socket
import os
import struct
import time
import select
import sys
import argparse
import random

ICMP_ECHO_REQUEST = 8  # ICMP type for Echo Request

def checksum(source_string):
    """Checksum function for verifying the integrity of the ICMP packet"""
    count_to = (len(source_string) // 2) * 2
    sum = 0
    count = 0
    while count < count_to:
        this_val = (source_string[count + 1] << 8) + source_string[count]
        sum = sum + this_val
        sum = sum & 0xffffffff  # Keep it within 32 bits
        count = count + 2

    if count_to < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff

    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def create_packet(id):
    """Create an ICMP Echo Request packet"""
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, id, 1)
    data = bytes(64 * "Q", "utf-8")
    my_checksum = checksum(header + data)
    if sys.platform == "darwin":
        my_checksum = socket.htons(my_checksum) & 0xffff
    else:
        my_checksum = socket.htons(my_checksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, id, 1)
    packet = header + data
    return packet

def udp_server(host='127.0.0.1', port=12345):
    """
    Start a UDP server to demonstrate unreliability
    This simulates a server that:
    1. Sometimes doesn't respond (packet loss)
    2. Has variable response times (jitter)
    """
    print(f"Starting UDP server on {host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    
    try:
        while True:
            # Receive data from client
            data, addr = server_socket.recvfrom(1024)
            
            # Simulate packet loss (30% chance of not responding)
            if random.random() < 0.3:
                print(f"Simulating packet loss - not responding to {addr}")
                continue
            
            # Simulate variable RTT - wait between 0 and 500 ms
            delay = random.uniform(0, 0.5)
            print(f"Responding to {addr} after {delay:.3f}s delay")
            time.sleep(delay)
            
            # Send response back to client
            server_socket.sendto(data, addr)
    except KeyboardInterrupt:
        print("\nUDP server stopped")
    finally:
        server_socket.close()

def udp_client(host='127.0.0.1', port=12345, count=4):
    """
    Client to demonstrate UDP unreliability by sending pings to our UDP server
    """
    print(f"UDP ping to {host}:{port}")
    print("This demonstrates UDP's unreliable nature with simulated packet loss and variable RTT")
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1)  # 1 second timeout
    
    sent = 0
    received = 0
    times = []
    
    for i in range(count):
        sent += 1
        message = f"Ping {i+1} {time.time()}"
        start_time = time.time()
        
        try:
            # Send the message
            client_socket.sendto(message.encode(), (host, port))
            
            # Wait for a response
            data, server = client_socket.recvfrom(1024)
            end_time = time.time()
            
            # Calculate and print RTT
            rtt = (end_time - start_time) * 1000  # in ms
            times.append(rtt)
            received += 1
            print(f"Reply from {host}: seq={i+1} time={rtt:.2f}ms")
            
        except socket.timeout:
            print(f"Request timed out for seq={i+1}")
        
        # Wait a bit before next ping
        time.sleep(0.5)
    
    # Print statistics, similar to regular ping
    if received > 0:
        min_time = min(times)
        max_time = max(times)
        avg_time = sum(times) / len(times)
        print(f"\nUDP Ping statistics for {host}:")
        print(f"    Packets: Sent = {sent}, Received = {received}, Lost = {sent - received} ({(sent - received) * 100 / sent:.0f}% loss)")
        print(f"Approximate round trip times in milliseconds:")
        print(f"    Minimum = {min_time:.2f}ms, Maximum = {max_time:.2f}ms, Average = {avg_time:.2f}ms")
    else:
        print(f"\nUDP Ping statistics for {host}:")
        print(f"    Packets: Sent = {sent}, Received = {received}, Lost = {sent} (100% loss)")
    
    client_socket.close()

def udp_demo():
    """Run a UDP unreliability demonstration"""
    print("\n===== UDP Unreliability Demo =====")
    print("1. Start UDP Server (shows packet loss simulation)")
    print("2. Run UDP Client (sends pings to the server)")
    print("3. Back to main menu")
    print("================================")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == '1':
        print("\nStarting UDP server - simulates packet loss and variable RTT")
        print("First run this option, then in another terminal, run option 2 to see the client side")
        print("Press Ctrl+C to stop the server when done")
        try:
            udp_server()
        except Exception as e:
            print(f"Server error: {e}")
    elif choice == '2':
        print("\nRunning UDP client - sends pings to the UDP server")
        print("Make sure you've started the UDP server first (option 1) in another terminal")
        host = input("Enter server IP (default: 127.0.0.1): ") or "127.0.0.1"
        port = input("Enter server port (default: 12345): ") or "12345"
        try:
            udp_client(host, int(port))
        except Exception as e:
            print(f"Client error: {e}")
    elif choice == '3':
        return
    else:
        print("Invalid choice. Please select 1, 2, or 3.")

def tcp_ping(host, port=80, timeout=1):
    """Ping a host using TCP connection (no admin privileges required)"""
    start_time = time.time()
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        return time.time() - start_time
    except (socket.timeout, socket.error):
        return None

def icmp_ping(dest_addr, timeout=1):
    """Try to ping using ICMP (requires admin privileges)"""
    try:
        icmp = socket.getprotobyname("icmp")
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)
        sock.settimeout(timeout)

        my_id = os.getpid() & 0xFFFF
        packet = create_packet(my_id)

        try:
            sock.sendto(packet, (dest_addr, 1))
            start_time = time.time()
            
            time_left = timeout
            while True:
                started_select = time.time()
                readable, _, _ = select.select([sock], [], [], time_left)
                select_time = time.time() - started_select
                
                if not readable:  # Timeout
                    return None
                
                receive_time = time.time()
                packet, addr = sock.recvfrom(1024)
                icmp_header = packet[20:28]
                type, code, checksum, packet_id, sequence = struct.unpack("bbHHh", icmp_header)
                
                if packet_id == my_id:
                    return receive_time - start_time
                
                time_left -= select_time
                if time_left <= 0:
                    return None
                
        finally:
            sock.close()
    except socket.error:
        # Permission denied or other socket error - we'll try TCP instead
        return None

def ping_host(host, count=4, interval=1, port=80, force_tcp=False):
    """Ping a host using either ICMP (if admin) or TCP (if not)"""
    try:
        ip_address = socket.gethostbyname(host)
    except socket.gaierror as e:
        print(f"Cannot resolve {host}: {e}")
        return

    # Try ICMP first unless forced to use TCP
    if not force_tcp:
        delay = icmp_ping(ip_address)
        if delay is not None:
            print(f"Using ICMP ping (admin privileges detected)")
            use_icmp = True
        else:
            print(f"Using TCP ping (admin privileges not available)")
            use_icmp = False
    else:
        print(f"Using TCP ping (forced by user)")
        use_icmp = False
    
    sent = 0
    received = 0
    times = []
    
    print(f"Pinging {host} [{ip_address}]")
    
    for i in range(count):
        sent += 1
        if use_icmp:
            delay = icmp_ping(ip_address)
        else:
            delay = tcp_ping(ip_address, port)
            
        if delay is None:
            print(f"Request timed out.")
        else:
            received += 1
            times.append(delay * 1000)  # Convert to ms
            print(f"Reply from {ip_address}: time={delay * 1000:.2f}ms")
            
        if i < count - 1:
            time.sleep(interval)
            
    # Print statistics
    if received > 0:
        min_time = min(times)
        max_time = max(times)
        avg_time = sum(times) / len(times)
        print(f"\nPing statistics for {ip_address}:")
        print(f"    Packets: Sent = {sent}, Received = {received}, Lost = {sent - received} ({(sent - received) * 100 / sent:.0f}% loss)")
        print(f"Approximate round trip times in milliseconds:")
        print(f"    Minimum = {min_time:.2f}ms, Maximum = {max_time:.2f}ms, Average = {avg_time:.2f}ms")

def show_options():
    """Display all available options for ping2 command"""
    print("\nUsage: ping2 [-t] [-a] [-n count] [-l size]")
    print("            [-i interval] [-p port] [-c count] [-w timeout]")
    print("            target_name")
    print("\nOptions:")
    print("    -c, --count count     Number of echo requests to send.")
    print("    -i, --interval time   Interval between pings in seconds.")
    print("    -p, --port port       TCP port to use if TCP ping is required (default: 80).")
    print("    -t, --tcp             Force TCP ping even if admin privileges are available.")
    print("    -w, --timeout sec     Timeout in seconds to wait for each reply (default: 1).")
    print("\nAdvanced Features:")
    print("    * Automatic fallback to TCP ping when admin privileges aren't available")
    print("    * Detailed statistics (min/max/avg times)")
    print("    * Domain name resolution")
    print("\nExamples:")
    print("    ping2 google.com" + " ( # This will ping google.com 4 times)") 
    print("    ping2 8.8.8.8 -c 10 -i 0.5" + " ( # This will limit the number of pings to 10 and set the interval to 0.5 seconds)")
    print("    ping2 example.com -t -p 443" + " ( # This will force TCP ping on port 443)")
    print("\nNote: ICMP ping requires administrator privileges.")
    print("      Without admin privileges, TCP ping will be used automatically.")

def display_menu():
    """Display the menu options"""
    print("\n===== Python Ping Tool =====")
    print("1. Ping a target")
    print("2. Show options")
    print("3. UDP unreliability example")
    print("4. Exit")
    print("===========================")
    return input("Enter your choice (1-4): ")

def menu_interface():
    """Menu-driven interface for ping tool"""
    while True:
        choice = display_menu()
        
        if choice == '1':
            host = input("Enter hostname or IP address to ping: ")
            print("\n")
            ping_host(host)
        elif choice == '2':
            show_options()
        elif choice == '3':
            udp_demo()
        elif choice == '4':
            print("Exiting. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please select 1-4.")
        
        input("\nPress Enter to continue...")

def main():
    # Check if arguments were provided
    if len(sys.argv) > 1:
        # Run in command-line mode
        parser = argparse.ArgumentParser(description="Ping a host using ICMP or TCP")
        parser.add_argument("host", help="Host to ping")
        parser.add_argument("-c", "--count", type=int, default=4, help="Number of pings to send (default: 4)")
        parser.add_argument("-i", "--interval", type=float, default=1, help="Interval between pings in seconds (default: 1)")
        parser.add_argument("-p", "--port", type=int, default=80, help="TCP port to use if TCP ping is required (default: 80)")
        parser.add_argument("-t", "--tcp", action="store_true", help="Force TCP ping even if admin privileges are available")
        parser.add_argument("-u", "--udp-demo", action="store_true", help="Run the UDP unreliability demonstration")
        
        args = parser.parse_args()
        
        if args.udp_demo:
            udp_demo()
        else:
            ping_host(args.host, args.count, args.interval, args.port, args.tcp)
    else:
        # Run in menu mode
        try:
            menu_interface()
        except KeyboardInterrupt:
            print("\nExiting. Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    main()