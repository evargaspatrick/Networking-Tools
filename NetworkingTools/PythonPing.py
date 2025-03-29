# import socket
# import os
# import struct
# import time
# import select
# import sys

# ICMP_ECHO_REQUEST = 8  # ICMP type for Echo Request

# def checksum(source_string):
#     """Checksum function for verifying the integrity of the ICMP packet"""
#     count_to = (len(source_string) // 2) * 2
#     sum = 0
#     count = 0
#     while count < count_to:
#         this_val = (source_string[count + 1] << 8) + source_string[count]
#         sum = sum + this_val
#         sum = sum & 0xffffffff  # Keep it within 32 bits
#         count = count + 2

#     if count_to < len(source_string):
#         sum = sum + source_string[len(source_string) - 1]
#         sum = sum & 0xffffffff

#     sum = (sum >> 16) + (sum & 0xffff)
#     sum = sum + (sum >> 16)
#     answer = ~sum & 0xffff
#     answer = answer >> 8 | (answer << 8 & 0xff00)
#     return answer

# def create_packet(id):
#     """Create an ICMP Echo Request packet"""
#     header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, id, 1)
#     data = bytes(64 * "Q", "utf-8")
#     my_checksum = checksum(header + data)
#     if sys.platform == "darwin":
#         my_checksum = socket.htons(my_checksum) & 0xffff
#     else:
#         my_checksum = socket.htons(my_checksum)

#     header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, id, 1)
#     packet = header + data
#     return packet

# def receive_ping(sock, id, timeout):
#     """Receive an ICMP Echo Reply and calculate round trip time"""
#     time_left = timeout
#     while True:
#         start_select = time.time()
#         readable, _, _ = select.select([sock], [], [], time_left)
#         how_long_in_select = time.time() - start_select
#         if readable == []:  # Timeout
#             return None

#         time_received = time.time()
#         packet, addr = sock.recvfrom(1024)
#         icmp_header = packet[20:28]
#         type, code, checksum, packet_id, sequence = struct.unpack("bbHHh", icmp_header)
#         if packet_id == id:
#             bytes_in_double = struct.calcsize("d")
#             time_sent = struct.unpack("d", packet[28:28 + bytes_in_double])[0]
#             return time_received - time_sent

#         time_left -= how_long_in_select
#         if time_left <= 0:
#             return None

# def send_ping(dest_addr, timeout=1):
#     """Send an ICMP Echo Request and get the round trip time"""
#     icmp = socket.getprotobyname("icmp")
#     sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)
#     sock.settimeout(timeout)

#     my_id = os.getpid() & 0xFFFF
#     packet = create_packet(my_id)

#     try:
#         sock.sendto(packet, (dest_addr, 1))
#         delay = receive_ping(sock, my_id, timeout)
#     except socket.error as e:
#         print(f"Error sending ping: {e}")
#         return None
#     finally:
#         sock.close()

#     return delay

# def ping(host):
#     """Ping a host"""
#     try:
#         dest_addr = socket.gethostbyname(host)
#     except socket.gaierror as e:
#         print(f"Cannot resolve {host}: {e}")
#         return

#     print(f"Pinging {host} [{dest_addr}]")
#     while True:
#         delay = send_ping(dest_addr)
#         if delay is None:
#             print(f"Request timeout")
#         else:
#             print(f"Reply from {dest_addr}: time={delay * 1000:.4f}ms")
#         time.sleep(1)

# def main():
#     if len(sys.argv) < 2:
#         print("Usage: ping2 <hostname or IP address>")
#         sys.exit(1)
#     ping(sys.argv[1])

# if __name__ == "__main__":
#     main()
