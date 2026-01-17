# NetGuard-DNS-Monitor
Real-time DNS monitoring with intelligent threat detection and ad-blocking

Developed as a Final Year Cybersecurity Project demonstrating advanced network security concepts, threat detection algorithms, and system optimization techniques.

Features

Core Monitoring

Real-time DNS Query Logging - Monitor all DNS queries across your network
Live Traffic Analysis - Instant visibility into network activity
Advanced Filtering - Search and filter by domain, IP, or query type
Visual Statistics - Comprehensive charts and graphs for traffic analysis.


Analytics & Reporting

Comprehensive Statistics - Traffic patterns, top domains, device activity
Visual Data Representation - Pie charts, bar graphs, trend analysis
CSV Export - Export logs for external analysis
Historical Tracking - Monitor trends over time


Quick Start
Prerequisites

Python 3.7 or higher
Administrator/root privileges (required for port 53)
Network access

Installation

Clone the repository

bashgit clone https://github.com/yourusername/netguard-dns-monitor.git
cd netguard-dns-monitor

Install dependencies

bashpip install -r requirements.txt

Run the application

Windows (Administrator):
bash# Right-click Command Prompt → "Run as Administrator"
python src/main.py
Linux/Mac (sudo):
bashsudo python3 src/main.py
Network Configuration
Configure devices to use your computer's IP as DNS server:
Find your IP address:

Windows: ipconfig
Linux/Mac: ifconfig or ip addr

Configure DNS on devices:

Set Primary DNS to your computer's IP
Set Secondary DNS to 8.8.8.8 (backup)