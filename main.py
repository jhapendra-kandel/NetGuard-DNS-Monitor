import threading
import queue
import sys
import time
from dns_server import (start_dns_server, DNSStats, DNSCache, 
                        DNSBlocklist, AnomalyDetector)
from gui import create_gui

def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🛡️  DNS NETWORK ACTIVITY MONITOR v2.0  🛡️            ║
║                                                              ║
║              Final Year Cybersecurity Project               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Features Enabled:
  ✓ Real-time DNS query monitoring
  ✓ DNS caching for improved performance
  ✓ Blocklist/Allowlist management
  ✓ Anomaly detection & security alerts
  ✓ Traffic analysis & statistics
  ✓ CSV export capabilities

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(banner)

def main():
    """Main entry point"""
    print_banner()
    
    # Initialize components
    log_queue = queue.Queue()
    all_logs = []
    stats_tracker = DNSStats()
    dns_cache = DNSCache()
    blocklist = DNSBlocklist()
    anomaly_detector = AnomalyDetector()
    
    print("Initializing DNS Monitor...")
    print()
    
    # Start DNS server thread
    dns_thread = threading.Thread(
        target=start_dns_server,
        args=(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector),
        daemon=True
    )
    dns_thread.start()
    
    # Wait for server to initialize
    time.sleep(1)
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("💡 SETUP INSTRUCTIONS:")
    print("   1. Configure devices to use this PC's IP as DNS server")
    print("   2. Use the Blocklist tab to block ads/trackers")
    print("   3. Monitor the Alerts tab for security issues")
    print("   4. View Statistics for network insights")
    print()
    print("Starting GUI...")
    print()
    
    try:
        create_gui(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector)
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    
    print("\n✓ DNS Monitor stopped successfully")
    print("Thank you for using DNS Network Activity Monitor!")

if __name__ == "__main__":
    main()