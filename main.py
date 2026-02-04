"""
NetGuard DNS Monitor - Main Entry Point
A comprehensive DNS proxy server with real-time monitoring and threat detection

Author: Jhapendra Kandel
Project: 1st Year Python Programming
Institution: Softwarica College of IT & E-Commerce (Coventry University)
Version: 2.0
"""

import threading
import queue
import sys
import time
import argparse
import platform
from dns_server import (start_dns_server, DNSStats, DNSCache, 
                        DNSBlocklist, AnomalyDetector)
from gui import create_gui

# Version information
VERSION = "2.0.0"
AUTHOR = "Jhapendra Kandel"
INSTITUTION = "Softwarica College (Coventry University)"

def print_banner():
    """Print startup banner with project information"""
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
    system = platform.system()
    
    if system == "Windows":
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            return is_admin
        except:
            return False
    else:
        # Unix-like systems
        import os
        return os.geteuid() == 0

def print_admin_warning():
    """Print warning if not running with admin privileges"""
    system = platform.system()
    
    print("⚠️  WARNING: Not running with administrator privileges!")
    print()
    
    if system == "Windows":
        print("   Please run this program as Administrator:")
        print("   1. Right-click on Command Prompt")
        print("   2. Select 'Run as administrator'")
        print("   3. Navigate to project folder")
        print("   4. Run: python main.py")
    else:
        print("   Please run this program with sudo:")
        print("   sudo python3 main.py")
    
    print()
    print("   DNS server requires port 53 access (privileged port)")
    print()
    
    response = input("Continue anyway? (y/N): ").strip().lower()
    if response != 'y':
        print("\nExiting...")
        sys.exit(0)

def get_local_ip():
    """Get local IP address for user information"""
    import socket
    try:
        # Create a socket to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "Unable to determine"

def parse_arguments():
    """Parse command-line arguments"""
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
    
    # Parse command-line arguments
    args = parse_arguments()
    
    # Print banner
    print_banner()
    
    # Check admin privileges
    if not check_admin_privileges():
        print_admin_warning()
    
    # Display system information
    print("System Information:")
    print(f"  Platform: {platform.system()} {platform.release()}")
    print(f"  Python: {platform.python_version()}")
    print(f"  Local IP: {get_local_ip()}")
    print()
    
    # Initialize components
    try:
        print("Initializing DNS Monitor components...")
        
        log_queue = queue.Queue()
        all_logs = []
        stats_tracker = DNSStats()
        dns_cache = DNSCache()
        blocklist = DNSBlocklist()
        anomaly_detector = AnomalyDetector()
        
        print("  ✓ Log queue created")
        print("  ✓ Statistics tracker initialized")
        print("  ✓ DNS cache ready")
        print("  ✓ Blocklist manager ready")
        print("  ✓ Anomaly detector active")
        print()
        
    except Exception as e:
        print(f"\n❌ Failed to initialize components: {e}")
        sys.exit(1)
    
    # Start DNS server thread
    try:
        print("Starting DNS server...")
        dns_thread = threading.Thread(
            target=start_dns_server,
            args=(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector),
            daemon=True,
            name="DNS-Server-Thread"
        )
        dns_thread.start()
        
        # Wait for server to initialize
        time.sleep(1)
        
        if not dns_thread.is_alive():
            print("\n❌ DNS server failed to start!")
            print("   This usually means port 53 is already in use or permission denied.")
            sys.exit(1)
        
        print("  ✓ DNS server started successfully")
        print()
        
    except Exception as e:
        print(f"\n❌ Failed to start DNS server: {e}")
        sys.exit(1)
    
    # Print setup instructions
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
    
    # Start GUI
    try:
        create_gui(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Keyboard interrupt detected")
        print("Shutting down gracefully...")
        
    except ImportError as e:
        print(f"\n❌ Missing required module: {e}")
        print("\nPlease install dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    # Cleanup
    print("\n" + "="*60)
    print("✓ DNS Monitor stopped successfully")
    print()
    print("Thank you for using NetGuard DNS Monitor!")
    print(f"Project by {AUTHOR}")
    print(f"{INSTITUTION}")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)