# NetGuard DNS Monitor - this is the main entry point of our whole project
# basically everything starts from here, it initializes all components and starts the server
# without this file nothing will run so dont delete or mess with it

# Author: Jhapendra Kandel
# Project: 1st Year Python Programming
# Institution: Softwarica College of IT & E-Commerce (Coventry University)
# Version: 2.2.0

# importing threading because our dns server runs on separate thread from gui
import threading
# queue is for passing log data between dns server thread and gui thread safely
import queue
import sys
import time
# argparse is for handling command line arguments like --version and --help
import argparse
# platform is to check what os we running on and if we have admin rights
import platform
# importing all the important classes from our dns_server file
from dns_server import (start_dns_server, DNSStats, DNSCache, 
                        DNSBlocklist, AnomalyDetector)
# this is our gui module that creates the tkinter window
from gui import create_gui

# version info for our project, we update this when we make changes
VERSION = "2.2.0" #Version as veriable here to use it to call in app
AUTHOR = "Jhapendra Kandel"
INSTITUTION = "Softwarica College (Coventry University)"

def print_banner():
    """Print startup banner with project information"""
    # this is just the fancy banner that shows when you start the program
    # it looks nice in the terminal with the box drawing characters
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🛡️  NetGuard DNS Monitor v{VERSION}  🛡️              ║
║                                                              ║
║         1st Year Python Programming Project                 ║
║              {INSTITUTION:^44}              ║
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

def check_admin_privileges():
    """Check if running with administrator/root privileges"""
    # we need admin rights because port 53 is a privileged port
    # without admin the server cant bind to port 53 and wont work
    system = platform.system()
    
    # checking for windows admin rights using ctypes
    if system == "Windows":
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            return is_admin
        except:
            return False
    else:
        # for linux and mac we check if user is root (uid 0)
        import os
        return os.geteuid() == 0

def print_admin_warning():
    """Print warning if not running with admin privileges"""
    # this function shows instructions on how to run as admin
    # because students always forget to run as administrator
    system = platform.system()
    
    print("⚠️  WARNING: Not running with administrator privileges!")
    print()
    
    if system == "Windows":
        # windows users need to right click and run as admin
        print("   Please run this program as Administrator:")
        print("   1. Right-click on Command Prompt")
        print("   2. Select 'Run as administrator'")
        print("   3. Navigate to project folder")
        print("   4. Run: python main.py")
    else:
        # linux and mac users need sudo
        print("   Please run this program with sudo:")
        print("   sudo python3 main.py")
    
    print()
    print("   DNS server requires port 53 access (privileged port)")
    print()
    
    # giving user option to continue anyway incase they want to test other things
    response = input("Continue anyway? (y/N): ").strip().lower()
    if response != 'y':
        print("\nExiting...")
        sys.exit(0)

def get_local_ip():
    """Get local IP address for user information"""
    # we need to show user their local ip so they can configure their devices
    # to use this computer as dns server
    import socket
    try:
        # this trick connects to google dns to find out our own ip address
        # it doesnt actually send any data just figures out what interface to use
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "Unable to determine"

