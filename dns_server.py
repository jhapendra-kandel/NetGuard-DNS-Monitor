"""
NetGuard DNS Server - Core DNS Proxy Implementation
Handles DNS query processing, caching, blocking, and anomaly detection

Author: Jhapendra Kandel
Project: 1st Year Python Programming
Institution: Softwarica College of IT & E-Commerce (Coventry University)
"""

import socket
import threading
import time
import datetime
import json
import os
from dnslib import DNSRecord, DNSQuestion, DNSHeader, RR, QTYPE, A
from collections import defaultdict

# DNS Server Configuration
UPSTREAM_DNS = '8.8.8.8'  # Google DNS
UPSTREAM_DNS_BACKUP = '1.1.1.1'  # Cloudflare DNS (fallback)
DNS_PORT = 53
TIMEOUT = 3  # Increased from 2 to 3 seconds for better reliability
MAX_RETRIES = 2  # Retry failed queries

# File paths for persistent storage
BLOCKLIST_FILE = 'blocklist.json'
ALLOWLIST_FILE = 'allowlist.json'


class DNSCache:
    """Thread-safe DNS cache with TTL support and statistics"""
    
    def __init__(self, max_size=10000):
        self.cache = {}  # key: (domain, qtype) -> (response, expiry_time)
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        self.max_size = max_size
        self.enabled = True  # Cache can be toggled on/off
        
    def get(self, domain, qtype):
        """Get cached response if not expired
        
        Args:
            domain (str): Domain name
            qtype (str): Query type (A, AAAA, etc.)
            
        Returns:
            bytes: Cached DNS response or None
        """
        # Return None if cache is disabled
        if not self.enabled:
            self.misses += 1
            return None
            
        with self.lock:
            key = (domain, qtype)
            if key in self.cache:
                response, expiry = self.cache[key]
                if time.time() < expiry:
                    self.hits += 1
                    return response
                else:
                    # Expired entry, remove it
                    del self.cache[key]
            self.misses += 1
            return None
    
    def set(self, domain, qtype, response, ttl=300):
        """Cache response with TTL
        
        Args:
            domain (str): Domain name
            qtype (str): Query type
            response (bytes): DNS response to cache
            ttl (int): Time to live in seconds (default 5 minutes)
        """
        # Don't cache if disabled
        if not self.enabled:
            return
            
        with self.lock:
            # If cache is full, remove oldest entry
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.items(), key=lambda x: x[1][1])[0]
                del self.cache[oldest_key]
            
            key = (domain, qtype)
            expiry = time.time() + min(ttl, 3600)  # Max 1 hour
            self.cache[key] = (response, expiry)
    
    def clear(self):
        """Clear all cached entries"""
        with self.lock:
            self.cache.clear()
            print("  Cache cleared")
    
    def get_stats(self):
        """Get cache statistics
        
        Returns:
            dict: Cache statistics (size, hits, misses, hit_rate)
        """
        with self.lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0
            return {
                'size': len(self.cache),
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'max_size': self.max_size
            }


