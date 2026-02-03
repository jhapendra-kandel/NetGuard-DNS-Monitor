# 📖 Usage Guide - NetGuard DNS Monitor

Complete user manual for operating NetGuard DNS Monitor.

---

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [User Interface Overview](#user-interface-overview)
- [Live Logs Tab](#-live-logs-tab)
- [Statistics & Analytics Tab](#-statistics--analytics-tab)
- [Blocklist Manager](#-blocklist-manager)
- [Alerts Monitor](#-alerts-monitor)
- [Menu Options](#menu-options)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)
- [Use Cases](#use-cases)

---

## 🚀 Getting Started

### Starting the Application

**Windows:**
```cmd
# Open Command Prompt as Administrator
cd C:\Path\To\NetGuard-DNS-Monitor
python main.py
```

**Linux/macOS:**
```bash
cd /path/to/NetGuard-DNS-Monitor
sudo python3 main.py
```

### First Launch

When you first launch NetGuard DNS Monitor, you'll see:

```
╔══════════════════════════════════════════════════════════════╗
║        🛡️  DNS NETWORK ACTIVITY MONITOR v2.0  🛡️            ║
║              Final Year Cybersecurity Project               ║
╚══════════════════════════════════════════════════════════════╝

Features Enabled:
  ✓ Real-time DNS query monitoring
  ✓ DNS caching for improved performance
  ✓ Blocklist/Allowlist management
  ✓ Anomaly detection & security alerts
  ✓ Traffic analysis & statistics
  ✓ CSV export capabilities

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ DNS Server running on port 53
✓ Forwarding to 8.8.8.8
✓ Cache enabled
✓ Blocklist enabled (0 domains)
✓ Anomaly detection active
```

---

## 🖥️ User Interface Overview

NetGuard DNS Monitor features a tabbed interface with four main sections:

| Tab | Icon | Purpose |
|-----|------|---------|
| **Live Logs** | 📋 | Real-time DNS query monitoring |
| **Statistics** | 📊 | Analytics and visualizations |
| **Blocklist** | 🚫 | Domain blocking management |
| **Alerts** | ⚠️ | Security threat notifications |

### Status Bar

Located at the bottom of the window, displays:
- Total queries processed
- Number of blocked queries
- Number of cached queries
- Application status (Running/Paused)

Example: `Queries: 1,234 | Blocked: 45 | Cached: 678 | Running ✓`

---

## 📋 Live Logs Tab

Monitor all DNS queries in real-time with detailed information.

### Display Columns

| Column | Description | Example |
|--------|-------------|---------|
| **Timestamp** | Query time | 2026-02-03 14:23:45.123 |
| **Source IP** | Device making query | 192.168.1.105 |
| **Query Domain** | Requested domain | www.google.com |
| **Type** | DNS record type | A, AAAA, CNAME |
| **Details** | Query result | ✓ OK (45ms) |
| **Status** | Success/Fail/Block | Success |

### Color Coding

Queries are color-coded for quick status identification:

- 🟢 **Green (Success)** - Query resolved successfully
  ```
  Example: www.google.com → ✓ OK (45.2ms)
  ```

- 🔵 **Blue (Cached)** - Response from cache
  ```
  Example: www.google.com → 💾 CACHED (1.2ms)
  ```

- 🔴 **Red (Blocked)** - Domain blocked
  ```
  Example: ads.doubleclick.net → 🚫 BLOCKED
  ```

- 🟠 **Orange (Failed)** - Query failed/timeout
  ```
  Example: invalid-domain.xyz → ⏱ Timeout
  ```

### Filtering Options

#### 1. Text Filter

Search for specific domains or IPs:

```
Filter box: "google"
Results: Shows only queries containing "google"
  - www.google.com
  - ads.google.com
  - fonts.googleapis.com
```

#### 2. Type Filter

Filter by DNS record type:

**Available Types:**
- **All** - Show all queries
- **A** - IPv4 address records
- **AAAA** - IPv6 address records
- **CNAME** - Canonical name records
- **MX** - Mail exchange records
- **TXT** - Text records

**Example Use:**
```
Type: A
Shows only: IPv4 address lookups
```

#### 3. Clear Filter

Click "Clear Filter" button to reset all filters.

### Interpreting Query Details

#### Success Response
```
Details: ✓ OK (45.2ms)
Meaning: Query resolved in 45.2 milliseconds
```

#### Cached Response
```
Details: 💾 CACHED (1.2ms)
Meaning: Response served from cache (very fast)
```

#### Blocked
```
Details: 🚫 BLOCKED
Meaning: Domain in blocklist, query denied
```

#### Timeout
```
Details: ⏱ Timeout
Meaning: Upstream DNS didn't respond in time
```

#### Error
```
Details: ❌ Error: Connection refused
Meaning: Network error occurred
```

---

## 📊 Statistics & Analytics Tab

View comprehensive network analytics and visualizations.

### Overview Metrics

Located at the top of the statistics tab:

```
📊 QUICK STATS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Queries: 5,234
  ✓ Successful: 4,890 (93.4%)
  ✗ Failed: 89 (1.7%)
  🚫 Blocked: 255 (4.9%)
  💾 Cached: 3,128 (59.8%)

Cache Hit Rate: 59.8% (3128/5234 hits)
Cache Size: 1,456 entries
```

### Detailed Statistics

#### 1. Overview Section
```
📊 OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total DNS Queries: 5,234
  ✓ Successful: 4,890 (93.4%)
  ✗ Failed: 89 (1.7%)
  🚫 Blocked: 255 (4.9%)
  💾 Cached: 3,128 (59.8%)

Time Range: 2026-02-03 10:00:00 to 2026-02-03 16:30:00
Unique IPs: 12 | Unique Domains: 1,567
```

#### 2. Top Active Devices
```
🌐 TOP ACTIVE DEVICES (by query count)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 192.168.1.105   │ 2,456 queries (46.9%) ████████████████
2. 192.168.1.108   │ 1,234 queries (23.6%) ████████
3. 192.168.1.110   │   890 queries (17.0%) ██████
```

**Interpretation:**
- Device at 192.168.1.105 is most active
- Could be a computer or smartphone
- High query count may indicate:
  - Heavy internet usage
  - Automated processes
  - Potential issue (if excessive)

#### 3. Top Requested Domains
```
📱 TOP REQUESTED DOMAINS/SERVICES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. www.google.com                    │  567 (10.8%)
2. fonts.googleapis.com              │  234 (4.5%)
3. api.weather.com                   │  189 (3.6%)
```

**Analysis:**
- Google services most popular (expected)
- Font loading (web browsing activity)
- Weather API (app checking weather)

#### 4. Query Type Breakdown
```
🔍 QUERY TYPE BREAKDOWN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A          │ 4,567 queries (87.3%) ██████████████████
AAAA       │   456 queries ( 8.7%) ██
CNAME      │   123 queries ( 2.4%) 
MX         │    67 queries ( 1.3%) 
TXT        │    21 queries ( 0.4%) 
```

**Understanding Types:**
- **A records (87%)** - Standard IPv4 lookups (most common)
- **AAAA records (9%)** - IPv6 lookups (modern devices)
- **CNAME (2%)** - Aliases/redirects
- **MX (1%)** - Email server lookups
- **TXT (<1%)** - Various metadata

#### 5. Performance Insights
```
💡 PERFORMANCE INSIGHTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cache Efficiency: 59.8% of queries served from cache
Security: 4.9% of queries blocked by filters

✓ Great cache performance! Reducing network load.
✓ Blocklist actively protecting your network.
```

### Visual Charts

#### Chart 1: Query Types Distribution (Pie Chart)

Shows percentage breakdown of DNS record types.

**Reading the Chart:**
- Larger slices = more common query types
- Typically dominated by A records (IPv4)
- AAAA growing as IPv6 adoption increases

#### Chart 2: Top 10 Requested Domains (Bar Chart)

Horizontal bar chart showing most popular domains.

**Insights:**
- Longest bars = most frequently queried
- Helps identify:
  - Popular services in your network
  - Potentially unnecessary requests
  - Candidates for caching optimization

#### Chart 3: Top Active IPs (Visual in some views)

Shows which devices make most queries.

**Use Cases:**
- Identify heavy users
- Detect unusual activity
- Monitor IoT devices

### Auto-Refresh

Statistics automatically refresh when you:
1. Switch to the Statistics tab
2. Click the refresh button (if available)

**Note:** Charts rebuild each time to show current data.

---

## 🚫 Blocklist Manager

Control which domains are allowed or blocked in your network.

### Understanding Blocklists vs Allowlists

| List Type | Purpose | Priority |
|-----------|---------|----------|
| **Blocklist** | Domains to block | Normal |
| **Allowlist** | Always allow (override blocklist) | High |

**Example:**
```
Blocklist: google.com
Allowlist: mail.google.com

Result:
❌ www.google.com → BLOCKED
✓ mail.google.com → ALLOWED (allowlist override)
```

### Adding Blocked Domains

#### Method 1: Manual Entry

1. Click "➕ Add Blocked Domain"
2. Enter domain name:
   ```
   Input: ads.example.com
   ```
3. Click OK
4. Domain appears in blocked list

#### Method 2: Load Default List

1. Click "🔄 Load Default Ads/Trackers"
2. Pre-configured list loads automatically
3. Includes common ad networks and trackers

**Default Blocklist Includes:**
- doubleclick.net (Google ads)
- googleadservices.com (Google ad services)
- googlesyndication.com (Google syndication)
- scorecardresearch.com (Tracking)
- taboola.com (Content recommendations)
- outbrain.com (Content recommendations)
- Many more...

### Wildcard Blocking

NetGuard supports automatic subdomain blocking:

**Example:**
```
Block: doubleclick.net

Automatically blocks:
✓ doubleclick.net
✓ ads.doubleclick.net
✓ tracking.doubleclick.net
✓ any.subdomain.doubleclick.net
```

**Important:** Only blocks subdomains, not superdomains:
```
Block: ads.example.com

Blocks: ads.example.com
Does NOT block: example.com (parent domain)
```

### Adding Allowed Domains

Use allowlist to override blocklist:

1. Click "➕ Add Allowed Domain"
2. Enter domain:
   ```
   Input: important-site.com
   ```
3. Click OK
4. Domain added to allowlist

**Use Case:**
```
Scenario: Blocked google.com but need Google Drive

Solution:
Blocklist: google.com
Allowlist: drive.google.com

Result:
❌ www.google.com → BLOCKED
✓ drive.google.com → ALLOWED
```

### Removing Domains

#### Remove from Blocklist:
1. Select domain in blocked list
2. Click "Remove Selected"
3. Domain removed

#### Remove from Allowlist:
1. Select domain in allowed list
2. Click "Remove Selected"
3. Domain removed

### Best Practices

#### Recommended Domains to Block

**Advertising:**
```
doubleclick.net
googlesyndication.com
advertising.com
adnxs.com
```

**Tracking:**
```
google-analytics.com
googletagmanager.com
hotjar.com
mouseflow.com
```

**Social Media Trackers:**
```
facebook.com (if you don't use Facebook)
connect.facebook.net
twitter.com (if you don't use Twitter)
```

⚠️ **Warning:** Don't block domains you need!

#### Domains to Allowlist

**Essential Services:**
```
Important work domains
Banking websites
Government websites
Healthcare portals
```

**Tip:** If something stops working after blocking, check logs and add to allowlist.

---

## ⚠️ Alerts Monitor

Real-time security threat detection and notification.

### Alert Types

#### 1. EXCESSIVE_QUERIES (High Severity)

**Trigger:** More than 100 queries/minute from single IP

**Alert Example:**
```
[14:23:45] [HIGH] Excessive queries from 192.168.1.105: 
156 queries in 1 minute
```

**Possible Causes:**
- Malware infection
- DDoS attack attempt
- Misconfigured application
- Bot activity

**Actions:**
1. Identify device at IP address
2. Check device for malware
3. Investigate running applications
4. Consider blocking IP temporarily

#### 2. SUSPICIOUS_DOMAIN (Medium Severity)

**Trigger:** Domain contains suspicious keywords

**Keywords Monitored:**
- torrent
- crack
- keygen
- malware
- phishing
- ransomware
- trojan

**Alert Example:**
```
[14:25:30] [MEDIUM] Suspicious domain queried: 
crack-software.xyz from 192.168.1.108
```

**Actions:**
1. Identify device
2. Talk to user about safe browsing
3. Add domain to blocklist
4. Run antivirus scan

#### 3. DGA_DETECTED (High Severity - Future)

**Trigger:** Potential Domain Generation Algorithm detected

**Characteristics:**
- Random-looking domain names
- Unusual TLDs
- High entropy strings

### Alert Display

Alerts appear in the Alerts tab with:
- Timestamp
- Severity level (color-coded)
- IP address involved
- Description
- Recommended action

**Color Coding:**
- 🔴 **Red** - High severity (immediate action needed)
- 🟡 **Yellow** - Medium severity (investigate soon)
- 🔵 **Blue** - Low severity (informational)

### Managing Alerts

#### View Alert Details

Click on alert to see full information:
```
Alert ID: 12345
Time: 2026-02-03 14:23:45
Type: EXCESSIVE_QUERIES
Severity: HIGH
Source IP: 192.168.1.105
Details: 156 queries in 60 seconds
Queries: [list of domains]
```

#### Clear Alerts

1. Click "Clear Alerts" button
2. Confirm action
3. All alerts removed from display

**Note:** Alerts are not logged to file, only displayed in UI.

### Alert Response Workflow

```
Alert Detected
    ↓
Identify Device (by IP)
    ↓
Assess Threat Level
    ↓
├─ High: Immediate action
│  ├─ Disconnect device
│  ├─ Run malware scan
│  └─ Change passwords
│
├─ Medium: Investigate
│  ├─ Check device activity
│  ├─ Review logs
│  └─ Monitor further
│
└─ Low: Document
   └─ Add to blocklist if needed
```

---

## 🔧 Menu Options

### File Menu

#### Export Logs (CSV)

Export all logs to CSV file for external analysis.

**Steps:**
1. File → Export Logs (CSV)
2. Choose location and filename
3. Click Save

**CSV Format:**
```csv
Timestamp,Source IP,Query Domain,Type,Details,Success,Blocked,Cached
2026-02-03 14:23:45.123,192.168.1.105,www.google.com,A,✓ OK (45ms),True,False,False
```

**Use Cases:**
- Long-term analysis
- Import to Excel/Google Sheets
- Data mining
- Compliance reporting

#### Clear Logs

Remove all logs from memory and display.

**Warning:** This action cannot be undone!

**Steps:**
1. File → Clear Logs
2. Confirm "Yes"
3. Logs cleared

**When to Use:**
- Fresh start for testing
- Memory management
- Privacy (remove history)

#### Exit

Close the application properly.

**Steps:**
1. File → Exit
2. DNS server stops gracefully
3. Application closes

### View Menu

#### Pause/Resume

Temporarily stop logging new queries.

**Paused State:**
- New queries still processed
- DNS service continues
- Logging to UI paused
- Status bar shows "PAUSED"

**Use Cases:**
- Examine specific logs
- Take screenshots
- Reduce CPU usage temporarily

### Cache Menu

#### Clear Cache

Remove all cached DNS responses.

**Effect:**
- Next queries will go to upstream
- Response times temporarily slower
- Cache rebuilds over time

**When to Use:**
- Testing changes
- Troubleshooting
- Force fresh lookups

#### Cache Statistics

View detailed cache performance metrics.

**Display:**
```
DNS Cache Statistics:

Cache Size: 1,456 entries
Cache Hits: 3,128
Cache Misses: 2,106
Hit Rate: 59.8%

A higher hit rate means better performance!
```

**Interpreting:**
- Hit Rate >50%: Excellent
- Hit Rate 30-50%: Good
- Hit Rate <30%: Room for improvement

---

## 🎓 Advanced Usage

### Scenario 1: Family Internet Monitoring

**Goal:** Monitor and control family internet usage

**Setup:**
1. Configure all family devices to use NetGuard
2. Load default ad/tracker blocklist
3. Add inappropriate content domains to blocklist
4. Monitor statistics for usage patterns

**Domains to Block:**
```
# Social media during study time
facebook.com
instagram.com
tiktok.com
snapchat.com

# Gaming during homework time
steam-api.com
epicgames.com
```

**Monitoring:**
- Check Top Active Devices to see who's online
- Review Top Domains for content access
- Monitor alerts for suspicious activity

### Scenario 2: Small Business Network Security

**Goal:** Protect business network from threats

**Setup:**
1. Deploy on network gateway
2. Extensive blocklist (ads, trackers, malware)
3. Allowlist for business-critical services
4. Enable all security alerts

**Critical Allowlist:**
```
# Business services
office365.com
salesforce.com
slack.com
zoom.us
```

**Monitoring:**
- Daily review of alerts
- Weekly statistics analysis
- Monthly CSV export for compliance

### Scenario 3: Development/Testing

**Goal:** Test applications and services

**Setup:**
1. Minimal blocklist
2. Extensive logging
3. Pause/resume as needed
4. Export logs for analysis

**Workflow:**
```
1. Clear logs
2. Run application test
3. Pause logging
4. Review specific DNS queries
5. Export to CSV
6. Analyze in external tool
```

### Scenario 4: Privacy-focused Home Network

**Goal:** Maximum privacy and ad-blocking

**Setup:**
1. Extensive blocklist:
   - All ad networks
   - All trackers
   - Social media trackers
   - Analytics services
2. Allowlist only essential services
3. Regular cache clearing

**Blocklist Categories:**
```
# Advertising (50+ domains)
# Tracking (30+ domains)
# Analytics (20+ domains)
# Social trackers (15+ domains)
```

---

## 🎯 Best Practices

### Daily Operations

✅ **DO:**
- Monitor status bar for anomalies
- Check alerts tab periodically
- Review top domains weekly
- Export logs monthly
- Keep blocklist updated

❌ **DON'T:**
- Block without understanding
- Ignore high-severity alerts
- Leave cache indefinitely
- Forget to backup blocklists

### Performance Optimization

#### Maximize Cache Hit Rate

1. **Don't Clear Cache Frequently**
   - Let it build over time
   - Only clear when necessary

2. **Monitor Popular Domains**
   - These benefit most from caching
   - Verify they're being cached

3. **Adjust TTL if Needed**
   - Edit `dns_server.py`
   - Increase for static sites
   - Decrease for dynamic content

#### Reduce Memory Usage

1. **Lower Log Retention**
   ```python
   # dns_server.py
   if len(all_logs) > 5000:  # Lower from 10000
   ```

2. **Clear Logs Regularly**
   - Daily or weekly
   - Export before clearing

3. **Restart Application**
   - Weekly or monthly
   - Frees accumulated memory

### Security Best Practices

#### Blocklist Management

1. **Start with Defaults**
   - Load default ad/tracker list
   - Test for a week
   - Adjust as needed

2. **Gradual Expansion**
   - Add domains slowly
   - Test after each addition
   - Note what broke

3. **Maintain Allowlist**
   - Document important domains
   - Add before blocking parent
   - Review quarterly

#### Alert Response

1. **Prioritize by Severity**
   ```
   HIGH → Immediate response
   MEDIUM → Investigate within 24h
   LOW → Review weekly
   ```

2. **Document Actions**
   - Keep response log
   - Note false positives
   - Track patterns

3. **Regular Reviews**
   - Daily quick scan
   - Weekly deep dive
   - Monthly summary

### Data Management

#### Export Strategy

**Daily:**
```
- Quick stats screenshot
- Alert summary
```

**Weekly:**
```
- Full CSV export
- Cache statistics
- Blocklist backup
```

**Monthly:**
```
- Comprehensive analysis
- Trend identification
- Blocklist optimization
```

#### Backup Important Data

1. **Blocklists**
   - Export to text file
   - Keep in version control
   - Document changes

2. **Critical Logs**
   - Export security incidents
   - Archive monthly exports
   - Retain per compliance needs

---

## 🔍 Use Cases

### Educational Institutions

**Scenario:** School network monitoring

**Benefits:**
- Block inappropriate content
- Monitor student activity
- Improve network performance (caching)
- Identify security threats

**Configuration:**
```
Blocklist:
- Social media (during classes)
- Gaming sites
- Streaming services
- Known malware domains

Allowlist:
- Educational resources
- Library services
- School portals
```

### Home Networks

**Scenario:** Family internet safety

**Benefits:**
- Parental controls
- Ad blocking
- Privacy protection
- Bandwidth monitoring

**Configuration:**
```
Blocklist:
- Ads and trackers
- Adult content (if desired)
- Time-based restrictions

Monitoring:
- Daily usage patterns
- Device identification
```

### Small Offices

**Scenario:** Business network security

**Benefits:**
- Malware protection
- Productivity monitoring
- Compliance logging
- Cost reduction (bandwidth)

**Configuration:**
```
Blocklist:
- Malware domains
- Non-work sites
- Excessive streaming

Allowlist:
- Business applications
- Cloud services
- Email servers
```

### Developers

**Scenario:** Application testing

**Benefits:**
- Debug DNS issues
- Monitor API calls
- Test blocklists
- Performance analysis

**Configuration:**
```
Minimal blocking
Detailed logging
CSV export for analysis
Cache testing
```

---

## 💡 Tips & Tricks

### Keyboard Shortcuts

*Note: Standard application shortcuts*
- `Ctrl+Q` - Quit (on some systems)
- `F5` - Refresh (in some tabs)

### Quick Filters

Create mental shortcuts for common filters:

```
Filter "google" → See all Google services
Filter ".edu" → See educational sites
Filter "192.168.1.105" → See one device
```

### Reading Patterns

Learn to spot patterns quickly:

**Normal Traffic:**
```
Mix of A and AAAA records
Familiar domain names
Consistent query rate
Mix of cached and fresh
```

**Suspicious Traffic:**
```
Excessive queries from one IP
Random-looking domains
All fresh (no caching)
Unusual query types
```

### Efficient Blocklist Building

1. Start with top requested domains
2. Identify unwanted patterns
3. Block parent domains (leverage wildcards)
4. Test before committing
5. Document decisions

---

## ❓ FAQ

### Q: Will this slow down my internet?

**A:** No! In fact, caching speeds it up by ~95% for repeated queries.

### Q: Can I run this on multiple computers?

**A:** Yes, but only one per network segment (both would compete for port 53).

### Q: Does it work with VPN?

**A:** Yes, configure VPN device to use NetGuard as DNS server.

### Q: How much data does it use?

**A:** Minimal. DNS queries are very small (typically <100 bytes).

### Q: Can it block YouTube ads?

**A:** Partially. YouTube serves some ads from same domains as content, making blocking difficult.

### Q: Is my data private?

**A:** Yes! All data stays on your computer. Nothing is sent to external servers except upstream DNS queries.

---

## 🆘 Getting Help

If you need assistance:

1. Check this usage guide
2. Review [INSTALLATION.md](INSTALLATION.md)
3. Search [GitHub Issues](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/issues)
4. Create new issue with details

---

<div align="center">

**Happy Monitoring!** 🛡️

[Back to README](README.md) | [Installation Guide](INSTALLATION.md) | [Report Issue](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/issues)

</div>
