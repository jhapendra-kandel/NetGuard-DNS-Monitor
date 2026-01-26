# NetGuard DNS Monitor v1.1.0

🛡️ Real-time DNS monitoring with intelligent threat detection and network protection

Developed as a Final Year Cybersecurity Project demonstrating advanced network security concepts, threat detection algorithms, and system optimization techniques.

---

## 🎯 Current Features (v1.1.0)

### Core Functionality
- ✅ **Real-time DNS Query Monitoring** - Live view of all DNS requests
- ✅ **Domain & IP Blocking** - Sinkhole malicious domains and blacklist IPs
- ✅ **Persistent Blocklists** - Auto-save/load from files
- ✅ **Bulk Import** - Import domain lists from text files
- ✅ **Color-coded Logs** - Green (safe), Red (blocked), Orange (failed)

### Analytics & Reporting
- 📊 **Auto-refreshing Statistics** - Updates when tab is selected
- 📈 **Visual Charts** - 3 real-time bar charts:
  - Query Status Distribution
  - Top 10 Active IPs
  - Top 10 Requested Domains
- 📉 **Comprehensive Metrics** - Traffic patterns, security threats, performance
- 💾 **CSV Export** - Export logs for external analysis
- 📋 **Historical Tracking** - Monitor trends over time

### Security Features
- 🛡️ **Domain Blacklisting** - Block malicious/unwanted domains
- 🚫 **IP Blacklisting** - Block traffic from specific IPs
- ⚠️ **Threat Detection** - Identify top blocked domains/IPs
- 📝 **Alert Logging** - All blocked queries logged to alerts.log
- 🔐 **IP Validation** - Prevent invalid IP entries

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Administrator/root privileges (required for port 53)
- Network access

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/NetGuard-DNS-Monitor.git
cd NetGuard-DNS-Monitor
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**

**Windows (Administrator):**
```bash
# Right-click Command Prompt → "Run as Administrator"
python main.py
```

**Linux/Mac (sudo):**
```bash
sudo python3 main.py
```

---

## 📱 Network Configuration

Configure devices to use your computer as DNS server:

1. **Find your computer's IP address:**
   - Windows: `ipconfig`
   - Linux/Mac: `ifconfig` or `ip addr`

2. **Configure DNS on devices:**
   - Set Primary DNS to your computer's IP
   - Set Secondary DNS to 8.8.8.8 (Google DNS as backup)

3. **Example:**
   - Your Computer IP: 192.168.1.100
   - Device DNS Settings: Primary = 192.168.1.100, Secondary = 8.8.8.8

---

## 📖 Usage Guide

### 1. Live Logs Tab
- View real-time DNS queries
- Color codes:
  - 🟢 **Green** = Safe query (forwarded)
  - 🔴 **Red** = Blocked (domain/IP blacklisted)
  - 🟠 **Orange** = Failed (timeout/error)
- **Controls:**
  - ⏸️ Pause/Resume logging
  - 💾 Export to CSV
  - 🗑️ Clear logs

### 2. Statistics Tab
- Auto-refreshes when selected
- Shows comprehensive metrics:
  - Total queries and percentages
  - Top 10 active IPs
  - Top 10 requested domains
  - Security threat analysis
  - Query type distribution
- **Charts:**
  - Status distribution
  - IP activity
  - Domain popularity

### 3. Blocklists Tab

**Domain Blocklist:**
- Manually add domains (e.g., `ads.example.com`)
- Import bulk lists using 📁 Import button
- Remove selected domains
- Auto-saves to `domain_blocklist.txt`

**IP Blacklist:**
- Add IPs in IPv4 format (e.g., `192.168.1.50`)
- Validates IP format automatically
- Remove selected IPs
- Auto-saves to `ip_blacklist.txt`

---

## 📁 Project Structure

```
NetGuard-DNS-Monitor/
├── main.py                    # Application entry point
├── dns_server.py              # DNS proxy server logic
├── gui.py                     # Tkinter GUI interface
├── stats.py                   # Statistics computation
├── requirements.txt           # Python dependencies
├── domain_blocklist.txt       # Saved domain blocklist (auto-created)
├── ip_blacklist.txt          # Saved IP blacklist (auto-created)
├── alerts.log                # Blocked query log (auto-created)
└── README.md                 # This file
```

---

## 🎓 Educational Value

This project demonstrates:

1. **Network Programming** - Socket programming, DNS protocol
2. **Multithreading** - Concurrent request handling
3. **GUI Development** - Tkinter interface design
4. **Data Visualization** - Matplotlib charts
5. **Security Concepts** - DNS filtering, blacklisting
6. **File I/O** - Persistent data storage
7. **Error Handling** - Robust error management
8. **Real-time Systems** - Live monitoring and updates

---

## 🔧 Configuration

### Upstream DNS Server
Default: Google DNS (8.8.8.8)

To change, edit in `dns_server.py`:
```python
UPSTREAM_DNS = '1.1.1.1'  # Cloudflare DNS
```

### Sinkhole IP
Default: 0.0.0.0

To change, edit in `dns_server.py`:
```python
SINKHOLE_IP = '127.0.0.1'  # Localhost
```

### Log Limit
Default: 5000 entries

To change, edit in `dns_server.py`:
```python
if len(all_logs) > 10000:  # Increase to 10000
```

---

## 📊 Sample Blocklist

Create `sample_domains_to_block.txt`:
```
# Ad Networks
doubleclick.net
googlesyndication.com
advertising.com

# Trackers
google-analytics.com
facebook.com

# Malware
malicious-site.com
```

Import via GUI: Blocklists → 📁 Import button

---

## 🐛 Troubleshooting

### Port 53 Permission Error
- **Windows:** Run as Administrator
- **Linux/Mac:** Use `sudo`

### No DNS Queries Showing
1. Check device DNS settings point to your computer
2. Verify firewall allows UDP port 53
3. Check computer IP hasn't changed

### Statistics Not Updating
- Click 🔄 Refresh button
- Switch to another tab and back

### Blocklists Not Working
1. Check domains are correctly formatted
2. Restart application after adding domains
3. Verify alerts.log for blocked attempts

---

## 🚀 Recent Updates (v1.1.0)

### January 26, 2026
- ✅ **Fixed:** Blocklists now fully functional with persistence
- ✅ **Fixed:** Statistics auto-refresh when tab selected
- ✅ **Fixed:** All charts display correctly
- ✅ **Added:** Import domain lists from files
- ✅ **Added:** IP validation for blacklist
- ✅ **Added:** Clear logs function
- ✅ **Added:** Enhanced UI with emojis and colors
- ✅ **Added:** Scrollable statistics view
- ✅ **Added:** Status distribution chart
- ✅ **Improved:** Error handling throughout
- ✅ **Improved:** Save blocklists on exit

### January 25, 2026
- Fixed UnboundLocalError in DNS handler
- Added upstream DNS timeout + retry
- Added pause/resume logging
- Added CSV export
- Improved GUI status bar

---

## 📝 License

MIT License - Feel free to use for educational purposes

---

## 🤝 Contributing

Pull requests welcome! For major changes, please open an issue first.

---

## 📧 Support

For issues or questions:
1. Check troubleshooting section
2. Review alerts.log file
3. Open GitHub issue with error details

---

## ⭐ Acknowledgments

- Built with Python, Tkinter, and Matplotlib
- DNS library: dnslib
- Inspired by Pi-hole and DNS security research

---

**NetGuard DNS Monitor** - Protecting your network, one query at a time 🛡️