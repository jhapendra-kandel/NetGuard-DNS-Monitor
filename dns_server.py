# NetGuard DNS Server - this is the main core dns server file
# it handles all the dns query stuff like processing, caching, blocking and detecting anomaly
# basically this whole file is the heart of our project without this nothing works

# Author: Jhapendra Kandel
# Project: 1st Year Python Programming
# Institution: Softwarica College of IT & E-Commerce (Coventry University)

# importing all the necessary modules we need for dns server to run
import socket
import threading
import time
import datetime
import json
import os
# dnslib is the main library we using for parsing and creating dns packets
from dnslib import DNSRecord, DNSQuestion, DNSHeader, RR, QTYPE, A
# defaultdict is useful for counting things without checking if key exists first
from collections import defaultdict

# --- DNS Server Configuration ---
# these are the upstream dns servers where we forward the queries to
UPSTREAM_DNS = '8.8.8.8'  # google dns - primary one we use
UPSTREAM_DNS_BACKUP = '1.1.1.1'  # cloudflare dns - backup incase google one fails
DNS_PORT = 53  # standard dns port, this is fixed dont change it
TIMEOUT = 3  # how long we wait for upstream response, increased to 3 sec for better reliability
MAX_RETRIES = 2  # if query fails we retry this many times before giving up

# file paths where we save blocklist and allowlist so they persist even after restart
BLOCKLIST_FILE = 'blocklist.json'
ALLOWLIST_FILE = 'allowlist.json'

# this lock is for thread safety when we writing logs
# without this multiple threads can write at same time and mess up the data
log_lock = threading.Lock()