def parse_arguments():
    """Parse command-line arguments"""
    # setting up command line arguments so user can do things like --version or --help
    parser = argparse.ArgumentParser(
        description='NetGuard DNS Monitor - Real-time DNS monitoring and security',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python main.py                    # Start with GUI
  python main.py --version          # Show version
  python main.py --help             # Show this help

Author: {AUTHOR}
Institution: {INSTITUTION}
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'NetGuard DNS Monitor v{VERSION}'
    )
    
    # this is for future use, right now gui always starts
    parser.add_argument(
        '--no-gui',
        action='store_true',
        help='Run in console mode without GUI (future feature)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()

def main():
    """Main entry point with enhanced error handling"""
    # this is the main function where everything begins
    # it sets up all components one by one and then starts the gui
    
    # first parse any command line arguments user might have given
    args = parse_arguments()
    
    # showing the nice banner in terminal
    print_banner()
    
    # checking if user has admin rights, if not we warn them
    if not check_admin_privileges():
        print_admin_warning()
    
    # showing some system info so we know whats going on
    print("System Information:")
    print(f"  Platform: {platform.system()} {platform.release()}")
    print(f"  Python: {platform.python_version()}")
    print(f"  Local IP: {get_local_ip()}")
    print()
    
    # now we initialize all the main components of our project
    # each component is a separate class that handles different thing
    try:
        print("Initializing DNS Monitor components...")
        
        # this queue is how dns server thread sends log data to gui thread
        # without this gui would freeze or crash trying to access data directly
        log_queue = queue.Queue()
        # this list stores all logs so we can use them for statistics and export
        all_logs = []
        # stats tracker keeps count of total queries, blocked, cached etc
        stats_tracker = DNSStats()
        # dns cache stores previously resolved domains so we dont have to ask upstream again
        dns_cache = DNSCache()
        # blocklist manages which domains are blocked and which are allowed
        blocklist = DNSBlocklist()
        # anomaly detector watches for suspicious patterns like ddos or malware domains
        anomaly_detector = AnomalyDetector()
        
        print("  ✓ Log queue created")
        print("  ✓ Statistics tracker initialized")
        print("  ✓ DNS cache ready")
        print("  ✓ Blocklist manager ready")
        print("  ✓ Anomaly detector active")
        print()
        
    except Exception as e:
        # if any component fails to initialize we cant continue so we exit
        print(f"\n❌ Failed to initialize components: {e}")
        sys.exit(1)
    
    # starting the dns server on a separate thread
    # it has to be separate thread because gui runs on main thread
    # and both need to run at same time without blocking each other
    try:
        print("Starting DNS server...")
        dns_thread = threading.Thread(
            target=start_dns_server,
            args=(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector),
            daemon=True,  # daemon means it will stop when main program stops
            name="DNS-Server-Thread"
        )
        dns_thread.start()
        
        # waiting a bit for server to initialize before checking if it started ok
        time.sleep(1)
        
        # if thread died already that means server failed to start
        if not dns_thread.is_alive():
            print("\n❌ DNS server failed to start!")
            print("   This usually means port 53 is already in use or permission denied.")
            sys.exit(1)
        
        print("  ✓ DNS server started successfully")
        print()
        
    except Exception as e:
        print(f"\n❌ Failed to start DNS server: {e}")
        sys.exit(1)
    
    # printing setup guide so user knows how to configure their devices
    # this is important because many people dont know how to change dns settings
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("💡 QUICK SETUP GUIDE:")
    print()
    print(f"   Your Computer's IP: {get_local_ip()}")
    print()
    print("   Configure your devices:")
    print("   1. Go to Network/WiFi settings")
    print(f"   2. Set Primary DNS to: {get_local_ip()}")
    print("   3. Set Secondary DNS to: 8.8.8.8")
    print()
    print("   Using NetGuard:")
    print("   • Live Logs: See real-time DNS queries")
    print("   • Statistics: View network analytics")
    print("   • Blocklist: Block ads and trackers")
    print("   • Alerts: Monitor security threats")
    print()
    print("Starting GUI interface...")
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    # now starting the gui, this is the last thing because gui blocks the main thread
    # meaning code after this line wont run until gui window is closed
    try:
        create_gui(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector)
        
    except KeyboardInterrupt:
        # user pressed ctrl+c to stop everything
        print("\n\n⚠️  Keyboard interrupt detected")
        print("Shutting down gracefully...")
        
    except ImportError as e:
        # some module is missing, user needs to install dependencies
        print(f"\n❌ Missing required module: {e}")
        print("\nPlease install dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        # something unexpected went wrong
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    # this part runs after gui is closed, just showing goodbye message
    print("\n" + "="*60)
    print("✓ DNS Monitor stopped successfully")
    print()
    print("Thank you for using NetGuard DNS Monitor!")
    print(f"Project by {AUTHOR}")
    print(f"{INSTITUTION}")
    print("="*60 + "\n")

# this is the standard python way to check if this file is being run directly
# not imported as a module, if run directly then call main function
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # last resort error catching incase something goes very wrong
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)