import socket
import threading
import time
import datetime
from dnslib import DNSRecord, DNSQuestion, DNSHeader, RR, QTYPE, A
from collections import defaultdict

UPSTREAM_DNS = '8.8.8.8'
DNS_PORT = 53
TIMEOUT = 2

class DNSCache:
    """Thread-safe DNS cache with TTL support"""
    def __init__(self):
        self.cache = {}  # key: (domain, qtype) -> (response, expiry_time)
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
    
    def get(self, domain, qtype):
        """Get cached response if not expired"""
        with self.lock:
            key = (domain, qtype)
            if key in self.cache:
                response, expiry = self.cache[key]
                if time.time() < expiry:
                    self.hits += 1
                    return response
                else:
                    del self.cache[key]
            self.misses += 1
            return None
    
    def set(self, domain, qtype, response, ttl=300):
        """Cache response with TTL (default 5 minutes)"""
        with self.lock:
            key = (domain, qtype)
            expiry = time.time() + min(ttl, 3600)  # Max 1 hour
            self.cache[key] = (response, expiry)
    
    def get_stats(self):
        """Get cache statistics"""
        with self.lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0
            return {
                'size': len(self.cache),
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate
            }

class DNSBlocklist:
    """Manage blocked and allowed domains"""
    def __init__(self):
        self.blocked_domains = set()
        self.allowed_domains = set()
        self.lock = threading.Lock()
        self.blocked_count = 0
        
    def add_blocked(self, domain):
        """Add domain to blocklist"""
        with self.lock:
            self.blocked_domains.add(domain.lower())
    
    def add_allowed(self, domain):
        """Add domain to allowlist"""
        with self.lock:
            self.allowed_domains.add(domain.lower())
    
    def remove_blocked(self, domain):
        """Remove from blocklist"""
        with self.lock:
            self.blocked_domains.discard(domain.lower())
    
    def remove_allowed(self, domain):
        """Remove from allowlist"""
        with self.lock:
            self.allowed_domains.discard(domain.lower())
    
    def is_blocked(self, domain):
        """Check if domain should be blocked"""
        domain_lower = domain.lower()
        with self.lock:
            # Check if explicitly allowed
            if domain_lower in self.allowed_domains:
                return False
            # Check if blocked
            if domain_lower in self.blocked_domains:
                return True
            # Check wildcard matches
            parts = domain_lower.split('.')
            for i in range(len(parts)):
                partial = '.'.join(parts[i:])
                if partial in self.blocked_domains:
                    return True
        return False
    
    def get_lists(self):
        """Get current blocked and allowed lists"""
        with self.lock:
            return list(self.blocked_domains), list(self.allowed_domains)
    
    def load_default_blocklist(self):
        """Load common ad/tracking domains (safe list - doesn't block useful sites)"""
        common_ads = [
            # Ad networks (safe to block)
            'doubleclick.net', 'googleadservices.com', 'googlesyndication.com',
            'google-analytics.com', 'googletagmanager.com',
            'scorecardresearch.com', 'taboola.com', 'outbrain.com',
            'advertising.com', 'adnxs.com', 'adsrvr.org',
            'criteo.com', 'pubmatic.com', 'rubiconproject.com',
            
            # Tracking (safe to block)
            'hotjar.com', 'mouseflow.com', 'crazyegg.com',
            'quantserve.com', 'optimizely.com',
            
            # Note: Facebook/Instagram/Gmail NOT blocked by default
            # Add them manually if you want to block social media
        ]
        for domain in common_ads:
            self.add_blocked(domain)

class AnomalyDetector:
    """Detect suspicious DNS patterns"""
    def __init__(self):
        self.ip_query_count = defaultdict(list)  # IP -> [timestamps]
        self.lock = threading.Lock()
        self.alerts = []
        
    def check_query(self, ip, domain, query_type):
        """Check for anomalies and return alert if found"""
        current_time = time.time()
        alert = None
        
        with self.lock:
            # Track queries per IP
            self.ip_query_count[ip].append(current_time)
            
            # Clean old entries (older than 1 minute)
            self.ip_query_count[ip] = [t for t in self.ip_query_count[ip] 
                                       if current_time - t < 60]
            
            # Check for excessive queries (>100 per minute)
            if len(self.ip_query_count[ip]) > 100:
                alert = {
                    'type': 'EXCESSIVE_QUERIES',
                    'severity': 'HIGH',
                    'ip': ip,
                    'count': len(self.ip_query_count[ip]),
                    'message': f'Excessive queries from {ip}: {len(self.ip_query_count[ip])} in 1 minute'
                }
                self.alerts.append(alert)
            
            # Check for suspicious domains
            suspicious_keywords = ['torrent', 'crack', 'keygen', 'malware', 'phishing']
            if any(kw in domain.lower() for kw in suspicious_keywords):
                alert = {
                    'type': 'SUSPICIOUS_DOMAIN',
                    'severity': 'MEDIUM',
                    'ip': ip,
                    'domain': domain,
                    'message': f'Suspicious domain queried: {domain} from {ip}'
                }
                self.alerts.append(alert)
            
            # Limit alert storage
            if len(self.alerts) > 100:
                self.alerts.pop(0)
        
        return alert
    
    def get_alerts(self):
        """Get recent alerts"""
        with self.lock:
            return list(self.alerts[-20:])  # Last 20 alerts

