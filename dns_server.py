import socket
import threading
from dnslib import DNSHeader, DNSRecord, QTYPE
import datetime

UPSTREAM_DNS = '8.8.8.8'  # Or '1.1.1.1'
DNS_PORT = 53

def handle_dns_request(data, addr, sock, log_queue, all_logs):
    try:
        request = DNSRecord.parse(data)
        query_name = str(request.q.qname).rstrip('.')  # e.g., 'example.com'
        query_type = QTYPE.get(request.q.qtype, 'UNKNOWN')  # e.g., 'A'
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        details = f'Forwarded to {UPSTREAM_DNS}'
        
        # Log to console for debugging
        print(f"DNS Query from {addr[0]}: {query_name} ({query_type})")
        
        # Put log into queue for GUI
        log_entry = (timestamp, addr[0], query_name, query_type, details)
        log_queue.put(log_entry)
        
        # Append to all_logs for stats
        all_logs.append(log_entry)
        
        # Forward to upstream
        upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        upstream_sock.sendto(data, (UPSTREAM_DNS, DNS_PORT))
        response, _ = upstream_sock.recvfrom(4096)
        upstream_sock.close()
        
        # Send response back
        sock.sendto(response, addr)
    except Exception as e:
        print(f"Error handling DNS: {e}")

def start_dns_server(log_queue, all_logs):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('0.0.0.0', DNS_PORT))
        print("DNS Proxy running on port 53...")
        while True:
            data, addr = sock.recvfrom(4096)
            threading.Thread(target=handle_dns_request, args=(data, addr, sock, log_queue, all_logs)).start()
    except PermissionError:
        print("Error: Run as admin/root to bind to port 53.")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        sock.close()