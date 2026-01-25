__version__ = "0.2.1"
import threading
import queue
from dns_server import start_dns_server
from gui import create_gui

try:
    import matplotlib.pyplot as plt
    from PIL import Image
    print("✓ Matplotlib & Pillow loaded successfully")
except ImportError as e:
    print("Error: Missing required library!")
    print("Run: pip install matplotlib pillow")
    print("Full error:", e)
    exit(1)

log_queue = queue.Queue()


all_logs = []

domain_blocklist = []  # e.g., ['example.com', 'sub.example.com']
ip_blacklist = []  # e.g., ['192.168.1.100']

if __name__ == "__main__":
   
    print("""
    ╔════════════════════════════════════════════╗
    ║     NetGuard DNS Monitor v0.2.0            ║
    ║  Real-time DNS Monitoring & Protection     ║
    ╚════════════════════════════════════════════╝
    Starting DNS server on port 53...
    """)

    print("NetGuard DNS Monitor v" + __version__)
    print("Starting DNS server and GUI...")

    dns_thread = threading.Thread(target=start_dns_server, args=(log_queue, all_logs, domain_blocklist, ip_blacklist), daemon=True)
    dns_thread.start()

   # Start GUI on main thread
    create_gui(log_queue, all_logs, domain_blocklist, ip_blacklist)