class DNSBlocklist:
    """Manage blocked and allowed domains with persistence"""
    
    def __init__(self):
        self.blocked_domains = set()
        self.allowed_domains = set()
        self.lock = threading.Lock()
        self.blocked_count = 0
        
        # Load saved lists
        self._load_lists()
        
    def add_blocked(self, domain):
        """Add domain to blocklist"""
        with self.lock:
            self.blocked_domains.add(domain.lower().strip())
            self._save_lists()
    
    def add_allowed(self, domain):
        """Add domain to allowlist"""
        with self.lock:
            self.allowed_domains.add(domain.lower().strip())
            self._save_lists()
    
    def remove_blocked(self, domain):
        """Remove from blocklist"""
        with self.lock:
            self.blocked_domains.discard(domain.lower().strip())
            self._save_lists()
    
    def remove_allowed(self, domain):
        """Remove from allowlist"""
        with self.lock:
            self.allowed_domains.discard(domain.lower().strip())
            self._save_lists()
    
    def is_blocked(self, domain):
        """Check if domain should be blocked
        
        Algorithm:
        1. Check if in allowlist (if yes, allow)
        2. Check exact match in blocklist
        3. Check wildcard subdomain matches
        
        Args:
            domain (str): Domain to check
            
        Returns:
            bool: True if blocked, False otherwise
        """
        domain_lower = domain.lower().strip()
        
        with self.lock:
            # Check if explicitly allowed
            if domain_lower in self.allowed_domains:
                return False
            
            # Check exact match
            if domain_lower in self.blocked_domains:
                self.blocked_count += 1
                return True
            
            # Check wildcard matches (subdomains)
            parts = domain_lower.split('.')
            for i in range(len(parts)):
                partial = '.'.join(parts[i:])
                if partial in self.blocked_domains:
                    self.blocked_count += 1
                    return True
        
        return False
    
    def get_lists(self):
        """Get current blocked and allowed lists"""
        with self.lock:
            return list(self.blocked_domains), list(self.allowed_domains)
    
    def load_default_blocklist(self):
        """Load common ad/tracking domains"""
        common_ads = [
            # Ad networks
            'doubleclick.net', 'googleadservices.com', 'googlesyndication.com',
            'google-analytics.com', 'googletagmanager.com',
            'scorecardresearch.com', 'taboola.com', 'outbrain.com',
            'advertising.com', 'adnxs.com', 'adsrvr.org',
            'criteo.com', 'pubmatic.com', 'rubiconproject.com',
            
            # Tracking
            'hotjar.com', 'mouseflow.com', 'crazyegg.com',
            'quantserve.com', 'optimizely.com', 'mixpanel.com',
            
            # More ad networks
            'adserver.com', 'ads.yahoo.com', 'amazon-adsystem.com',
            'bing.com/ads', 'facebook.com/tr', 'twitter.com/i/adsct',
            
            # Extended tracking/ad domains (v2.2.0)
            'linkedin.com/analytics', 'branch.io', 'appsflyer.com',
            'adjust.com', 'adsystem.com', 'adroll.com', 'bidswitch.net',
            'demdex.net', 'omtrdc.net', 'everesttech.net', 'segment.com',
            'amplitude.com', 'heap.io', 'fullstory.com', 'loggly.com',
            
            # Additional ad networks
            'moatads.com', 'doubleverify.com', 'ias.com', 'integral-ad-science.com',
            'adform.net', 'casalemedia.com', 'openx.net', 'sharethrough.com',
            'triplelift.com', 'indexexchange.com', 'spotxchange.com', 'smartadserver.com',
            'yieldmo.com', 'sovrn.com', 'lijit.com', 'rhythmone.com',
            
            # Tracking pixels and analytics
            'pixel.facebook.com', 'pixel.ad', 'tracking.com', 'tr.snapchat.com',
            'analytics.tiktok.com', 'ads.tiktok.com', 'analytics.twitter.com',
            'ads.pinterest.com', 'analytics.pinterest.com', 'ads.reddit.com',
            'events.reddit.com', 'pixel.reddit.com', 'analytics.yahoo.com',
            
            # Mobile ad networks
            'admob.com', 'unity3d.com/ads', 'unityads.unity3d.com', 'vungle.com',
            'chartboost.com', 'ironsrc.com', 'ironsource.mobi', 'mopub.com',
            'inmobi.com', 'startapp.com', 'adcolony.com', 'fyber.com',
            
            # Data brokers and trackers
            'bluekai.com', 'exelator.com', 'acxiom.com', 'liveramp.com',
            'oracle.com/cx', 'tapad.com', 'drawbridge.com', 'crosswise.com',
            'lotame.com', 'neustar.biz', 'rlcdn.com', 'krxd.net',
            
            # Retargeting and remarketing
            'adsbygoogle.com', 'adskeeper.co.uk', 'revcontent.com', 'mgid.com',
            'contentad.net', 'adblade.com', 'zergnet.com', 'nativo.com',
        ]
        
        for domain in common_ads:
            self.add_blocked(domain)
        
        print(f"  Loaded {len(common_ads)} default blocked domains")
    
    def import_from_file(self, filename):
        """Import domains from text file (one per line)"""
        try:
            with open(filename, 'r') as f:
                count = 0
                for line in f:
                    domain = line.strip()
                    if domain and not domain.startswith('#'):
                        self.add_blocked(domain)
                        count += 1
                print(f"  Imported {count} domains from {filename}")
                return count
        except FileNotFoundError:
            print(f"  File not found: {filename}")
            return 0
        except Exception as e:
            print(f"  Error importing: {e}")
            return 0
    
    def import_from_url(self, url):
        """Import blocklist from URL (e.g., GitHub hosts file)
        
        Args:
            url (str): URL to blocklist file
            
        Returns:
            int: Number of domains imported
        """
        import requests
        
        try:
            print(f"  Downloading blocklist from: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            count = 0
            for line in response.text.split('\n'):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse hosts file format (IP domain)
                parts = line.split()
                if len(parts) >= 2:
                    # Second part is the domain in hosts file format
                    domain = parts[1].lower().strip()
                    # Skip localhost entries
                    if domain and domain not in ['localhost', 'localhost.localdomain', 'local']:
                        # Skip IP addresses
                        if not domain.replace('.', '').replace(':', '').isdigit():
                            self.add_blocked(domain)
                            count += 1
                elif len(parts) == 1:
                    # Plain domain list
                    domain = parts[0].lower().strip()
                    if domain and not domain.replace('.', '').replace(':', '').isdigit():
                        self.add_blocked(domain)
                        count += 1
            
            print(f"  Successfully imported {count} domains from URL")
            return count
            
        except requests.RequestException as e:
            print(f"  Error downloading blocklist: {e}")
            raise Exception(f"Failed to download: {e}")
        except Exception as e:
            print(f"  Error parsing blocklist: {e}")
            raise Exception(f"Failed to parse: {e}")
    
    def _save_lists(self):
        """Save blocklists to JSON files"""
        try:
            with open(BLOCKLIST_FILE, 'w') as f:
                json.dump(list(self.blocked_domains), f, indent=2)
            
            with open(ALLOWLIST_FILE, 'w') as f:
                json.dump(list(self.allowed_domains), f, indent=2)
        except Exception as e:
            print(f"  Warning: Could not save lists: {e}")
    
    def _load_lists(self):
        """Load blocklists from JSON files"""
        try:
            if os.path.exists(BLOCKLIST_FILE):
                with open(BLOCKLIST_FILE, 'r') as f:
                    self.blocked_domains = set(json.load(f))
                print(f"  Loaded {len(self.blocked_domains)} blocked domains")
        except Exception as e:
            print(f"  Warning: Could not load blocklist: {e}")
        
        try:
            if os.path.exists(ALLOWLIST_FILE):
                with open(ALLOWLIST_FILE, 'r') as f:
                    self.allowed_domains = set(json.load(f))
                print(f"  Loaded {len(self.allowed_domains)} allowed domains")
        except Exception as e:
            print(f"  Warning: Could not load allowlist: {e}")


class AnomalyDetector:
    """Detect suspicious DNS patterns with enhanced algorithms"""
    
    def __init__(self):
        self.ip_query_count = defaultdict(list)  # IP -> [timestamps]
        self.domain_queries = defaultdict(int)   # domain -> count
        self.lock = threading.Lock()
        self.alerts = []
        self.alert_cooldown = {}  # Prevent duplicate alerts
        
    def check_query(self, ip, domain, query_type):
        """Check for anomalies and return alert if found
        
        Detections:
        1. Excessive queries (DDoS indicator)
        2. Suspicious domain keywords
        3. High entropy domains (DGA detection)
        
        Args:
            ip (str): Source IP address
            domain (str): Queried domain
            query_type (str): DNS query type
            
        Returns:
            dict: Alert object or None
        """
        current_time = time.time()
        alert = None
        
        with self.lock:
            # Track queries per IP
            self.ip_query_count[ip].append(current_time)
            
            # Clean old entries (older than 1 minute)
            self.ip_query_count[ip] = [t for t in self.ip_query_count[ip] 
                                       if current_time - t < 60]
            
            # Check for excessive queries (>200 per minute)
            query_count = len(self.ip_query_count[ip])
            if query_count > 200:
                # Check cooldown to avoid spam
                cooldown_key = f"excessive_{ip}"
                if cooldown_key not in self.alert_cooldown or \
                   current_time - self.alert_cooldown[cooldown_key] > 300:  # 5 min cooldown
                    
                    alert = {
                        'type': 'EXCESSIVE_QUERIES',
                        'severity': 'HIGH',
                        'ip': ip,
                        'count': query_count,
                        'message': f'Excessive queries from {ip}: {query_count} in 1 minute',
                        'timestamp': current_time
                    }
                    self.alerts.append(alert)
                    self.alert_cooldown[cooldown_key] = current_time
            
            # Check for suspicious domains
            suspicious_keywords = [
                'torrent', 'crack', 'keygen', 'malware', 'phishing',
                'ransomware', 'trojan', 'virus', 'exploit', 'hack'
            ]
            
            domain_lower = domain.lower()
            if any(kw in domain_lower for kw in suspicious_keywords):
                cooldown_key = f"suspicious_{domain}"
                if cooldown_key not in self.alert_cooldown or \
                   current_time - self.alert_cooldown[cooldown_key] > 600:  # 10 min cooldown
                    
                    alert = {
                        'type': 'SUSPICIOUS_DOMAIN',
                        'severity': 'MEDIUM',
                        'ip': ip,
                        'domain': domain,
                        'message': f'Suspicious domain queried: {domain} from {ip}',
                        'timestamp': current_time
                    }
                    self.alerts.append(alert)
                    self.alert_cooldown[cooldown_key] = current_time
            
            # DGA Detection (high entropy/randomness in domain)
            if self._is_potential_dga(domain):
                cooldown_key = f"dga_{domain}"
                if cooldown_key not in self.alert_cooldown or \
                   current_time - self.alert_cooldown[cooldown_key] > 600:
                    
                    alert = {
                        'type': 'POTENTIAL_DGA',
                        'severity': 'HIGH',
                        'ip': ip,
                        'domain': domain,
                        'message': f'Potential DGA domain detected: {domain} from {ip}',
                        'timestamp': current_time
                    }
                    self.alerts.append(alert)
                    self.alert_cooldown[cooldown_key] = current_time
            
            # Limit alert storage
            if len(self.alerts) > 100:
                self.alerts.pop(0)
        
        return alert
    
    def _is_potential_dga(self, domain):
        """Simple DGA detection based on entropy
        
        DGA (Domain Generation Algorithm) creates random-looking domains
        used by malware for C&C communication
        """
        # Extract just the domain name (before TLD)
        parts = domain.split('.')
        if len(parts) < 2:
            return False
        
        name = parts[0]
        
        # Skip if too short or known legitimate
        if len(name) < 8:
            return False
        
        # Calculate simple randomness score
        # High number of consonants in a row suggests randomness
        consonants = 'bcdfghjklmnpqrstvwxyz'
        max_consonants = 0
        current_consonants = 0
        
        for char in name.lower():
            if char in consonants:
                current_consonants += 1
                max_consonants = max(max_consonants, current_consonants)
            else:
                current_consonants = 0
        
        # If more than 5 consonants in a row, likely DGA
        return max_consonants > 5
    
    def get_alerts(self):
        """Get recent alerts"""
        with self.lock:
            return list(self.alerts[-20:])  # Last 20 alerts


class DNSStats:
    """Thread-safe statistics tracking with extended metrics"""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.total_queries = 0
        self.failed_queries = 0
        self.blocked_queries = 0
        self.cached_queries = 0
        self.response_times = []
        self.start_time = time.time()
        
    def add_query(self, success=True, blocked=False, cached=False, response_time=0):
        """Add query statistics"""
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
                # Keep last 1000 response times
                if len(self.response_times) > 1000:
                    self.response_times.pop(0)
    
    def get_stats(self):
        """Get comprehensive statistics"""
        with self.lock:
            avg_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            uptime = time.time() - self.start_time
            qps = self.total_queries / uptime if uptime > 0 else 0
            
            return {
                'total': self.total_queries,
                'failed': self.failed_queries,
                'blocked': self.blocked_queries,
                'cached': self.cached_queries,
                'avg_time': avg_time,
                'uptime': uptime,
                'queries_per_second': qps
            }


def create_blocked_response(request):
    """Create NXDOMAIN response for blocked domains"""
    reply = DNSRecord(
        DNSHeader(
            id=request.header.id,
            qr=1,    # Response
            aa=1,    # Authoritative
            ra=1,    # Recursion available
            rcode=3  # NXDOMAIN (domain doesn't exist)
        ),
        q=request.q
    )
    return reply.pack()


def handle_dns_request(data, addr, sock, log_queue, all_logs, stats_tracker, 
                       dns_cache, blocklist, anomaly_detector):
    """Handle individual DNS request with all features
    
    Process:
    1. Parse DNS request
    2. Check for anomalies
    3. Check blocklist
    4. Check cache
    5. Forward to upstream (with retry)
    6. Log result
    """
    start_time = time.time()
    success = True
    blocked = False
    cached = False
    response_time = 0
    
    try:
        # Parse DNS request
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
            response_time = (time.time() - start_time) * 1000
            details = '🚫 BLOCKED'
        else:
            # Check cache first
            cached_response = dns_cache.get(query_name, query_type)
            
            if cached_response:
                cached = True
                sock.sendto(cached_response, addr)
                response_time = (time.time() - start_time) * 1000
                details = f'💾 CACHED ({response_time:.1f}ms)'
            else:
                # Forward to upstream DNS with retry
                details = None
                for attempt in range(MAX_RETRIES):
                    try:
                        upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        upstream_sock.settimeout(TIMEOUT)
                        
                        # Use backup DNS on retry
                        upstream_server = UPSTREAM_DNS if attempt == 0 else UPSTREAM_DNS_BACKUP
                        
                        upstream_sock.sendto(data, (upstream_server, DNS_PORT))
                        response, _ = upstream_sock.recvfrom(4096)
                        
                        # Cache the response
                        dns_cache.set(query_name, query_type, response)
                        
                        response_time = (time.time() - start_time) * 1000
                        details = f'✓ OK ({response_time:.1f}ms)'
                        if attempt > 0:
                            details += f' [retry:{attempt}]'
                        
                        sock.sendto(response, addr)
                        upstream_sock.close()
                        break  # Success, exit retry loop
                        
                    except socket.timeout:
                        upstream_sock.close()
                        if attempt == MAX_RETRIES - 1:
                            success = False
                            details = '⏱ Timeout (all retries failed)'
                        continue
                        
                    except Exception as e:
                        upstream_sock.close()
                        if attempt == MAX_RETRIES - 1:
                            success = False
                            details = f'❌ Error: {str(e)[:20]}'
                        continue
        
        # Log entry
        log_entry = (timestamp, addr[0], query_name, query_type, details, success, blocked, cached)
        log_queue.put(log_entry)
        
        # Thread-safe log storage
        with threading.Lock():
            all_logs.append(log_entry)
            # Keep last 10000 entries
            if len(all_logs) > 10000:
                all_logs.pop(0)
        
        # Update statistics
        stats_tracker.add_query(success, blocked, cached, response_time if (success or blocked) else 0)
        
    except Exception as e:
        # Handle any unexpected errors
        print(f"⚠️  Error handling DNS request: {e}")
        stats_tracker.add_query(success=False)


def start_dns_server(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector):
    """Start DNS proxy server with error handling"""
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind(('0.0.0.0', DNS_PORT))
        
        print(f"✓ DNS Server running on port {DNS_PORT}")
        print(f"✓ Primary DNS: {UPSTREAM_DNS}")
        print(f"✓ Backup DNS: {UPSTREAM_DNS_BACKUP}")
        print(f"✓ Cache enabled (max: {dns_cache.max_size} entries)")
        print(f"✓ Blocklist enabled ({len(blocklist.blocked_domains)} domains)")
        print(f"✓ Allowlist enabled ({len(blocklist.allowed_domains)} domains)")
        print(f"✓ Anomaly detection active")
        print(f"✓ Request timeout: {TIMEOUT}s with {MAX_RETRIES} retries")
        print()
        
        # Main server loop
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                
                # Handle each request in a new thread
                thread = threading.Thread(
                    target=handle_dns_request,
                    args=(data, addr, sock, log_queue, all_logs, stats_tracker,
                          dns_cache, blocklist, anomaly_detector),
                    daemon=True,
                    name=f"DNS-Handler-{addr[0]}"
                )
                thread.start()
                
            except Exception as e:
                print(f"⚠️  Error receiving DNS request: {e}")
                continue
                
    except PermissionError:
        print("\n❌ Permission denied! Port 53 requires administrator/root privileges")
        print("   Please run this program as administrator (Windows) or with sudo (Linux/Mac)")
        
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Port {DNS_PORT} is already in use!")
            print("   Another DNS server or service is using this port.")
            print("   Please stop the other service first.")
        else:
            print(f"\n❌ Cannot bind to port {DNS_PORT}: {e}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Keyboard interrupt detected")
        print("Shutting down DNS server...")
        
    finally:
        sock.close()
        print("✓ DNS server socket closed")