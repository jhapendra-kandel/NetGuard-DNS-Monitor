# NetGuard DNS Monitor - this is the main entry point of our whole project
# basically everything starts from here, it initializes all components and starts the server
# without this file nothing will run so dont delete or mess with it

# Author: Jhapendra kandel
# Project: 1st Year Python Programming
# Institution: Softwarica College of IT & E-Commerce (Coventry University)
# Version: 2.2.0

# importing threading because our dns server runs on separate thread from gui
import threading
# queue is for passing log data between dns server thread and gui thread safely
import queue
import sys
import time
import os
# argparse is for handling command line arguments like --version and --help
import argparse
# platform is to check what os we running on and if we have admin rights
import platform
# importing all the important classes from our dns_server file
from dns_server import (start_dns_server, DNSStats, DNSCache, 
                        DNSBlocklist, AnomalyDetector)

# version info for our project, we update this when we make changes
VERSION = "2.3.0"
AUTHOR = "Jhapendra kandel"
INSTITUTION = "Softwarica College (Coventry University)"


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal styling"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # foreground colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # bright foreground colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


def colored(text, color):
    """Return colored text"""
    return f"{color}{text}{Colors.RESET}"


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_ascii_logo():
    """Print ASCII art logo from file or use embedded version"""
    
    # trying to load from ASCII_logo.txt file first
    logo_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ASCII_logo.txt')
    
    if os.path.exists(logo_file):
        try:
            with open(logo_file, 'r') as f:
                logo = f.read()
            print(colored(logo, Colors.CYAN))
            return
        except:
            pass

    # fallback embedded ASCII art if file not found
    logo = """
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@--%@@@@@@@@@@@@@@@--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%@@@@@@@@@@@@@@%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@-@@@@@@@@@@@@#@@@%*%%+----+=%%@@@@@@@@@@*--@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@-%@@@@@@@=@@@#%%%%+----%%----+%%%%%@@@@+@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@*@@@@@@@%%-%%#*-----%%%%%%%%-----*%%%%%%@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@*@@@@@*=----------%%%%%%%%%%%%%%%%----------=*@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@#@@@@------*@%%%%%%%%%%%%%%%%%%%%%%%%%%%*------@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@#@@@@---%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%---@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@#@@@%---%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%---%@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@-@@@%---%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%---%%#=@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@--@%%---%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%---%%--@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@+%---%%%%%%%%%%%%-----------=%%%%%=-%%%%%---%%@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@%---%%%%%%%%%----%--------%----%+--%%%%%---%@@@@@--@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@%%---%%%%%%%--=%%%---%%%----%%%----%%%%%%---%@@@@@@#@@@@@@@@@
@@@@@@@@@@@@@@-@@@@@@%%---%%%%%--+%%%%---%%%#-----%%%%+--%%%%%---%@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@-=@@@@@%%---%%%%%--=%%%%---%%%%%%---%%%%---%%%%%---%@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@*@@@@%---%%%%%%%---%%%---%%%%---%%%---%%%%%%%---%@@@--+@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@%*--%%%%%%%%%----%--------%----%%%%%%%%%--#%@@@@=@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@--%%--#%%%%%%%%%%%%----------#%%%%%%%%%%%*--%%%@@@=@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@%%#--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%--%%@@@%@+@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@=%%---%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%---%%@@@@---@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@+@@@%%---%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%--=%@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@%+--*%%%%%%%%%%%%%%%%%%%%%%%%%%+--*%%@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@#@@@@@@@@%%%---%%%%%%%%%%%%%%%%%%%%%%%%---#%@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@#--++****++++**++---%%%%%%%%%%%%%%%%%%%%---%%%@%@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%+---%%%%%%%%%%%%%%%%---*@%%@@@@%@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#%%%----%%%%%%%%%%----%%%@@@@@@@@--@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@*@@@@%%%#----*%%+----#%%*#%@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@*-=@@@@@@@@%%%%------%%%%@@@--@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
"""
    print(colored(logo, Colors.CYAN))


