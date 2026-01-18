# dns_server.py
import socket
import threading
from dnslib import DNSHeader, DNSRecord, QTYPE, DNSLabel, RR, A
import datetime

UPSTREAM_DNS = '8.8.8.8'  # Or '1.1.1.1'
DNS_PORT = 53
SINKHOLE_IP = '0.0.0.0'  # Or use '127.0.0.1' for local sinkhole

def is_domain_blocked(query_name, blocklist):
    # Check exact match or subdomain (*.example.com style, but simple check)
    query_name = query_name.rstrip('.')
    for blocked in blocklist:
        if query_name == blocked or query_name.endswith('.' + blocked):
            return True
    return False

def handle_dns_request(data, addr, sock, log_queue, all_logs, domain_blocklist, ip_blacklist):
    try:
        request = DNSRecord.parse(data)
        query_name = str(request.q.qname).rstrip('.')  # e.g., 'example.com'
        query_type = QTYPE.get(request.q.qtype, 'UNKNOWN')  # e.g., 'A'
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        src_ip = addr[0]
        status = 'safe'  # Default
        details = f'Forwarded to {UPSTREAM_DNS}'
        
        if src_ip in ip_blacklist:
            status = 'blocked_ip'
            details = 'Blocked: IP blacklisted'
            # Create NXDOMAIN response
            reply = request.reply()
            reply.header.rcode = getattr(DNSHeader.RCODE, 'NXDOMAIN')
            sock.sendto(reply.pack(), addr)
        elif is_domain_blocked(query_name, domain_blocklist):
            status = 'blocked_domain'
            details = 'Blocked: Domain blacklisted'
            # Sinkhole response (return sinkhole IP for A/AAAA queries)
            reply = request.reply()
            if request.q.qtype in (QTYPE.A, QTYPE.AAAA):
                reply.add_answer(RR(request.q.qname, request.q.qtype, rdata=A(SINKHOLE_IP)))
            else:
                reply.header.rcode = getattr(DNSHeader.RCODE, 'NXDOMAIN')
            sock.sendto(reply.pack(), addr)
        else:
            # Forward to upstream
            upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            upstream_sock.sendto(data, (UPSTREAM_DNS, DNS_PORT))
            response, _ = upstream_sock.recvfrom(4096)
            upstream_sock.close()
            sock.sendto(response, addr)
        
        # Log to console for debugging
        print(f"DNS Query from {src_ip}: {query_name} ({query_type}) - {details}")
        
        # Put log into queue for GUI (add status for coloring)
        log_entry = (timestamp, src_ip, query_name, query_type, details, status)
        log_queue.put(log_entry)
        
        # Append to all_logs for stats
        all_logs.append(log_entry)
    except Exception as e:
        print(f"Error handling DNS: {e}")

def start_dns_server(log_queue, all_logs, domain_blocklist, ip_blacklist):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('0.0.0.0', DNS_PORT))
        print("DNS Proxy running on port 53...")
        while True:
            data, addr = sock.recvfrom(4096)
            threading.Thread(target=handle_dns_request, args=(data, addr, sock, log_queue, all_logs, domain_blocklist, ip_blacklist)).start()
    except PermissionError:
        print("Error: Run as admin/root to bind to port 53.")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        sock.close()