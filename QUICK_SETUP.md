# ⚡ Quick Setup Guide - NetGuard DNS Monitor

Get up and running in 5 minutes!

---

## 🚀 Prerequisites

- Python 3.8+ installed
- Administrator/sudo access
- Internet connection

---

## 📥 Installation (3 Steps)

### 1. Clone Repository

```bash
git clone https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor.git
cd NetGuard-DNS-Monitor
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Application

**Windows (as Administrator):**
```cmd
python main.py
```

**Linux/macOS:**
```bash
sudo python3 main.py
```

---

## 🔧 Configure Device DNS

### Find Your Computer's IP

**Windows:**
```cmd
ipconfig
```

**Linux/macOS:**
```bash
hostname -I
# or
ip addr show
```

### Set DNS on Client Device

1. Go to Network Settings
2. Set **Primary DNS** to your computer's IP (e.g., 192.168.1.100)
3. Set **Secondary DNS** to 8.8.8.8
4. Save and reconnect

---

## ✅ Verify It's Working

1. Browse any website on your configured device
2. Check NetGuard **Live Logs** tab
3. You should see DNS queries appearing in real-time!

---

## 🎯 Next Steps

1. **Block Ads:** Go to Blocklist tab → Click "Load Default Ads/Trackers"
2. **Monitor Stats:** Check Statistics tab for network insights
3. **Review Alerts:** Watch Alerts tab for security warnings

---

## 📚 Full Documentation

- [README.md](README.md) - Complete project overview
- [INSTALLATION.md](INSTALLATION.md) - Detailed installation guide
- [USAGE.md](USAGE.md) - User manual
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute

---

## 🆘 Having Issues?

**Port 53 Error:**
- Run as Administrator (Windows) or sudo (Linux/macOS)

**No Queries Showing:**
- Check device DNS settings
- Verify firewall allows UDP port 53
- Restart application

**Need More Help:**
- [Troubleshooting Guide](INSTALLATION.md#troubleshooting)
- [GitHub Issues](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/issues)

---

<div align="center">

**That's it! You're all set!** 🎉

Happy Monitoring! 🛡️

</div>