class DNSCache:
    """Thread-safe DNS cache with TTL support and statistics"""
    
    # initializing the cache with max size limit
    def __init__(self, max_size=10000):
        self.cache = {}  # storing cached responses here, key is (domain, qtype) and value is (response, expiry_time)
        self.lock = threading.Lock()  # lock for thread safety so multiple threads dont mess up cache
        self.hits = 0  # counting how many times we found answer in cache
        self.misses = 0  # counting how many times answer was not in cache
        self.max_size = max_size  # maximum entries we allow in cache
        self.enabled = True  # we can turn cache on and off from gui
        
    def get(self, domain, qtype):
        """Get cached response if not expired
        
        Args:
            domain (str): Domain name
            qtype (str): Query type (A, AAAA, etc.)
            
        Returns:
            bytes: Cached DNS response or None
        """
        # if cache is turned off just return nothing and count as miss
        if not self.enabled:
            self.misses += 1
            return None
            
        with self.lock:
            key = (domain, qtype)
            if key in self.cache:
                response, expiry = self.cache[key]
                # checking if the cached entry is still valid (not expired yet)
                if time.time() < expiry:
                    self.hits += 1
                    return response
                else:
                    # entry expired so we remove it from cache no point keeping it
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
        # if cache disabled we dont store anything just return
        if not self.enabled:
            return
            
        with self.lock:
            # if cache is full we need to remove the oldest entry to make space
            if len(self.cache) >= self.max_size:
                # finding the entry that expires soonest and removing it
                oldest_key = min(self.cache.items(), key=lambda x: x[1][1])[0]
                del self.cache[oldest_key]
            
            key = (domain, qtype)
            # we cap the ttl at 1 hour max even if upstream says longer
            expiry = time.time() + min(ttl, 3600)
            self.cache[key] = (response, expiry)
    
    # clearing all cached entries, useful when user wants fresh start
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
            # calculating hit rate percentage
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
        self.blocked_domains = set()  # set of domains that are blocked
        self.allowed_domains = set()  # set of domains that are always allowed (whitelist)
        self.lock = threading.Lock()  # thread safety lock
        self.blocked_count = 0  # tracking how many queries we blocked so far
        
        # loading previously saved lists from json files when server starts
        self._load_lists()
    
    # adding a domain to the blocklist and saving to file
    def add_blocked(self, domain):
        """Add domain to blocklist"""
        with self.lock:
            self.blocked_domains.add(domain.lower().strip())
            self._save_lists()
    
    # adding a domain to allowlist so it never gets blocked
    def add_allowed(self, domain):
        """Add domain to allowlist"""
        with self.lock:
            self.allowed_domains.add(domain.lower().strip())
            self._save_lists()
    
    # removing domain from blocklist
    def remove_blocked(self, domain):
        """Remove from blocklist"""
        with self.lock:
            self.blocked_domains.discard(domain.lower().strip())
            self._save_lists()
    
    # removing domain from allowlist
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
            # first check if domain is in allowlist, if yes we let it through no matter what
            if domain_lower in self.allowed_domains:
                return False
            
            # checking exact match in blocklist
            if domain_lower in self.blocked_domains:
                self.blocked_count += 1
                return True
            
            # checking wildcard matches for subdomains
            # like if we blocked example.com then ads.example.com should also be blocked
            parts = domain_lower.split('.')
            for i in range(len(parts)):
                partial = '.'.join(parts[i:])
                if partial in self.blocked_domains:
                    self.blocked_count += 1
                    return True
        
        return False
    
    # returning both lists so gui can display them
    def get_lists(self):
        """Get current blocked and allowed lists"""
        with self.lock:
            return list(self.blocked_domains), list(self.allowed_domains)
    
    def load_default_blocklist(self):
        """Load common ad/tracking domains"""
        # these are common advertising and tracking domains that most people want to block
        # we collected these from various sources
        common_ads = [
            # Ad networks - these are the big advertising companies
            'doubleclick.net', 'googleadservices.com', 'googlesyndication.com',
            'google-analytics.com', 'googletagmanager.com',
            'scorecardresearch.com', 'taboola.com', 'outbrain.com',
            'advertising.com', 'adnxs.com', 'adsrvr.org',
            'criteo.com', 'pubmatic.com', 'rubiconproject.com',
            
            # Tracking domains - these track what you do online
            'hotjar.com', 'mouseflow.com', 'crazyegg.com',
            'quantserve.com', 'optimizely.com', 'mixpanel.com',
            
            # More ad networks
            'adserver.com', 'ads.yahoo.com', 'amazon-adsystem.com',
            'bing.com/ads', 'facebook.com/tr', 'twitter.com/i/adsct',
            
            # Extended tracking/ad domains added in v2.2.0
            'linkedin.com/analytics', 'branch.io', 'appsflyer.com',
            'adjust.com', 'adsystem.com', 'adroll.com', 'bidswitch.net',
            'demdex.net', 'omtrdc.net', 'everesttech.net', 'segment.com',
            'amplitude.com', 'heap.io', 'fullstory.com', 'loggly.com',
            
            # Additional ad networks we added later
            'moatads.com', 'doubleverify.com', 'ias.com', 'integral-ad-science.com',
            'adform.net', 'casalemedia.com', 'openx.net', 'sharethrough.com',
            'triplelift.com', 'indexexchange.com', 'spotxchange.com', 'smartadserver.com',
            'yieldmo.com', 'sovrn.com', 'lijit.com', 'rhythmone.com',
            
            # Tracking pixels and analytics - these are sneaky tracking things
            'pixel.facebook.com', 'pixel.ad', 'tracking.com', 'tr.snapchat.com',
            'analytics.tiktok.com', 'ads.tiktok.com', 'analytics.twitter.com',
            'ads.pinterest.com', 'analytics.pinterest.com', 'ads.reddit.com',
            'events.reddit.com', 'pixel.reddit.com', 'analytics.yahoo.com',
            
            # Mobile ad networks - ads that show in mobile apps
            'admob.com', 'unity3d.com/ads', 'unityads.unity3d.com', 'vungle.com',
            'chartboost.com', 'ironsrc.com', 'ironsource.mobi', 'mopub.com',
            'inmobi.com', 'startapp.com', 'adcolony.com', 'fyber.com',
            
            # Data brokers and trackers - these collect and sell your data
            'bluekai.com', 'exelator.com', 'acxiom.com', 'liveramp.com',
            'oracle.com/cx', 'tapad.com', 'drawbridge.com', 'crosswise.com',
            'lotame.com', 'neustar.biz', 'rlcdn.com', 'krxd.net',
            
            # Retargeting and remarketing - ads that follow you around the internet
            'adsbygoogle.com', 'adskeeper.co.uk', 'revcontent.com', 'mgid.com',
            'contentad.net', 'adblade.com', 'zergnet.com', 'nativo.com',
        ]
        
        # adding all these domains to our blocklist one by one
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
                    # skipping empty lines and comments that start with #
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
            # going through each line of the downloaded file
            for line in response.text.split('\n'):
                line = line.strip()
                
                # skipping empty lines and comment lines
                if not line or line.startswith('#'):
                    continue
                
                # hosts file format has IP then domain like "0.0.0.0 ads.example.com"
                parts = line.split()
                if len(parts) >= 2:
                    # second part is the domain name we want to block
                    domain = parts[1].lower().strip()
                    # we skip localhost entries because blocking those would break things
                    if domain and domain not in ['localhost', 'localhost.localdomain', 'local']:
                        # also skip if its just an ip address not a domain
                        if not domain.replace('.', '').replace(':', '').isdigit():
                            self.add_blocked(domain)
                            count += 1
                elif len(parts) == 1:
                    # some files just have plain domain list without ip
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
        # saving both lists to json files so they survive restart
        try:
            with open(BLOCKLIST_FILE, 'w') as f:
                json.dump(list(self.blocked_domains), f, indent=2)
            
            with open(ALLOWLIST_FILE, 'w') as f:
                json.dump(list(self.allowed_domains), f, indent=2)
        except Exception as e:
            print(f"  Warning: Could not save lists: {e}")
    
    def _load_lists(self):
        """Load blocklists from JSON files"""
        # loading blocked domains from saved file if it exists
        try:
            if os.path.exists(BLOCKLIST_FILE):
                with open(BLOCKLIST_FILE, 'r') as f:
                    self.blocked_domains = set(json.load(f))
                print(f"  Loaded {len(self.blocked_domains)} blocked domains")
        except Exception as e:
            print(f"  Warning: Could not load blocklist: {e}")
        
        # loading allowed domains from saved file if it exists
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
        self.ip_query_count = defaultdict(list)  # tracking timestamps of queries per ip
        self.domain_queries = defaultdict(int)   # counting how many times each domain queried
        self.lock = threading.Lock()
        self.alerts = []  # storing all the alerts we generated
        self.alert_cooldown = {}  # this prevents sending same alert again and again
        
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
            # recording this query timestamp for the ip
            self.ip_query_count[ip].append(current_time)
            
            # removing old entries that are older than 1 minute, we only care about recent ones
            self.ip_query_count[ip] = [t for t in self.ip_query_count[ip] 
                                       if current_time - t < 60]
            
            # if someone sends more than 200 queries in 1 minute thats suspicious
            # could be a ddos attack or something bad happening
            query_count = len(self.ip_query_count[ip])
            if query_count > 200:
                # checking cooldown so we dont spam same alert every second
                cooldown_key = f"excessive_{ip}"
                if cooldown_key not in self.alert_cooldown or \
                   current_time - self.alert_cooldown[cooldown_key] > 300:  # 5 min cooldown between same alerts
                    
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
            
            # checking if domain name contains any suspicious keywords
            # like torrent, malware, hack etc these are red flags
            suspicious_keywords = [
                'torrent', 'crack', 'keygen', 'malware', 'phishing',
                'ransomware', 'trojan', 'virus', 'exploit', 'hack'
            ]
            
            domain_lower = domain.lower()
            if any(kw in domain_lower for kw in suspicious_keywords):
                cooldown_key = f"suspicious_{domain}"
                if cooldown_key not in self.alert_cooldown or \
                   current_time - self.alert_cooldown[cooldown_key] > 600:  # 10 min cooldown for suspicious
                    
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
            
            # DGA Detection - checking if domain looks randomly generated
            # malware uses random domain names to communicate with command server
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
            
            # we only keep last 100 alerts so memory doesnt fill up
            if len(self.alerts) > 100:
                self.alerts.pop(0)
        
        return alert
    
    def _is_potential_dga(self, domain):
        """Simple DGA detection based on entropy
        
        DGA (Domain Generation Algorithm) creates random-looking domains
        used by malware for C&C communication
        """
        # getting just the main part of domain before the tld
        parts = domain.split('.')
        if len(parts) < 2:
            return False
        
        name = parts[0]
        
        # if name is short its probably not dga, legit domains can be short
        if len(name) < 8:
            return False
        
        # checking how many consonants appear in a row
        # real words have mix of vowels and consonants but random strings have lots of consonants together
        consonants = 'bcdfghjklmnpqrstvwxyz'
        max_consonants = 0
        current_consonants = 0
        
        for char in name.lower():
            if char in consonants:
                current_consonants += 1
                max_consonants = max(max_consonants, current_consonants)
            else:
                current_consonants = 0
        
        # more than 5 consonants in a row means its probably random generated domain
        return max_consonants > 5
    
    # returning last 20 alerts for display in gui
    def get_alerts(self):
        """Get recent alerts"""
        with self.lock:
            return list(self.alerts[-20:])