def print_app_info():
    """Print application information after logo"""
    print()
    print(colored("╔══════════════════════════════════════════════════════════════════════════════╗", Colors.BRIGHT_CYAN))
    print(colored("║                                                                              ║", Colors.BRIGHT_CYAN))
    print(colored("║", Colors.BRIGHT_CYAN) + colored("            🛡️  NetGuard DNS Monitor v" + VERSION + "  🛡️                         ", Colors.BRIGHT_WHITE + Colors.BOLD) + colored("║", Colors.BRIGHT_CYAN))
    print(colored("║                                                                              ║", Colors.BRIGHT_CYAN))
    print(colored("║", Colors.BRIGHT_CYAN) + colored("              Real-time DNS Monitoring & Security Tool                       ", Colors.WHITE) + colored("║", Colors.BRIGHT_CYAN))
    print(colored("║                                                                              ║", Colors.BRIGHT_CYAN))
    print(colored("║", Colors.BRIGHT_CYAN) + colored("         1st Year Python Programming Project                                 ", Colors.DIM) + colored("║", Colors.BRIGHT_CYAN))
    print(colored("║", Colors.BRIGHT_CYAN) + colored("         Softwarica College of IT & E-Commerce (Coventry University)        ", Colors.DIM) + colored("║", Colors.BRIGHT_CYAN))
    print(colored("║                                                                              ║", Colors.BRIGHT_CYAN))
    print(colored("╚══════════════════════════════════════════════════════════════════════════════╝", Colors.BRIGHT_CYAN))
    print()


def print_features():
    """Print enabled features"""
    print(colored("  Features Enabled:", Colors.BRIGHT_WHITE + Colors.BOLD))
    print(colored("    ✓ Real-time DNS query monitoring", Colors.GREEN))
    print(colored("    ✓ DNS caching for improved performance", Colors.GREEN))
    print(colored("    ✓ Blocklist/Allowlist management", Colors.GREEN))
    print(colored("    ✓ Anomaly detection & security alerts", Colors.GREEN))
    print(colored("    ✓ Traffic analysis & statistics", Colors.GREEN))
    print(colored("    ✓ CSV export capabilities", Colors.GREEN))
    print()


