__version__ = "0.2.1"
import threading
import queue
from dns_server import start_dns_server
from gui import create_gui


log_queue = queue.Queue()


all_logs = []

domain_blocklist = []  # e.g., ['example.com', 'sub.example.com']
ip_blacklist = []  # e.g., ['192.168.1.100']

if __name__ == "__main__":
   
    print("NetGuard DNS Monitor v" + __version__)
    print("Starting DNS server and GUI...")

    dns_thread = threading.Thread(target=start_dns_server, args=(log_queue, all_logs, domain_blocklist, ip_blacklist), daemon=True)
    dns_thread.start()

   # Start GUI on main thread
    create_gui(log_queue, all_logs, domain_blocklist, ip_blacklist)