class DNSStats:
    """Thread-safe statistics tracking with extended metrics"""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.total_queries = 0  # total number of queries we processed
        self.failed_queries = 0  # queries that failed
        self.blocked_queries = 0  # queries we blocked
        self.cached_queries = 0  # queries served from cache
        self.response_times = []  # storing response times to calculate average
        self.start_time = time.time()  # when server started, for uptime calculation
        
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
                # we only keep last 1000 response times so list doesnt get too big
                if len(self.response_times) > 1000:
                    self.response_times.pop(0)
    
    # calculating and returning all the stats for display
    def get_stats(self):
        """Get comprehensive statistics"""
        with self.lock:
            # calculating average response time
            avg_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            # how long server has been running
            uptime = time.time() - self.start_time
            # queries per second calculation
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


# this function creates a fake response for blocked domains
# it tells the device that domain doesnt exist (NXDOMAIN)
def create_blocked_response(request):
    """Create NXDOMAIN response for blocked domains"""
    reply = DNSRecord(
        DNSHeader(
            id=request.header.id,
            qr=1,    # this means its a response not a question
            aa=1,    # we are saying we are authoritative for this
            ra=1,    # recursion is available
            rcode=3  # NXDOMAIN means domain doesnt exist, this is how we block it
        ),
        q=request.q
    )
    return reply.pack()


