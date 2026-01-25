# dns_server.py
import socket
import threading
from dnslib import DNSHeader, DNSRecord, QTYPE, DNSLabel, RR, A
import datetime

# Simple cache placeholder (to be expanded later)
dns_cache = {}
cache_hits = 0
cache_misses = 0

UPSTREAM_DNS = '8.8.8.8'
DNS_PORT = 53
SINKHOLE_IP = '0.0.0.0'

def is_domain_blocked(query_name, blocklist):
    query_name = query_name.rstrip('.')
    for blocked in blocklist:
        if query_name == blocked or query_name.endswith('.' + blocked):
            return True
    return False

def handle_dns_request(data, addr, sock, log_queue, all_logs, domain_blocklist, ip_blacklist):
    # Future cache check placeholder
    global cache_hits, cache_misses
    if query_name in dns_cache:
        cache_hits += 1
    # sock.sendto(dns_cache[query_name], addr)  # Uncomment later
        details = 'Cached (placeholder)'
    else:
        cache_misses += 1
    try:
        request = DNSRecord.parse(data)
        query_name = str(request.q.qname).rstrip('.')
        query_type = QTYPE.get(request.q.qtype, 'UNKNOWN')
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        src_ip = addr[0]
        status = 'safe'
        details = f'Forwarded to {UPSTREAM_DNS}'

        if src_ip in ip_blacklist:
            status = 'blocked_ip'
            details = 'Blocked: IP blacklisted'
            reply = request.reply()
            reply.header.rcode = getattr(DNSHeader.RCODE, 'NXDOMAIN')
            sock.sendto(reply.pack(), addr)

        elif is_domain_blocked(query_name, domain_blocklist):
            status = 'blocked_domain'
            details = 'Blocked: Domain blacklisted'
            reply = request.reply()
            if request.q.qtype in (QTYPE.A, QTYPE.AAAA):
                reply.add_answer(RR(request.q.qname, request.q.qtype, rdata=A(SINKHOLE_IP)))
            else:
                reply.header.rcode = getattr(DNSHeader.RCODE, 'NXDOMAIN')
            sock.sendto(reply.pack(), addr)

        else:
        # Forward to upstream with timeout and 1 retry
            success = False
        for attempt in range(2):
            try:
                upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                upstream_sock.settimeout(2.0)  # 2-second timeout
                upstream_sock.sendto(data, (UPSTREAM_DNS, DNS_PORT))
                response, _ = upstream_sock.recvfrom(4096)
                upstream_sock.close()
                sock.sendto(response, addr)
                success = True
                details = f'Forwarded (attempt {attempt+1})'
                break
            except socket.timeout:
                details = f'Timeout (attempt {attempt+1}/2)'
                print(f"Timeout from {src_ip}: {query_name}")
                if attempt == 1:
                    reply = request.reply()
                    reply.header.rcode = getattr(DNSHeader.RCODE, 'SERVFAIL')
                    sock.sendto(reply.pack(), addr)
                    details = 'Failed after retries'
            except Exception as e:
                details = f'Error: {str(e)[:30]}'
                print(f"Upstream error from {src_ip}: {query_name} - {e}")
                if attempt == 1:
                    reply = request.reply()
                    reply.header.rcode = getattr(DNSHeader.RCODE, 'SERVFAIL')
                    sock.sendto(reply.pack(), addr)
        if not success:
            status = 'failed'

        print(f"DNS Query from {src_ip}: {query_name} ({query_type}) - {details}")
        log_entry = (timestamp, src_ip, query_name, query_type, details, status)
        log_queue.put(log_entry)
        # Append log and auto-trim to prevent memory bloat
        all_logs.append(log_entry)
        if len(all_logs) > 5000:
            all_logs = all_logs[-5000:]  # Keep only the last 5000 entries
        
                # Log blocked queries to file
        if status in ['blocked_ip', 'blocked_domain']:
            with open("alerts.log", "a") as f:
                f.write(f"{timestamp} | BLOCKED | {src_ip} | {query_name} | {details}\n")    

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