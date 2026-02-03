# 📦 Installation Guide - NetGuard DNS Monitor

Complete installation instructions for Windows, Linux, and macOS.

---

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Pre-installation Checklist](#pre-installation-checklist)
- [Installation Methods](#installation-methods)
  - [Windows Installation](#windows-installation)
  - [Linux Installation](#linux-installation)
  - [macOS Installation](#macos-installation)
- [Post-installation Setup](#post-installation-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## 💻 System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|------------|
| **OS** | Windows 10/11, Ubuntu 18.04+, macOS 10.14+ |
| **Python** | 3.8 or higher |
| **RAM** | 512 MB (1 GB recommended) |
| **Disk Space** | 100 MB |
| **Network** | Active network connection |
| **Privileges** | Administrator/root access |

### Software Dependencies

- Python 3.8+
- pip (Python package manager)
- tkinter (usually included with Python)
- Git (for cloning repository)

---

## ✅ Pre-installation Checklist

Before installation, ensure you have:

- [ ] Administrator/root access to your computer
- [ ] Python 3.8 or higher installed
- [ ] Internet connection for downloading dependencies
- [ ] Firewall configured to allow UDP port 53
- [ ] Git installed (or download ZIP from GitHub)

### Check Python Version

**Windows:**
```cmd
python --version
```

**Linux/macOS:**
```bash
python3 --version
```

Expected output: `Python 3.8.x` or higher

### Check pip Installation

```bash
pip --version
# or
pip3 --version
```

---

## 🪟 Windows Installation

### Step 1: Install Python (if not installed)

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. ✅ **IMPORTANT:** Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

### Step 2: Install Git (Optional)

**Option A: Using Git**
1. Download Git from [git-scm.com](https://git-scm.com/download/win)
2. Install with default settings
3. Open Command Prompt

**Option B: Download ZIP**
1. Visit [GitHub Repository](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor)
2. Click "Code" → "Download ZIP"
3. Extract to desired location

### Step 3: Clone/Download Project

**Using Git:**
```cmd
cd C:\Users\YourName\Documents
git clone https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor.git
cd NetGuard-DNS-Monitor
```

**Using ZIP:**
- Extract to `C:\Users\YourName\Documents\NetGuard-DNS-Monitor`
- Open Command Prompt in that folder

### Step 4: Create Virtual Environment (Recommended)

```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your command prompt.

### Step 5: Install Dependencies

```cmd
pip install -r requirements.txt
```

Expected output:
```
Successfully installed dnslib-0.9.23 matplotlib-3.7.1 ...
```

### Step 6: Configure Windows Firewall

**Method 1: Automatic (Run as Admin)**
```cmd
netsh advfirewall firewall add rule name="NetGuard DNS" dir=in action=allow protocol=UDP localport=53
```

**Method 2: Manual**
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Select "Port" → Next
5. Select "UDP" → Enter "53" → Next
6. Select "Allow the connection" → Next
7. Check all profiles → Next
8. Name: "NetGuard DNS" → Finish

### Step 7: Run the Application

```cmd
# MUST run as Administrator
# Right-click Command Prompt → "Run as administrator"
cd C:\Users\YourName\Documents\NetGuard-DNS-Monitor
python main.py
```

---

## 🐧 Linux Installation

### Step 1: Update Package Manager

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt upgrade
```

**Fedora/RHEL:**
```bash
sudo dnf update
```

**Arch Linux:**
```bash
sudo pacman -Syu
```

### Step 2: Install Python and Dependencies

**Ubuntu/Debian:**
```bash
sudo apt install python3 python3-pip python3-venv python3-tk git
```

**Fedora/RHEL:**
```bash
sudo dnf install python3 python3-pip python3-tkinter git
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip tk git
```

### Step 3: Clone Repository

```bash
cd ~/Documents
git clone https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor.git
cd NetGuard-DNS-Monitor
```

### Step 4: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Configure Firewall

**Ubuntu (UFW):**
```bash
sudo ufw allow 53/udp
sudo ufw reload
```

**Fedora/RHEL (firewalld):**
```bash
sudo firewall-cmd --permanent --add-port=53/udp
sudo firewall-cmd --reload
```

**Arch Linux (iptables):**
```bash
sudo iptables -A INPUT -p udp --dport 53 -j ACCEPT
sudo iptables-save > /etc/iptables/iptables.rules
```

### Step 7: Run the Application

```bash
sudo python3 main.py
```

**Note:** `sudo` is required to bind to port 53.

---

## 🍎 macOS Installation

### Step 1: Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Python

```bash
brew install python@3.11
brew install python-tk
```

Verify installation:
```bash
python3 --version
```

### Step 3: Install Git

```bash
brew install git
```

### Step 4: Clone Repository

```bash
cd ~/Documents
git clone https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor.git
cd NetGuard-DNS-Monitor
```

### Step 5: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 6: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 7: Configure Firewall

macOS firewall usually allows local services automatically. If issues occur:

1. System Preferences → Security & Privacy → Firewall
2. Click "Firewall Options"
3. Add Python to allowed applications

### Step 8: Run the Application

```bash
sudo python3 main.py
```

Enter your macOS password when prompted.

---

## 🔧 Post-installation Setup

### 1. Find Your Computer's IP Address

**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" under your active network adapter.

**Linux/macOS:**
```bash
ip addr show
# or
ifconfig
```
Look for `inet` address (e.g., 192.168.1.100).

### 2. Configure Client Devices

#### Windows Device:
1. Settings → Network & Internet → Wi-Fi (or Ethernet)
2. Click your connection → Properties
3. IP Settings → Edit
4. Change to "Manual"
5. IPv4: On
6. DNS Primary: `<your-computer-ip>`
7. DNS Secondary: `8.8.8.8`
8. Save

#### Android Device:
1. Settings → Wi-Fi
2. Long press your network → Modify
3. Advanced options → IP settings
4. Change to "Static"
5. DNS 1: `<your-computer-ip>`
6. DNS 2: `8.8.8.8`
7. Save

#### iOS Device:
1. Settings → Wi-Fi
2. Tap (i) next to your network
3. Configure DNS → Manual
4. Add Server: `<your-computer-ip>`
5. Save

#### macOS Device:
1. System Preferences → Network
2. Select your connection → Advanced
3. DNS tab → Click +
4. Add: `<your-computer-ip>`
5. OK → Apply

### 3. Load Default Blocklist

1. Run NetGuard DNS Monitor
2. Click "Blocklist Manager" tab
3. Click "🔄 Load Default Ads/Trackers"
4. Verify domains appear in blocked list

---

## ✔️ Verification

### Test 1: Check Application Startup

```bash
sudo python3 main.py
```

Expected output:
```
╔══════════════════════════════════════════════════════════════╗
║        🛡️  DNS NETWORK ACTIVITY MONITOR v2.0  🛡️            ║
╚══════════════════════════════════════════════════════════════╝

✓ DNS Server running on port 53
✓ Forwarding to 8.8.8.8
✓ Cache enabled
✓ Blocklist enabled
✓ Anomaly detection active
```

### Test 2: Verify DNS Resolution

From a configured client device:

**Windows:**
```cmd
nslookup google.com <your-computer-ip>
```

**Linux/macOS:**
```bash
dig @<your-computer-ip> google.com
```

Expected: Successful resolution + entry in Live Logs tab

### Test 3: Test Blocking

1. Add `example.com` to blocklist
2. From client device, visit `http://example.com`
3. Should see "Server not found" error
4. Check Live Logs: entry should be RED (blocked)

### Test 4: Cache Functionality

1. Visit `google.com` on client device
2. Check Live Logs: First query shows ✓ OK
3. Visit `google.com` again immediately
4. Check Live Logs: Second query shows 💾 CACHED

---

## 🐛 Troubleshooting

### Issue 1: "Permission Denied" Error

**Problem:**
```
❌ Permission denied! Run as administrator/sudo
```

**Solutions:**

**Windows:**
- Right-click Command Prompt
- Select "Run as administrator"
- Navigate to project folder
- Run `python main.py`

**Linux/macOS:**
```bash
sudo python3 main.py
```

### Issue 2: "Address Already in Use"

**Problem:**
```
❌ Cannot bind to port 53: Address already in use
```

**Solutions:**

**Windows:**
```cmd
# Find process using port 53
netstat -ano | findstr :53
# Kill process (replace PID)
taskkill /PID <process_id> /F
```

**Linux/macOS:**
```bash
# Find process
sudo lsof -i :53
# Kill process
sudo kill -9 <PID>
```

### Issue 3: ModuleNotFoundError

**Problem:**
```
ModuleNotFoundError: No module named 'dnslib'
```

**Solutions:**

1. Verify virtual environment is activated:
   ```bash
   # You should see (venv) in prompt
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. If still failing, install manually:
   ```bash
   pip install dnslib matplotlib
   ```

### Issue 4: tkinter Not Found

**Problem:**
```
ModuleNotFoundError: No module named 'tkinter'
```

**Solutions:**

**Ubuntu/Debian:**
```bash
sudo apt install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**macOS:**
```bash
brew install python-tk
```

### Issue 5: No Queries Appearing

**Problem:** Application runs but no DNS queries show in Live Logs.

**Checklist:**

1. ✅ Client device DNS configured correctly?
2. ✅ Firewall allows UDP port 53?
3. ✅ Computer IP hasn't changed?
4. ✅ Application running as admin/sudo?

**Debug Steps:**

```bash
# Test DNS server from same computer
nslookup google.com 127.0.0.1

# Check if port 53 is listening
# Windows:
netstat -an | findstr :53

# Linux/macOS:
sudo netstat -tulpn | grep :53
```

### Issue 6: High Memory Usage

**Problem:** Application using too much RAM.

**Solutions:**

1. Reduce log retention:
   ```python
   # Edit dns_server.py, line ~230
   if len(all_logs) > 5000:  # Reduce from 10000
   ```

2. Clear logs periodically:
   - File menu → Clear Logs

3. Restart application after clearing

### Issue 7: Firewall Blocking

**Windows:**
- Windows Defender may prompt for access
- Click "Allow access" when prompted
- Or manually add rule (see Step 6 in Windows Installation)

**Linux:**
- Check SELinux: `sudo setenforce 0` (temporary)
- Check AppArmor: `sudo aa-status`

**macOS:**
- System Preferences → Security & Privacy
- Allow Python in Firewall settings

---

## 📚 Additional Resources

### Official Documentation
- [Python Installation Guide](https://www.python.org/downloads/)
- [Git Documentation](https://git-scm.com/doc)
- [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html)

### Community Support
- [GitHub Issues](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/issues)
- [GitHub Discussions](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/discussions)

### Video Tutorials
- [YouTube: DNS Server Setup](https://youtube.com)
- [YouTube: Python Virtual Environments](https://youtube.com)

---

## 🎯 Next Steps

After successful installation:

1. ✅ Read [USAGE.md](USAGE.md) for detailed usage instructions
2. ✅ Configure blocklists for ad/tracker blocking
3. ✅ Set up alerts for security monitoring
4. ✅ Explore statistics and analytics features

---

## 💬 Need Help?

If you encounter issues not covered here:

1. Check [Troubleshooting](#troubleshooting) section
2. Search [existing issues](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/issues)
3. Create a [new issue](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/issues/new) with:
   - Operating system and version
   - Python version
   - Full error message
   - Steps to reproduce

---

<div align="center">

**Installation Complete!** 🎉

[Back to README](README.md) | [Usage Guide](USAGE.md) | [Report Issue](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/issues)

</div>