# this is the main function that handles each dns request
# every dns query that comes in gets processed here
# this is very important function dont remove or change
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
        # parsing the raw dns data into something we can read
        request = DNSRecord.parse(data)
        # getting the domain name that was requested
        query_name = str(request.q.qname).rstrip('.')
        # getting what type of query it is (A record, AAAA etc)
        query_type = QTYPE.get(request.q.qtype, 'UNKNOWN')
        
        # getting current time for logging purpose
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # first we check if this query looks suspicious or not
        alert = anomaly_detector.check_query(addr[0], query_name, query_type)
        if alert:
            # if anomaly found we put alert in queue for gui to show
            log_queue.put(('ALERT', alert))
        
        # now checking if this domain is in our blocklist
        if blocklist.is_blocked(query_name):
            blocked = True
            # sending back NXDOMAIN response so device thinks domain doesnt exist
            response = create_blocked_response(request)
            sock.sendto(response, addr)
            response_time = (time.time() - start_time) * 1000
            details = '🚫 BLOCKED'
        else:
            # domain is not blocked so we need to resolve it
            # first checking if we already have answer in cache
            cached_response = dns_cache.get(query_name, query_type)
            
            if cached_response:
                # found in cache so we send cached response, much faster this way
                cached = True
                sock.sendto(cached_response, addr)
                response_time = (time.time() - start_time) * 1000
                details = f'💾 CACHED ({response_time:.1f}ms)'
            else:
                # not in cache so we have to ask upstream dns server
                # we try multiple times incase first attempt fails
                details = None
                for attempt in range(MAX_RETRIES):
                    try:
                        # creating new socket for upstream query
                        upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        upstream_sock.settimeout(TIMEOUT)
                        
                        # on first try use google dns, on retry use cloudflare as backup
                        upstream_server = UPSTREAM_DNS if attempt == 0 else UPSTREAM_DNS_BACKUP
                        
                        # forwarding the original query to upstream dns
                        upstream_sock.sendto(data, (upstream_server, DNS_PORT))
                        # waiting for response from upstream
                        response, _ = upstream_sock.recvfrom(4096)
                        
                        # saving response in cache for next time someone asks same thing
                        dns_cache.set(query_name, query_type, response)
                        
                        response_time = (time.time() - start_time) * 1000
                        details = f'✓ OK ({response_time:.1f}ms)'
                        if attempt > 0:
                            # letting user know this was a retry not first attempt
                            details += f' [retry:{attempt}]'
                        
                        # sending the response back to the device that asked
                        sock.sendto(response, addr)
                        upstream_sock.close()
                        break  # success so we exit the retry loop
                        
                    except socket.timeout:
                        # upstream didnt respond in time
                        upstream_sock.close()
                        if attempt == MAX_RETRIES - 1:
                            # all retries failed, nothing we can do
                            success = False
                            details = '⏱ Timeout (all retries failed)'
                        continue
                        
                    except Exception as e:
                        # some other error happened
                        upstream_sock.close()
                        if attempt == MAX_RETRIES - 1:
                            success = False
                            details = f'❌ Error: {str(e)[:20]}'
                        continue
        
        # creating log entry with all the info about this query
        log_entry = (timestamp, addr[0], query_name, query_type, details, success, blocked, cached)
        # putting in queue so gui can pick it up and display
        log_queue.put(log_entry)
        
        # storing log in our main log list, using lock for thread safety
        with log_lock:                   
            all_logs.append(log_entry)
            # keeping only last 10000 logs so memory doesnt overflow
            if len(all_logs) > 10000:
                all_logs.pop(0)
        
        # updating the statistics counters
        stats_tracker.add_query(success, blocked, cached, response_time if (success or blocked) else 0)
        
    except Exception as e:
        # if anything goes wrong we just log the error and move on
        # we dont want one bad query to crash the whole server
        print(f"⚠️  Error handling DNS request: {e}")
        stats_tracker.add_query(success=False)


