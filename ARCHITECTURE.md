# 🏗️ Architecture Documentation - NetGuard DNS Monitor

Technical architecture and design documentation for developers and contributors.

---

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Threading Model](#threading-model)
- [DNS Protocol Implementation](#dns-protocol-implementation)
- [Caching Strategy](#caching-strategy)
- [Security Architecture](#security-architecture)
- [Performance Considerations](#performance-considerations)
- [Database Schema](#database-schema)
- [API Design](#api-design)

---

## 🎯 System Overview

NetGuard DNS Monitor is a multi-threaded DNS proxy server with GUI monitoring capabilities, built on a modular architecture separating concerns between networking, business logic, and presentation.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                         │
│  (Phones, Computers, IoT Devices making DNS queries)       │
└────────────────────────┬────────────────────────────────────┘
                         │ UDP Port 53
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   NetGuard DNS Monitor                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Presentation Layer (GUI)                │   │
│  │                   [gui.py]                           │   │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐           │   │
│  │  │Logs  │  │Stats │  │Block │  │Alert │           │   │
│  │  │ Tab  │  │ Tab  │  │ Tab  │  │ Tab  │           │   │
│  │  └──────┘  └──────┘  └──────┘  └──────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Business Logic Layer                    │   │
│  │                [dns_server.py, stats.py]             │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │DNSCache  │ │Blocklist │ │ Anomaly  │           │   │
│  │  │          │ │          │ │ Detector │           │   │
│  │  └──────────┘ └──────────┘ └──────────┘           │   │
│  │  ┌──────────────────────────────────────┐          │   │
│  │  │        DNSStats (Metrics)            │          │   │
│  │  └──────────────────────────────────────┘          │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Network Layer                           │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │   DNS Request Handler (Multi-threaded)      │    │   │
│  │  │   - Parse DNS request                       │    │   │
│  │  │   - Check cache                             │    │   │
│  │  │   - Apply filters                           │    │   │
│  │  │   - Forward to upstream                     │    │   │
│  │  │   - Return response                         │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ DNS Queries
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Upstream DNS (e.g., 8.8.8.8)                   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **GUI** | Tkinter | User interface |
| **Visualization** | Matplotlib | Charts and graphs |
| **DNS** | dnslib | DNS protocol handling |
| **Networking** | socket (stdlib) | UDP communication |
| **Concurrency** | threading (stdlib) | Multi-threaded processing |
| **Data Structures** | collections (stdlib) | Efficient data handling |

---

## 🧩 Component Architecture

### 1. Main Application (`main.py`)

**Responsibilities:**
- Application bootstrap
- Component initialization
- Thread orchestration
- Graceful shutdown

**Key Functions:**

```python
def main():
    """
    Entry point that:
    1. Initializes shared data structures
    2. Starts DNS server thread (daemon)
    3. Launches GUI (main thread)
    4. Handles shutdown signals
    """
```

**Initialized Components:**
```python
log_queue = queue.Queue()          # Thread-safe log communication
all_logs = []                       # Shared log storage
stats_tracker = DNSStats()          # Metrics tracking
dns_cache = DNSCache()              # Response caching
blocklist = DNSBlocklist()          # Domain filtering
anomaly_detector = AnomalyDetector() # Threat detection
```

### 2. DNS Server (`dns_server.py`)

**Architecture:**

```
┌─────────────────────────────────────────┐
│         DNSServer (Main Thread)         │
│  - Binds to UDP port 53                │
│  - Listens for incoming requests       │
│  - Spawns handler threads              │
└────────┬────────────────────────────────┘
         │
         ├─► Handler Thread 1 ──► Process Request 1
         ├─► Handler Thread 2 ──► Process Request 2
         ├─► Handler Thread 3 ──► Process Request 3
         └─► Handler Thread N ──► Process Request N
```

#### Class: `DNSCache`

```python
class DNSCache:
    """Thread-safe DNS response cache with TTL support."""
    
    def __init__(self):
        self.cache: Dict[Tuple[str, str], Tuple[bytes, float]] = {}
        self.lock: threading.Lock = threading.Lock()
        self.hits: int = 0
        self.misses: int = 0
    
    def get(self, domain: str, qtype: str) -> Optional[bytes]:
        """Retrieve cached response if valid."""
        
    def set(self, domain: str, qtype: str, response: bytes, ttl: int):
        """Store response with TTL-based expiration."""
```

**Data Structure:**
```python
cache = {
    ('example.com', 'A'): (b'<dns_response>', 1675430400.0),  # (response, expiry_timestamp)
    ('google.com', 'AAAA'): (b'<dns_response>', 1675431000.0)
}
```

**Thread Safety:**
- Uses `threading.Lock()` for all cache operations
- Lock acquired with context manager: `with self.lock:`
- Prevents race conditions in multi-threaded access

#### Class: `DNSBlocklist`

```python
class DNSBlocklist:
    """Manage blocked and allowed domains."""
    
    def __init__(self):
        self.blocked_domains: Set[str] = set()
        self.allowed_domains: Set[str] = set()
        self.lock: threading.Lock = threading.Lock()
    
    def is_blocked(self, domain: str) -> bool:
        """Check if domain should be blocked.
        
        Algorithm:
        1. Check allowlist (if present, return False)
        2. Check exact match in blocklist
        3. Check wildcard matches (subdomains)
        """
```

**Wildcard Matching Algorithm:**
```python
# For domain: "ads.tracking.example.com"
parts = domain.split('.')  # ['ads', 'tracking', 'example', 'com']

# Check each partial match:
# - ads.tracking.example.com
# - tracking.example.com
# - example.com
# - com

for i in range(len(parts)):
    partial = '.'.join(parts[i:])
    if partial in blocked_domains:
        return True
```

#### Class: `AnomalyDetector`

```python
class AnomalyDetector:
    """Pattern-based threat detection."""
    
    def __init__(self):
        self.ip_query_count: Dict[str, List[float]] = defaultdict(list)
        self.alerts: List[Dict] = []
    
    def check_query(self, ip: str, domain: str, query_type: str) -> Optional[Dict]:
        """Analyze query for suspicious patterns.
        
        Detections:
        1. Excessive queries (>100/min from single IP)
        2. Suspicious keywords in domain
        3. DGA patterns (future enhancement)
        """
```

**Alert Structure:**
```python
alert = {
    'type': 'EXCESSIVE_QUERIES',
    'severity': 'HIGH',
    'ip': '192.168.1.105',
    'count': 156,
    'message': 'Excessive queries from 192.168.1.105: 156 in 1 minute',
    'timestamp': 1675430400.0
}
```

#### Class: `DNSStats`

```python
class DNSStats:
    """Thread-safe statistics tracking."""
    
    def __init__(self):
        self.lock: threading.Lock = threading.Lock()
        self.total_queries: int = 0
        self.failed_queries: int = 0
        self.blocked_queries: int = 0
        self.cached_queries: int = 0
        self.response_times: List[float] = []
    
    def add_query(self, success: bool, blocked: bool, 
                  cached: bool, response_time: float):
        """Record query statistics."""
```

### 3. GUI Interface (`gui.py`)

**Class Hierarchy:**

```
DNSMonitorGUI
├── create_logs_tab()
│   ├── Treeview (log display)
│   ├── Filters (text, type)
│   └── Update loop
│
├── create_stats_tab()
│   ├── Metrics display
│   ├── Charts (Matplotlib)
│   └── Auto-refresh
│
├── create_blocklist_tab()
│   ├── Blocked list
│   ├── Allowed list
│   └── Management buttons
│
└── create_alerts_tab()
    ├── Alert display
    └── Alert management
```

**Update Mechanism:**

```python
def update_gui(self):
    """Main update loop (500ms interval).
    
    Process:
    1. Update logs from queue
    2. Update statistics if tab active
    3. Update status bar
    4. Schedule next update
    """
    self.update_logs()
    if self.notebook.index(self.notebook.select()) == 1:
        self.update_stats()
    self.status_bar.config(text=status_text)
    self.root.after(500, self.update_gui)  # Recursive call
```

### 4. Statistics Engine (`stats.py`)

**Function: `compute_stats()`**

```python
def compute_stats(all_logs: List[Tuple]) -> str:
    """Compute comprehensive statistics.
    
    Input: List of log tuples
    Output: Formatted statistics string
    
    Computations:
    - Overview metrics
    - Top devices analysis
    - Top domains analysis
    - Query type breakdown
    - Performance insights
    """
```

**Data Processing Pipeline:**

```
Raw Logs
    ↓
Counter Analysis
    ├─► IP Counter (Top Devices)
    ├─► Domain Counter (Top Domains)
    └─► Type Counter (Query Types)
    ↓
Percentage Calculations
    ↓
Formatting & Visualization
    ↓
String Output
```

---

## 🔄 Data Flow

### DNS Query Processing Flow

```
1. Client Device
   │
   ├─► DNS Query (UDP:53)
   │
2. NetGuard Server
   │
   ├─► Parse Request (dnslib)
   │
3. Anomaly Detection
   │
   ├─► Check for suspicious patterns
   │   └─► If suspicious: Generate Alert
   │
4. Blocklist Check
   │
   ├─► Is domain blocked?
   │   ├─► YES: Return NXDOMAIN (blocked response)
   │   └─► NO: Continue
   │
5. Cache Lookup
   │
   ├─► Is response cached?
   │   ├─► YES: Return cached response (fast)
   │   └─► NO: Continue
   │
6. Upstream Forwarding
   │
   ├─► Forward to 8.8.8.8
   │
   ├─► Receive response
   │
   ├─► Cache response
   │
7. Return to Client
   │
8. Logging
   │
   ├─► Add to log queue
   │
   ├─► Update statistics
   │
9. GUI Update
   │
   └─► Display in interface
```

### Inter-Component Communication

```
DNS Server Thread ─────► Log Queue ─────► GUI Thread
                  (Producer)    (Consumer)

Shared Resources (Thread-Safe):
├─► all_logs (list with threading.Lock in operations)
├─► DNSCache (internal lock)
├─► DNSBlocklist (internal lock)
├─► DNSStats (internal lock)
└─► AnomalyDetector (internal lock)
```

---

## 🧵 Threading Model

### Thread Architecture

```
Main Thread (GUI)
├─► Tkinter event loop
├─► GUI updates every 500ms
└─► Handles user interactions

DNS Server Thread (Daemon)
├─► Listens on port 53
├─► Spawns handler threads
└─► Dies when main thread exits

Handler Threads (Multiple, Daemon)
├─► One per DNS request
├─► Short-lived
├─► Process request and exit
└─► Die when main thread exits
```

### Thread Synchronization

**1. Locks**

```python
# Each shared resource has its own lock
cache.lock = threading.Lock()
blocklist.lock = threading.Lock()
stats.lock = threading.Lock()
anomaly_detector.lock = threading.Lock()
```

**2. Queue**

```python
# Thread-safe queue for logging
log_queue = queue.Queue()

# Producer (DNS Handler Thread)
log_queue.put(log_entry)

# Consumer (GUI Thread)
while not log_queue.empty():
    log_entry = log_queue.get()
```

**3. Shared List Access**

```python
# Not inherently thread-safe, so we use manual locking
lock = threading.Lock()

with lock:
    all_logs.append(log_entry)
    if len(all_logs) > 10000:
        all_logs.pop(0)
```

### Avoiding Deadlocks

**Rules:**
1. Always acquire locks in same order
2. Use context managers (`with lock:`)
3. Never nest locks if possible
4. Keep critical sections small
5. Release locks quickly

---

## 🌐 DNS Protocol Implementation

### DNS Message Structure

```
+---------------------+
|        Header       |  12 bytes
+---------------------+
|       Question      |  Variable
+---------------------+
|        Answer       |  Variable
+---------------------+
|      Authority      |  Variable
+---------------------+
|      Additional     |  Variable
+---------------------+
```

### Request Parsing

```python
# Using dnslib
request = DNSRecord.parse(data)
query_name = str(request.q.qname).rstrip('.')
query_type = QTYPE.get(request.q.qtype)

# Example:
# query_name = "www.google.com"
# query_type = "A"
```

### Response Creation

#### Success Response
```python
# Forward to upstream and cache
upstream_sock.sendto(data, (UPSTREAM_DNS, DNS_PORT))
response, _ = upstream_sock.recvfrom(4096)
dns_cache.set(query_name, query_type, response)
sock.sendto(response, addr)
```

#### Blocked Response (NXDOMAIN)
```python
def create_blocked_response(request):
    """Create NXDOMAIN for blocked domains."""
    reply = DNSRecord(
        DNSHeader(
            id=request.header.id,
            qr=1,    # Response
            aa=1,    # Authoritative
            ra=1,    # Recursion available
            rcode=3  # NXDOMAIN
        ),
        q=request.q
    )
    return reply.pack()
```

---

## 💾 Caching Strategy

### Cache Key Design

```python
# Composite key: (domain, query_type)
key = ("example.com", "A")

# Why composite?
# - Same domain, different types (A, AAAA, MX)
# - Each needs separate caching
# - Prevents type confusion
```

### TTL Management

```python
def set(self, domain, qtype, response, ttl=300):
    """Cache with TTL."""
    expiry = time.time() + min(ttl, 3600)  # Max 1 hour
    self.cache[key] = (response, expiry)

def get(self, domain, qtype):
    """Get if not expired."""
    if key in self.cache:
        response, expiry = self.cache[key]
        if time.time() < expiry:
            return response  # Valid
        else:
            del self.cache[key]  # Expired, remove
    return None
```

### Cache Eviction

**Currently:** No automatic eviction (relies on TTL expiration)

**Future Enhancement:** LRU (Least Recently Used)
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)  # Mark as recently used
            return self.cache[key]
    
    def set(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # Remove oldest
```

---

## 🔒 Security Architecture

### Defense in Depth

```
Layer 1: Input Validation
├─► Validate DNS query format
├─► Sanitize domain names
└─► Check for malformed packets

Layer 2: Blocklist Filtering
├─► Check against known malicious domains
├─► Apply custom user rules
└─► Allowlist override for false positives

Layer 3: Anomaly Detection
├─► Monitor query frequency
├─► Detect suspicious patterns
└─► Alert on potential threats

Layer 4: Rate Limiting (Future)
├─► Per-IP query limits
├─► Global query limits
└─► Temporary bans for abuse
```

### Threat Model

**Protected Against:**
- ✅ Malware callbacks
- ✅ Ad tracking
- ✅ Phishing domains
- ✅ DDoS attempts (partial)
- ✅ Data exfiltration (DNS tunneling detection)

**Not Protected Against:**
- ❌ Encrypted DNS tunneling (advanced)
- ❌ Sophisticated DDoS (needs additional layers)
- ❌ Zero-day domain threats (not in blocklist)

---

## ⚡ Performance Considerations

### Bottlenecks

1. **GUI Updates (500ms)**
   - Too frequent: High CPU
   - Too infrequent: Laggy UI
   - **Solution:** Adaptive update rate based on query volume

2. **Log Storage**
   - Unlimited growth causes memory issues
   - **Solution:** Rotating log with 10,000 entry limit

3. **Chart Rendering**
   - Rebuilding charts is expensive
   - **Solution:** Only render when stats tab active

### Optimization Strategies

#### 1. Efficient Data Structures

```python
# Using sets for O(1) lookup instead of lists O(n)
blocked_domains = set()  # Fast membership testing

# Using Counter for aggregation
from collections import Counter
domain_counter = Counter(log[2] for log in all_logs)  # Efficient counting
```

#### 2. Lazy Loading

```python
def update_stats(self):
    """Only compute when needed."""
    if self.notebook.index(self.notebook.select()) == 1:
        # Stats tab is active, update
        self.render_statistics()
```

#### 3. Batch Processing

```python
def update_logs(self):
    """Process logs in batches."""
    new_entries = []
    while not self.log_queue.empty() and len(new_entries) < 100:
        new_entries.append(self.log_queue.get())
    # Insert all at once
```

---

## 🗄️ Database Schema (Future Enhancement)

### Proposed SQLite Schema

```sql
-- Queries table
CREATE TABLE queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    source_ip TEXT NOT NULL,
    query_domain TEXT NOT NULL,
    query_type TEXT NOT NULL,
    response_time REAL,
    success BOOLEAN,
    blocked BOOLEAN,
    cached BOOLEAN,
    INDEX idx_timestamp (timestamp),
    INDEX idx_source_ip (source_ip),
    INDEX idx_domain (query_domain)
);

-- Blocklist table
CREATE TABLE blocklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT UNIQUE NOT NULL,
    added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    category TEXT,
    INDEX idx_domain (domain)
);

-- Alerts table
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    source_ip TEXT,
    message TEXT,
    acknowledged BOOLEAN DEFAULT 0
);
```

---

## 🔌 API Design (Future Enhancement)

### RESTful API Endpoints

```
GET    /api/v1/stats          # Get statistics
GET    /api/v1/logs           # Get logs (with pagination)
GET    /api/v1/blocklist      # Get blocklist
POST   /api/v1/blocklist      # Add to blocklist
DELETE /api/v1/blocklist/:id  # Remove from blocklist
GET    /api/v1/alerts         # Get alerts
POST   /api/v1/alerts/:id/ack # Acknowledge alert
```

### Example Response

```json
{
  "stats": {
    "total_queries": 5234,
    "successful": 4890,
    "failed": 89,
    "blocked": 255,
    "cached": 3128,
    "cache_hit_rate": 59.8
  },
  "top_domains": [
    {"domain": "www.google.com", "count": 567},
    {"domain": "fonts.googleapis.com", "count": 234}
  ]
}
```

---

<div align="center">

**Architecture Documentation** | NetGuard DNS Monitor v2.0

[Back to README](README.md) | [Contributing](CONTRIBUTING.md)

</div>
