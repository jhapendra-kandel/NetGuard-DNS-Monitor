# ⚡ Quick Setup - Get Running in 5 Minutes!

Hey! So you want to try NetGuard but don't want to read a whole manual? Cool, I got you. Follow these steps and you'll be monitoring your network in literally 5 minutes.

---

## ✅ What You Need

- Computer with Python 3.8+ installed -- may not work properly for python verison 3.14 ++ in windows 
- Admin/sudo access (you'll need it!)
- Internet connection
- That's it!

---

## 🚀 Let's Go!

### Step 1: Clone This Thing

Open your terminal/command prompt and paste this:

```bash
git clone https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor.git
cd NetGuard-DNS-Monitor
```

Don't have Git? No problem! Just download the ZIP from GitHub and extract it.

---

### Step 2: Install Dependencies

Just one command:

```bash
pip install -r requirements.txt
```

This installs all the libraries needed. Takes like 30 seconds.

---

### Step 3: Run It!

**On Windows:**
1. Right-click Command Prompt → "Run as Administrator"
2. Navigate to your project folder
3. Run:
```cmd
python main.py
```

**On Mac/Linux:**
```bash
sudo python3 main.py
```

You should see this cool banner:
```
╔══════════════════════════════════════╗
║   🛡️  NetGuard DNS Monitor  🛡️      ║
╚══════════════════════════════════════╝

✓ DNS Server running on port 53
✓ Cache enabled
✓ Blocklist enabled
```

If you see that, you're good to go! ✨

---

## 📱 Step 4: Configure Your Phone/Laptop

Now the fun part - actually using it!

### Find Your Computer's IP

**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" (something like 192.168.1.100)

**Mac/Linux:**
```bash
hostname -I
```
First address shown is your IP

### Set Up Your Device

I'll show you for a phone (laptop is similar):

1. **Go to WiFi Settings**
2. **Tap your WiFi network**
3. **Find DNS settings** (might be under "Advanced")
4. **Change to Manual/Static**
5. **Set Primary DNS:** Your computer's IP (e.g., 192.168.1.100)
6. **Set Secondary DNS:** 8.8.8.8 -- NOT RECOMENDED (FOR BACKUPS ONLY)
7. **Save**

---

## 🎉 Test It!

1. On your phone, open any website
2. Look at NetGuard on your computer
3. You should see DNS queries appearing!

**Color meanings:**
- 🟢 Green = Successful query
- 🔵 Blue = From cache (fast!)
- 🔴 Red = Blocked
- ⚫ Grey = Failed

---

## 🚫 Want to Block Ads?

Easy!

1. Click "Blocklist Manager" tab
2. Click "Load Default Ads/Trackers"
3. Boom! 100+ ad domains blocked

Now browse and watch ads get stopped before they even load 😎

---

## ⚠️ Troubleshooting

### "Permission Denied" Error
- **Windows:** Run as Administrator
- **Mac/Linux:** Use `sudo`

### "Port 53 Already in Use"
Someone else is using that port. Usually it's:
- Another DNS service
- Docker
- System DNS service

**Fix:** Stop that service first

### "ModuleNotFoundError"
You forgot Step 2! Run:
```bash
pip install -r requirements.txt
```

### Not Seeing Any Queries?
Check:
- Did you set DNS on your device correctly?
- Is NetGuard actually running?
- Did your computer's IP change?

---

## 📚 Want More Details?

Check these out:
- [Full Installation Guide](INSTALLATION.md) - Detailed setup for each OS
- [Usage Guide](USAGE.md) - How to use every feature
- [YouTube Tutorial](#) - Video walkthrough (way easier!)

---

## 💡 Quick Tips

1. **Load Blocklist:** Block ads right away
2. **Check Statistics:** After a few hours of use
3. **Export Logs:** Save interesting traffic patterns
4. **Pause Logging:** When doing sensitive stuff
5. **Cache On:** Keep it on for faster internet

---

## 🎯 What's Next?

Now that it's running:

1. **Browse around** - See what gets logged
2. **Block some ads** - Add domains to blocklist
3. **Check stats** - See your network patterns
4. **Set alerts** - Get notified of weird stuff
5. **Explore features** - Try everything!

---

<div align="center">

**That's it! You're now monitoring your network!** 🎉

If you get stuck, check the full docs or open an issue on GitHub.

**Happy monitoring!** 🛡️

[Back to Main README](README.md) | [Detailed Installation](INSTALLATION.md)

</div>