# this function starts the main dns server and listens for incoming queries
# this is like the entry point for the dns server part
def start_dns_server(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector):
    """Start DNS proxy server with error handling"""
    
    # creating udp socket for dns (dns uses udp not tcp)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # this allows reusing the port if server restarts quickly
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # binding to port 53 on all interfaces so any device can send queries to us
        sock.bind(('0.0.0.0', DNS_PORT))
        
        # printing all the server info when it starts successfully
        print(f"✓ DNS Server running on port {DNS_PORT}")
        print(f"✓ Primary DNS: {UPSTREAM_DNS}")
        print(f"✓ Backup DNS: {UPSTREAM_DNS_BACKUP}")
        print(f"✓ Cache enabled (max: {dns_cache.max_size} entries)")
        print(f"✓ Blocklist enabled ({len(blocklist.blocked_domains)} domains)")
        print(f"✓ Allowlist enabled ({len(blocklist.allowed_domains)} domains)")
        print(f"✓ Anomaly detection active")
        print(f"✓ Request timeout: {TIMEOUT}s with {MAX_RETRIES} retries")
        print()
        
        # this is the main loop that runs forever listening for dns queries
        # it keeps running until server is stopped
        while True:
            try:
                # waiting for incoming dns query data
                data, addr = sock.recvfrom(4096)
                
                # creating a new thread for each request so server can handle multiple at same time
                # without threading server would be very slow handling one by one
                thread = threading.Thread(
                    target=handle_dns_request,
                    args=(data, addr, sock, log_queue, all_logs, stats_tracker,
                          dns_cache, blocklist, anomaly_detector),
                    daemon=True,
                    name=f"DNS-Handler-{addr[0]}"
                )
                thread.start()
                
            except Exception as e:
                # if error happens receiving data we just log it and continue listening
                print(f"⚠️  Error receiving DNS request: {e}")
                continue
                
    except PermissionError:
        # port 53 needs admin/root access, this error means user didnt run as admin
        print("\n❌ Permission denied! Port 53 requires administrator/root privileges")
        print("   Please run this program as administrator (Windows) or with sudo (Linux/Mac)")
        
    except OSError as e:
        # another program is already using port 53
        if "Address already in use" in str(e):
            print(f"\n❌ Port {DNS_PORT} is already in use!")
            print("   Another DNS server or service is using this port.")
            print("   Please stop the other service first.")
        else:
            print(f"\n❌ Cannot bind to port {DNS_PORT}: {e}")
        
    except KeyboardInterrupt:
        # user pressed ctrl+c to stop the server
        print("\n\n⚠️  Keyboard interrupt detected")
        print("Shutting down DNS server...")
        
    finally:
        # no matter what happens we always close the socket properly
        sock.close()
        print("✓ -DNS server socket closed-")