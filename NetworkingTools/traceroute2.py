import socket
import time
import sys
import argparse
import subprocess
import re
import platform

def is_admin():
    """Check if the script is running with admin privileges"""
    try:
        if platform.system() == 'Windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False

def traceroute_subprocess(destination, max_hops=30):
    """Use the system's traceroute/tracert command"""
    try:
        cmd = 'tracert' if platform.system() == 'Windows' else 'traceroute'
        args = [cmd, '-h', str(max_hops), destination]
        
        process = subprocess.Popen(
            args, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        return True
    except Exception as e:
        print(f"Error using system traceroute: {e}")
        return False

def tcp_traceroute(destination, max_hops=30, timeout=1, port=80):
    """Perform traceroute using TCP connections - works without admin privileges"""
    try:
        dest_ip = socket.gethostbyname(destination)
    except socket.gaierror:
        print(f"Cannot resolve {destination}: Unknown host")
        return False
    
    print(f"Tracing route to {destination} [{dest_ip}]")
    print(f"over a maximum of {max_hops} hops:\n")
    
    for ttl in range(1, max_hops + 1):
        # Try up to 3 times for each hop
        successes = []
        timeouts = 0
        
        for attempt in range(3):
            start_time = time.time()
            
            try:
                # Create TCP socket with the specified TTL
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
                s.settimeout(timeout)
                
                # Start connection attempt to destination
                err = s.connect_ex((dest_ip, port))
                end_time = time.time()
                
                # Calculate round-trip time
                rtt = (end_time - start_time) * 1000  # ms
                
                if err == 0:
                    # Connection succeeded - we've reached the destination
                    successes.append(rtt)
                    if attempt == 0:  # Only print on first success
                        print(f"{ttl:2d}  {rtt:.1f} ms  {dest_ip}  Destination reached")
                    if ttl == max_hops:
                        return True
                elif err == 10060:  # Timeout
                    timeouts += 1
                elif err == 10061:  # Connection refused - we've reached the destination but port is closed
                    successes.append(rtt)
                    if attempt == 0:  # Only print on first success
                        print(f"{ttl:2d}  {rtt:.1f} ms  {dest_ip}  Destination reached (port closed)")
                    return True
                elif err == 10064:  # Host unreachable
                    if attempt == 0:
                        print(f"{ttl:2d}  *  Host unreachable")
                    timeouts += 1
                else:
                    # For TTL exceeded errors, Windows doesn't tell us the IP that responded
                    # But if we got here, we at least know a router exists at this hop
                    if attempt == 0:
                        print(f"{ttl:2d}  {rtt:.1f} ms  (Intermediate hop)")
                    successes.append(rtt)
            except socket.timeout:
                timeouts += 1
            except socket.error as e:
                if "TTL expired" in str(e):
                    rtt = (time.time() - start_time) * 1000
                    successes.append(rtt)
                    if attempt == 0:
                        print(f"{ttl:2d}  {rtt:.1f} ms  (Intermediate hop)")
                else:
                    if attempt == 0:
                        print(f"{ttl:2d}  *  Error: {e}")
                    timeouts += 1
            finally:
                s.close()
            
            # Short delay between attempts
            if attempt < 2:
                time.sleep(0.2)
        
        # After all attempts
        if timeouts == 3:
            print(f"{ttl:2d}  *  *  *  Request timed out.")
        elif not successes and ttl == max_hops:
            print(f"Trace complete - maximum hops ({max_hops}) reached")
            return True
            
        # Small delay before next hop
        time.sleep(0.1)
    
    print(f"Trace complete - maximum hops ({max_hops}) reached")
    return True

def traceroute(destination, max_hops=30, timeout=1):
    """Select the best available traceroute method"""
    # Try to use the system's traceroute/tracert command first
    if traceroute_subprocess(destination, max_hops):
        return
    
    # Fall back to our TCP implementation if the system command fails
    print("\nSystem traceroute failed. Using TCP-based traceroute instead.\n")
    tcp_traceroute(destination, max_hops, timeout)

def show_options():
    """Display available options for traceroute2"""
    print("\nUsage: traceroute2 [-m max_hops] [-w timeout] target_name")
    print("\nOptions:")
    print("    -m, --max-hops       Maximum number of hops to search for target")
    print("    -w, --timeout        Wait timeout seconds for each reply")
    print("\nExamples:")
    print("    traceroute2 google.com")
    print("    traceroute2 8.8.8.8 -m 15 -w 2")
    print("\nNote: This tool uses your system's tracert/traceroute command when available")
    print("      or falls back to a TCP-based implementation when needed.")

def display_menu():
    """Display menu options"""
    print("\n===== Traceroute Tool =====")
    print("1. Trace route to a target")
    print("2. Show options")
    print("3. Exit")
    print("===========================")
    return input("Enter your choice (1-3): ")

def menu_interface():
    """Menu-driven interface for traceroute tool"""
    while True:
        choice = display_menu()
        
        if choice == '1':
            host = input("Enter hostname or IP address to trace: ")
            print("\n")
            traceroute(host)
        elif choice == '2':
            show_options()
        elif choice == '3':
            print("Exiting. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please select 1, 2, or 3.")
        
        input("\nPress Enter to continue...")

def main():
    # Check if arguments were provided
    if len(sys.argv) > 1:
        # Run in command-line mode
        parser = argparse.ArgumentParser(description="Trace the route to a host")
        parser.add_argument("host", help="Target hostname or IP address")
        parser.add_argument("-m", "--max-hops", type=int, default=30, 
                          help="Maximum number of hops (default: 30)")
        parser.add_argument("-w", "--timeout", type=float, default=1, 
                          help="Timeout in seconds for each reply (default: 1)")
        
        args = parser.parse_args()
        traceroute(args.host, args.max_hops, args.timeout)
    else:
        # Run in menu mode
        try:
            menu_interface()
        except KeyboardInterrupt:
            print("\nExiting. Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    main()