class DNSStats:
    """Thread-safe statistics tracking"""
    def __init__(self):
        self.lock = threading.Lock()
        self.total_queries = 0
        self.failed_queries = 0
        self.blocked_queries = 0
        self.cached_queries = 0
        self.response_times = []
        
    def add_query(self, success=True, blocked=False, cached=False, response_time=0):
        with self.lock:
            self.total_queries += 1
            if not success:
                self.failed_queries += 1
            if blocked:
                self.blocked_queries += 1
            if cached:
                self.cached_queries += 1
            if response_time > 0:
                self.response_times.append(response_time)
                if len(self.response_times) > 1000:
                    self.response_times.pop(0)
    
    def get_stats(self):
        with self.lock:
            avg_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            return {
                'total': self.total_queries,
                'failed': self.failed_queries,
                'blocked': self.blocked_queries,
                'cached': self.cached_queries,
                'avg_time': avg_time
            }

def create_blocked_response(request):
    """Create NXDOMAIN response for blocked domains"""
    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1, rcode=3), q=request.q)
    return reply.pack()

def handle_dns_request(data, addr, sock, log_queue, all_logs, stats_tracker, 
                       dns_cache, blocklist, anomaly_detector):
    """Handle individual DNS request with all features"""
    start_time = time.time()
    success = True
    blocked = False
    cached = False
    
    try:
        request = DNSRecord.parse(data)
        query_name = str(request.q.qname).rstrip('.')
        query_type = QTYPE.get(request.q.qtype, 'UNKNOWN')
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Check for anomalies
        alert = anomaly_detector.check_query(addr[0], query_name, query_type)
        if alert:
            log_queue.put(('ALERT', alert))
        
        # Check blocklist
        if blocklist.is_blocked(query_name):
            blocked = True
            response = create_blocked_response(request)
            sock.sendto(response, addr)
            details = '🚫 BLOCKED'
            response_time = (time.time() - start_time) * 1000
        else:
            # Check cache first
            cached_response = dns_cache.get(query_name, query_type)
            
            if cached_response:
                cached = True
                sock.sendto(cached_response, addr)
                response_time = (time.time() - start_time) * 1000
                details = f'💾 CACHED ({response_time:.1f}ms)'
            else:
                # Forward to upstream
                upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                upstream_sock.settimeout(TIMEOUT)
                
                try:
                    upstream_sock.sendto(data, (UPSTREAM_DNS, DNS_PORT))
                    response, _ = upstream_sock.recvfrom(4096)
                    
                    # Cache the response
                    dns_cache.set(query_name, query_type, response)
                    
                    response_time = (time.time() - start_time) * 1000
                    details = f'✓ OK ({response_time:.1f}ms)'
                    sock.sendto(response, addr)
                    
                except socket.timeout:
                    success = False
                    details = '⏱ Timeout'
                    
                except Exception as e:
                    success = False
                    details = f'❌ Error: {str(e)[:20]}'
                    
                finally:
                    upstream_sock.close()
        
        # Log entry
        log_entry = (timestamp, addr[0], query_name, query_type, details, success, blocked, cached)
        log_queue.put(log_entry)
        
        with threading.Lock():
            all_logs.append(log_entry)
            if len(all_logs) > 10000:
                all_logs.pop(0)
        
        stats_tracker.add_query(success, blocked, cached, response_time if success or blocked else 0)
        
    except Exception as e:
        print(f"Error handling DNS request: {e}")
        stats_tracker.add_query(success=False)

def start_dns_server(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector):
    """Start DNS proxy server"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind(('0.0.0.0', DNS_PORT))
        print(f"✓ DNS Server running on port {DNS_PORT}")
        print(f"✓ Forwarding to {UPSTREAM_DNS}")
        print(f"✓ Cache enabled")
        print(f"✓ Blocklist enabled ({len(blocklist.blocked_domains)} domains)")
        print(f"✓ Anomaly detection active\n")
        
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                thread = threading.Thread(
                    target=handle_dns_request,
                    args=(data, addr, sock, log_queue, all_logs, stats_tracker,
                          dns_cache, blocklist, anomaly_detector),
                    daemon=True
                )
                thread.start()
                
            except Exception as e:
                print(f"Error receiving DNS request: {e}")
                continue
                
    except PermissionError:
        print("\n❌ Permission denied! Run as administrator/sudo")
        
    except OSError as e:
        print(f"\n❌ Cannot bind to port {DNS_PORT}: {e}")
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        
    finally:
        sock.close()