def get_interface_choice():
    """Ask user to choose between CLI and GUI"""
    print(colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", Colors.CYAN))
    print()
    print(colored("  Please select interface mode:", Colors.BRIGHT_WHITE + Colors.BOLD))
    print()
    print(colored("    [1]", Colors.BRIGHT_CYAN) + colored(" CLI", Colors.BRIGHT_WHITE) + colored(" - Command Line Interface (Terminal-based)", Colors.DIM))
    print(colored("    [2]", Colors.BRIGHT_CYAN) + colored(" GUI", Colors.BRIGHT_WHITE) + colored(" - Graphical User Interface (Window-based)", Colors.DIM))
    print()
    print(colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", Colors.CYAN))
    print()
    
    while True:
        choice = input(colored("  Would you like to choose CLI or GUI? Press 1 or 2 for CLI and GUI resp:\n", Colors.BRIGHT_YELLOW) + 
                      colored("  1.cli or 2.gui == ??? ---> REPLY:(1/2): ", Colors.BRIGHT_CYAN)).strip()
        
        if choice == '1':
            print()
            print(colored("  ✓ CLI mode selected!", Colors.GREEN))
            print()
            time.sleep(1)
            return 'cli'
        elif choice == '2':
            print()
            print(colored("  ✓ GUI mode selected!", Colors.GREEN))
            print()
            time.sleep(1)
            return 'gui'
        else:
            print(colored("  ✗ Invalid choice! Please enter 1 or 2.", Colors.RED))
            print()


def check_admin_privileges():
    """Check if running with administrator/root privileges"""
    system = platform.system()
    
    if system == "Windows":
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            return is_admin
        except:
            return False
    else:
        return os.geteuid() == 0


def print_admin_warning():
    """Print warning if not running with admin privileges"""
    system = platform.system()
    
    print(colored("⚠️  WARNING: Not running with administrator privileges!", Colors.BRIGHT_YELLOW))
    print()
    
    if system == "Windows":
        print(colored("   Please run this program as Administrator:", Colors.WHITE))
        print(colored("   1. Right-click on Command Prompt", Colors.DIM))
        print(colored("   2. Select 'Run as administrator'", Colors.DIM))
        print(colored("   3. Navigate to project folder", Colors.DIM))
        print(colored("   4. Run: python main.py", Colors.DIM))
    else:
        print(colored("   Please run this program with sudo:", Colors.WHITE))
        print(colored("   sudo python3 main.py", Colors.BRIGHT_CYAN))
    
    print()
    print(colored("   DNS server requires port 53 access (privileged port)", Colors.DIM))
    print()
    
    response = input(colored("  Continue anyway? (y/N): ", Colors.YELLOW)).strip().lower()
    if response != 'y':
        print(colored("\n  Exiting...", Colors.RED))
        sys.exit(0)


def get_local_ip():
    """Get local IP address for user information"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "Unable to determine"


def print_system_info():
    """Print system information"""
    print(colored("  System Information:", Colors.BRIGHT_WHITE + Colors.BOLD))
    print(colored(f"    Platform: {platform.system()} {platform.release()}", Colors.WHITE))
    print(colored(f"    Python: {platform.python_version()}", Colors.WHITE))
    print(colored(f"    Local IP: {get_local_ip()}", Colors.CYAN))
    print()


def print_setup_guide():
    """Print setup guide for configuring devices"""
    print(colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", Colors.CYAN))
    print()
    print(colored("  💡 QUICK SETUP GUIDE:", Colors.BRIGHT_WHITE + Colors.BOLD))
    print()
    print(colored(f"     Your Computer's IP: {get_local_ip()}", Colors.BRIGHT_CYAN))
    print()
    print(colored("     Configure your devices:", Colors.WHITE))
    print(colored("     1. Go to Network/WiFi settings", Colors.DIM))
    print(colored(f"     2. Set Primary DNS to: {get_local_ip()}", Colors.DIM))
    print(colored("     3. Set Secondary DNS to: 8.8.8.8", Colors.DIM))
    print()
    print(colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", Colors.CYAN))
    print()


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='NetGuard DNS Monitor - Real-time DNS monitoring and security',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  sudo python3 main.py              # Start with interface selection
  sudo python3 main.py --cli        # Start directly in CLI mode
  sudo python3 main.py --gui        # Start directly in GUI mode
  python main.py --version          # Show version

Author: {AUTHOR}
Institution: {INSTITUTION}
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'NetGuard DNS Monitor v{VERSION}'
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Start directly in CLI mode (skip selection)'
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Start directly in GUI mode (skip selection)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()


def initialize_components():
    """Initialize all DNS monitor components"""
    print(colored("  Initializing DNS Monitor components...", Colors.WHITE))
    
    log_queue = queue.Queue()
    all_logs = []
    stats_tracker = DNSStats()
    dns_cache = DNSCache()
    blocklist = DNSBlocklist()
    anomaly_detector = AnomalyDetector()
    
    print(colored("    ✓ Log queue created", Colors.GREEN))
    print(colored("    ✓ Statistics tracker initialized", Colors.GREEN))
    print(colored("    ✓ DNS cache ready", Colors.GREEN))
    print(colored("    ✓ Blocklist manager ready", Colors.GREEN))
    print(colored("    ✓ Anomaly detector active", Colors.GREEN))
    print()
    
    return log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector


def start_dns_server_thread(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector):
    """Start DNS server on a separate thread"""
    print(colored("  Starting DNS server...", Colors.WHITE))
    
    dns_thread = threading.Thread(
        target=start_dns_server,
        args=(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector),
        daemon=True,
        name="DNS-Server-Thread"
    )
    dns_thread.start()
    
    time.sleep(1)
    
    if not dns_thread.is_alive():
        print(colored("\n  ✗ DNS server failed to start!", Colors.RED))
        print(colored("    This usually means port 53 is already in use or permission denied.", Colors.DIM))
        sys.exit(1)
    
    print(colored("    ✓ DNS server started successfully", Colors.GREEN))
    print()
    
    return dns_thread


def main():
    """Main entry point with enhanced error handling"""
    
    # parse command line arguments first
    args = parse_arguments()
    
    # clear screen and show ASCII logo
    clear_screen()
    print_ascii_logo()
    print_app_info()
    print_features()
    
    # check admin privileges
    if not check_admin_privileges():
        print_admin_warning()
    
    # print system info
    print_system_info()
    
    # determine interface mode
    if args.cli:
        interface_mode = 'cli'
        print(colored("  ✓ CLI mode selected (via --cli flag)", Colors.GREEN))
        print()
    elif args.gui:
        interface_mode = 'gui'
        print(colored("  ✓ GUI mode selected (via --gui flag)", Colors.GREEN))
        print()
    else:
        # ask user to choose
        interface_mode = get_interface_choice()
    
    # initialize all components
    try:
        log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector = initialize_components()
    except Exception as e:
        print(colored(f"\n  ✗ Failed to initialize components: {e}", Colors.RED))
        sys.exit(1)
    
    # start dns server thread
    try:
        dns_thread = start_dns_server_thread(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector)
    except Exception as e:
        print(colored(f"\n  ✗ Failed to start DNS server: {e}", Colors.RED))
        sys.exit(1)
    
    # print setup guide
    print_setup_guide()
    
    # launch the selected interface
    if interface_mode == 'cli':
        print(colored("  Starting CLI interface...", Colors.CYAN))
        print()
        time.sleep(1)
        
        try:
            from cli import run_cli
            run_cli(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector)
            
        except ImportError as e:
            print(colored(f"\n  ✗ Failed to import CLI module: {e}", Colors.RED))
            print(colored("    Make sure cli.py exists in the same directory.", Colors.DIM))
            sys.exit(1)
            
        except KeyboardInterrupt:
            print(colored("\n\n  ⚠️  Keyboard interrupt detected", Colors.YELLOW))
            print(colored("  Shutting down gracefully...", Colors.WHITE))
            
        except Exception as e:
            print(colored(f"\n  ✗ CLI error: {e}", Colors.RED))
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    else:  # gui mode
        print(colored("  Starting GUI interface...", Colors.CYAN))
        print()
        
        try:
            from gui import create_gui
            create_gui(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector)
            
        except ImportError as e:
            print(colored(f"\n  ✗ Failed to import GUI module: {e}", Colors.RED))
            print(colored("\n  Please install required packages:", Colors.WHITE))
            print(colored("    pip install -r requirements.txt", Colors.CYAN))
            sys.exit(1)
            
        except KeyboardInterrupt:
            print(colored("\n\n  ⚠️  Keyboard interrupt detected", Colors.YELLOW))
            print(colored("  Shutting down gracefully...", Colors.WHITE))
            
        except Exception as e:
            print(colored(f"\n  ✗ GUI error: {e}", Colors.RED))
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    # goodbye message
    print()
    print(colored("═" * 70, Colors.CYAN))
    print(colored("  ✓ DNS Monitor stopped successfully", Colors.GREEN))
    print()
    print(colored("  Thank you for using NetGuard DNS Monitor!", Colors.BRIGHT_CYAN))
    print(colored(f"  Author: {AUTHOR}", Colors.DIM))
    print(colored(f"  {INSTITUTION}", Colors.DIM))
    print(colored("═" * 70, Colors.CYAN))
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(colored(f"\n  ✗ Fatal error: {e}", Colors.RED))
        sys.exit(1)