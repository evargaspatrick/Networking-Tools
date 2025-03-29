# How to install

1. Download to your desired directoy
2. pip install -e .

# Requirements

1. Python 3.6 or higher
2. No additional packages required - uses Python standard library
3. Administrator privileges recommended for full functionality (but not required)

# How to run

1. Run 'ping2' in your cmd or run 'traceroute2' in your cmd

# Options for ping2
1. `-c, --count COUNT` - Number of echo requests to send (default: 4)
2. `-i, --interval TIME` - Interval between pings in seconds (default: 1)
3. `-p, --port PORT` - TCP port to use if TCP ping is required (default: 80)
4. `-t, --tcp` - Force TCP ping even if admin privileges are available
5. `-u, --udp-demo` - Run the UDP unreliability demonstration
6. Running without arguments shows an interactive menu interface

Examples:
- `ping2 google.com` - Ping google.com 4 times with default settings
- `ping2 8.8.8.8 -c 10 -i 0.5` - Send 10 pings with 0.5 second interval
- `ping2 example.com -t -p 443` - Force TCP ping on port 443
- `ping2 -u` - Run the UDP unreliability demonstration

Note: ICMP ping requires administrator privileges. Without admin privileges, TCP ping will be used automatically.

## Interactive Menu Options
When running ping2 without arguments, you'll see a menu with these options:
1. Ping a target - Standard ping functionality
2. Show options - Display all available command-line options
3. UDP unreliability example - Demonstrates UDP's packet loss and variable response times
4. Exit - Quit the program

# Options for traceroute2
1. `-m, --max-hops HOPS` - Maximum number of hops to search for target (default: 30)
2. `-w, --timeout SEC` - Wait timeout seconds for each reply (default: 1)
3. Running without arguments shows an interactive menu interface

Examples:
- `traceroute2 google.com` - Trace route to google.com with default settings
- `traceroute2 8.8.8.8 -m 15 -w 2` - Limit to 15 hops with 2 second timeout

Note: This tool uses your system's tracert/traceroute command when available or falls back to a TCP-based implementation when needed.

# Uninstall

1. pip uninstall network-tools