import threading
import queue
from dns_server import start_dns_server
from gui import create_gui


log_queue = queue.Queue()


all_logs = []

if __name__ == "__main__":
   
    dns_thread = threading.Thread(target=start_dns_server, args=(log_queue, all_logs), daemon=True)
    dns_thread.start()

   
    create_gui(log_queue, all_logs)