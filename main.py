# main.py
import threading
import queue
import sys
import time
from dns_server import start_dns_server
from gui import create_gui

# Simple banner for startup
print("""
╔════════════════════════════════════════════╗
║     NetGuard DNS Monitor v1.0.0            ║
║  Real-time DNS Monitoring & Protection     ║
╚════════════════════════════════════════════╝
""")

def main():
    print("Starting DNS server and GUI...")
    
    log_queue = queue.Queue()
    all_logs = []
    domain_blocklist = []
    ip_blacklist = []

    # Start DNS server in background thread
    dns_thread = threading.Thread(
        target=start_dns_server,
        args=(log_queue, all_logs, domain_blocklist, ip_blacklist),
        daemon=True
    )
    dns_thread.start()

    # Give server a moment to bind port 53
    time.sleep(1)

    try:
        # Launch GUI (this blocks until GUI closes)
        create_gui(log_queue, all_logs, domain_blocklist, ip_blacklist)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"\nError during startup: {e}")
        sys.exit(1)

    print("NetGuard DNS Monitor stopped.")

if __name__ == "__main__":
    main()