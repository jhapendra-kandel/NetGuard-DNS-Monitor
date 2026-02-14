# NetGuard DNS Monitor - ULTIMATE CLI Interface v2.2
# Enhanced command line interface with AMAZING real-time features
# This is THE BEST CLI experience you'll ever have for DNS monitoring!

# Author: Jhapendra kandel
# Project: 1st Year Python Programming
# Institution: Softwarica College of IT & E-Commerce (Coventry University)

VERSION = "2.2.0"

import os
import sys
import time
import datetime
import csv
import signal
import threading
from collections import Counter

from stats import compute_stats, export_stats_to_file


# ═══════════════════════════════════════════════════════════════════════════
#                         ENHANCED COLOR SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

class Colors:
    """Advanced ANSI color codes with custom NetGuard theme"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    
    # Standard colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors - Much better visibility!
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # NetGuard custom theme - Beautiful cyan/blue gradient
    NETGUARD_PRIMARY = '\033[38;5;51m'      # Bright cyan - main color
    NETGUARD_SECONDARY = '\033[38;5;39m'    # Blue - secondary
    NETGUARD_SUCCESS = '\033[38;5;46m'      # Bright green - success
    NETGUARD_WARNING = '\033[38;5;226m'     # Bright yellow - warnings
    NETGUARD_ERROR = '\033[38;5;196m'       # Bright red - errors
    NETGUARD_INFO = '\033[38;5;117m'        # Light blue - info


# ═══════════════════════════════════════════════════════════════════════════
#                         UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def clear_screen():
    """Clear terminal screen (works on Windows, Linux, Mac)"""
    os.system('cls' if os.name == 'nt' else 'clear')


def colored(text, color):
    """Return colored text with automatic reset"""
    return f"{color}{text}{Colors.RESET}"


def gradient_text(text, start_color, end_color):
    """Create simple gradient effect"""
    result = ""
    for i, char in enumerate(text):
        result += colored(char, start_color if i % 2 == 0 else end_color)
    return result


def print_header(title, width=80):
    """Print beautiful header with box drawing characters"""
    print()
    print(colored("╔" + "═" * (width - 2) + "╗", Colors.NETGUARD_PRIMARY))
    print(colored("║", Colors.NETGUARD_PRIMARY) + 
          colored(title.center(width - 2), Colors.BRIGHT_WHITE + Colors.BOLD) + 
          colored("║", Colors.NETGUARD_PRIMARY))
    print(colored("╚" + "═" * (width - 2) + "╝", Colors.NETGUARD_PRIMARY))
    print()


def print_separator(char="─", width=80, color=Colors.DIM):
    """Print separator line"""
    print(colored(char * width, color))


def print_box(text, width=80, color=Colors.NETGUARD_PRIMARY):
    """Print text in a nice box"""
    lines = text.split('\n')
    print(colored("┌" + "─" * (width - 2) + "┐", color))
    for line in lines:
        padding = width - len(line) - 4
        print(colored("│ ", color) + line + " " * padding + colored(" │", color))
    print(colored("└" + "─" * (width - 2) + "┘", color))


def print_menu_item(number, text, icon="●"):
    """Print styled menu item"""
    num_colored = colored(f"[{number}]", Colors.NETGUARD_PRIMARY + Colors.BOLD)
    icon_colored = colored(icon, Colors.BRIGHT_WHITE)
    print(f"  {num_colored} {icon_colored} {text}")


def animate_loading(text="Processing", duration=1.5):
    """Show cool animated loading spinner"""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    
    while time.time() < end_time:
        frame = frames[i % len(frames)]
        sys.stdout.write(f"\r  {colored(frame, Colors.NETGUARD_PRIMARY)} {text}...")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()


def print_success(message):
    """Print success message with green checkmark"""
    print(colored("  ✓ ", Colors.NETGUARD_SUCCESS + Colors.BOLD) + 
          colored(message, Colors.BRIGHT_WHITE))


def print_error(message):
    """Print error message with red X"""
    print(colored("  ✗ ", Colors.NETGUARD_ERROR + Colors.BOLD) + 
          colored(message, Colors.BRIGHT_WHITE))


def print_warning(message):
    """Print warning message with yellow triangle"""
    print(colored("  ⚠ ", Colors.NETGUARD_WARNING + Colors.BOLD) + 
          colored(message, Colors.BRIGHT_WHITE))


def print_info(message):
    """Print info message with blue i"""
    print(colored("  ℹ ", Colors.NETGUARD_INFO + Colors.BOLD) + 
          colored(message, Colors.BRIGHT_WHITE))


def format_number(num):
    """Format number with commas and cyan color"""
    return colored(f"{num:,}", Colors.BRIGHT_CYAN)


def format_percentage(value):
    """Format percentage with color coding (green=good, yellow=ok, red=bad)"""
    if value >= 70:
        color = Colors.NETGUARD_SUCCESS
    elif value >= 40:
        color = Colors.NETGUARD_WARNING
    else:
        color = Colors.NETGUARD_ERROR
    return colored(f"{value:.1f}%", color + Colors.BOLD)


def create_progress_bar(current, total, width=40):
    """Create beautiful ASCII progress bar"""
    percentage = (current / total) * 100 if total > 0 else 0
    filled = int((current / total) * width) if total > 0 else 0
    bar = "█" * filled + "░" * (width - filled)
    return f"{colored(bar, Colors.NETGUARD_PRIMARY)} {format_percentage(percentage)}"


# ═══════════════════════════════════════════════════════════════════════════
#                         MAIN CLI CLASS
# ═══════════════════════════════════════════════════════════════════════════

class DNSMonitorCLI:
    """THE ULTIMATE Command Line Interface for NetGuard DNS Monitor"""
    
    def __init__(self, log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector):
        self.log_queue = log_queue
        self.all_logs = all_logs
        self.stats_tracker = stats_tracker
        self.dns_cache = dns_cache
        self.blocklist = blocklist
        self.anomaly_detector = anomaly_detector
        
        self.running = True
        self.live_mode = False
        
        # Performance tracking
        self.last_query_count = 0
        self.queries_per_second = 0
        
        # Graceful interrupt handling
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Background thread for real-time stats
        self.refresh_thread = threading.Thread(target=self.background_refresh, daemon=True)
        self.refresh_thread.start()
    
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        self.live_mode = False
        self.running = True
        print(colored("\n\n  ⚡ Interrupted! Returning to menu...", Colors.NETGUARD_WARNING))
        time.sleep(0.8)
    
    def background_refresh(self):
        """Background thread for calculating queries per second"""
        while True:
            time.sleep(1)
            current_count = len(self.all_logs)
            if current_count > self.last_query_count:
                self.queries_per_second = current_count - self.last_query_count
                self.last_query_count = current_count
    
    def run(self):
        """Main CLI loop"""
        while self.running:
            self.show_main_menu()
    
    def print_banner(self):
        """Print EPIC ASCII banner"""
        banner = """
  ███╗   ██╗███████╗████████╗ ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗ 
  ████╗  ██║██╔════╝╚══██╔══╝██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗
  ██╔██╗ ██║█████╗     ██║   ██║  ███╗██║   ██║███████║██████╔╝██║  ██║
  ██║╚██╗██║██╔══╝     ██║   ██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║
  ██║ ╚████║███████╗   ██║   ╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
  ╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
"""
        print(gradient_text(banner, Colors.NETGUARD_PRIMARY, Colors.NETGUARD_SECONDARY))
        print(colored("                  DNS MONITOR v2.2 - CLI EDITION", Colors.BRIGHT_WHITE + Colors.BOLD))
        print(colored("           Real-time Monitoring • Security • Performance", Colors.DIM))
        print()
    
    def show_main_menu(self):
        """Enhanced main menu with REAL-TIME dashboard"""
        clear_screen()
        self.print_banner()
        
        # REAL-TIME STATS DASHBOARD
        stats = self.stats_tracker.get_stats()
        cache_stats = self.dns_cache.get_stats()
        
        print(colored("╔══════════════════════════════════════════════════════════════════════════════╗", Colors.NETGUARD_PRIMARY))
        print(colored("║", Colors.NETGUARD_PRIMARY) + 
              colored("      REAL-TIME DASHBOARD ", Colors.BRIGHT_WHITE + Colors.BOLD).center(88) + 
              colored("║", Colors.NETGUARD_PRIMARY))
        print(colored("╠══════════════════════════════════════════════════════════════════════════════╣", Colors.NETGUARD_PRIMARY))
        
        # Stats row 1
        total = format_number(stats['total'])
        blocked = format_number(stats['blocked'])
        cached = format_number(stats['cached'])
        qps = colored(f"{self.queries_per_second}", Colors.NETGUARD_WARNING + Colors.BOLD)
        
        print(colored("║", Colors.NETGUARD_PRIMARY) + 
              f"  📊 Queries: {total}  │  🚫 Blocked: {blocked}  │  💾 Cached: {cached}  │  ⚡ {qps} q/s".ljust(88) + 
              colored("║", Colors.NETGUARD_PRIMARY))
        
        # Stats row 2
        cache_status = colored("● ON", Colors.NETGUARD_SUCCESS + Colors.BOLD) if self.dns_cache.enabled else colored("● OFF", Colors.NETGUARD_ERROR + Colors.BOLD)
        hit_rate = format_percentage(cache_stats['hit_rate'])
        uptime = str(datetime.timedelta(seconds=int(stats['uptime'])))
        
        print(colored("║", Colors.NETGUARD_PRIMARY) + 
              f"  Cache: {cache_status}  │  Hit Rate: {hit_rate}  │  Uptime: {colored(uptime, Colors.BRIGHT_CYAN)}".ljust(94) + 
              colored("║", Colors.NETGUARD_PRIMARY))
        
        print(colored("╚══════════════════════════════════════════════════════════════════════════════╝", Colors.NETGUARD_PRIMARY))
        print()
        
        # MAIN MENU OPTIONS
        print(colored("┌─────────────────────────────────────────────────────────────────────────────┐", Colors.BRIGHT_CYAN))
        print(colored("│", Colors.BRIGHT_CYAN) + 
              colored("                              MAIN MENU", Colors.BRIGHT_WHITE + Colors.BOLD).center(85) + 
              colored("│", Colors.BRIGHT_CYAN))
        print(colored("└─────────────────────────────────────────────────────────────────────────────┘", Colors.BRIGHT_CYAN))
        print()
        
        print_menu_item("1", " Live DNS Logs (Real-time Stream)", "●")
        print_menu_item("2", " Statistics & Analytics", "●")
        print_menu_item("3", " Blocklist Management", "●")
        print_menu_item("4", " Security Alerts Monitor", "●")
        print_menu_item("5", " Cache Control Panel", "●")
        print_menu_item("6", " Export & Backup", "●")
        print_menu_item("7", " Advanced Settings", "●")
        print_menu_item("8", " System Information", "●")
        print_menu_item("0", " Exit NetGuard CLI", "●")
        
        print()
        print_separator("─", 80, Colors.DIM)
        
        choice = input(colored("\n  ➤ Your choice [0-8]: ", Colors.NETGUARD_PRIMARY + Colors.BOLD)).strip()
        
        if choice == '1':
            self.show_live_logs()
        elif choice == '2':
            self.show_statistics()
        elif choice == '3':
            self.blocklist_menu()
        elif choice == '4':
            self.show_alerts()
        elif choice == '5':
            self.cache_menu()
        elif choice == '6':
            self.export_menu()
        elif choice == '7':
            self.settings_menu()
        elif choice == '8':
            self.show_system_info()
        elif choice == '0':
            self.exit_cli()
        else:
            print_error("Invalid! Please enter 0-8")
            time.sleep(1)
    
    def show_live_logs(self):
        """ENHANCED live logs with BEAUTIFUL color coding"""
        clear_screen()
        print_header("🔴 LIVE DNS LOGS - REAL-TIME MONITORING", 80)
        
        print_info("Watching DNS queries in real-time...")
        print_warning("Press Ctrl+C to return to menu")
        print()
        print_separator("═", 80, Colors.NETGUARD_PRIMARY)
        
        # Beautiful header
        header = (
            colored("TIME", Colors.BRIGHT_YELLOW + Colors.BOLD).ljust(26) + " │ " +
            colored("SOURCE IP", Colors.BRIGHT_CYAN + Colors.BOLD).ljust(28) + " │ " +
            colored("DOMAIN", Colors.BRIGHT_GREEN + Colors.BOLD).ljust(50) + " │ " +
            colored("TYPE", Colors.BRIGHT_MAGENTA + Colors.BOLD).ljust(16) + " │ " +
            colored("STATUS", Colors.BRIGHT_WHITE + Colors.BOLD).ljust(22)
        )
        print(header)
        print_separator("─", 80, Colors.NETGUARD_PRIMARY)
        
        self.live_mode = True
        last_count = len(self.all_logs)
        query_counter = 0
        
        try:
            while self.live_mode:
                current_count = len(self.all_logs)
                
                if current_count > last_count:
                    new_logs = self.all_logs[last_count:current_count]
                    
                    for log in new_logs:
                        timestamp, ip, domain, qtype, details, success, blocked, cached = log
                        
                        query_counter += 1
                        
                        # Format time
                        time_str = timestamp.split(' ')[1][:12] if ' ' in timestamp else timestamp[:12]
                        
                        # Truncate domain
                        domain_display = domain[:35] + "..." if len(domain) > 35 else domain
                        
                        # BEAUTIFUL color coding
                        if blocked:
                            status = colored("🚫 BLOCKED", Colors.NETGUARD_ERROR + Colors.BOLD)
                            domain_colored = colored(domain_display, Colors.RED)
                        elif cached:
                            status = colored("💾 CACHED", Colors.NETGUARD_INFO + Colors.BOLD)
                            domain_colored = colored(domain_display, Colors.BRIGHT_BLUE)
                        elif success:
                            status = colored("✓ SUCCESS", Colors.NETGUARD_SUCCESS + Colors.BOLD)
                            domain_colored = colored(domain_display, Colors.BRIGHT_WHITE)
                        else:
                            status = colored("✗ FAILED", Colors.NETGUARD_ERROR)
                            domain_colored = colored(domain_display, Colors.RED + Colors.DIM)
                        
                        time_colored = colored(time_str, Colors.BRIGHT_YELLOW)
                        ip_colored = colored(ip, Colors.BRIGHT_CYAN)
                        type_colored = colored(qtype, Colors.BRIGHT_MAGENTA)
                        
                        print(f"{time_colored.ljust(32)} │ {ip_colored.ljust(34)} │ {domain_colored.ljust(47)} │ {type_colored.ljust(22)} │ {status}")
                        
                        # Show counter every 10 queries
                        if query_counter % 10 == 0:
                            sys.stdout.write(colored(f"\r  📈 Total monitored: {query_counter} queries", Colors.DIM))
                            sys.stdout.flush()
                    
                    last_count = current_count
                
                time.sleep(0.1)  # Super fast refresh!
                
        except KeyboardInterrupt:
            pass
        
        self.live_mode = False
        print("\n")
        print_success(f"Session complete! Monitored {query_counter} queries")
        time.sleep(2)
    
    def show_statistics(self):
        """Enhanced statistics with AMAZING visualizations"""
        clear_screen()
        print_header("📊 STATISTICS & ANALYTICS", 80)
        
        if not self.all_logs:
            print_warning("No data available yet")
            print_info("Configure devices to use this DNS server")
            print()
            input(colored("  Press Enter...", Colors.DIM))
            return
        
        animate_loading("Generating statistics", 1.5)
        
        stats_text = compute_stats(self.all_logs)
        
        # Color-enhanced output
        for line in stats_text.split('\n'):
            if '===' in line or '---' in line:
                print(colored(line, Colors.NETGUARD_PRIMARY))
            elif any(emoji in line for emoji in ['📊', '🌐', '📱', '🚫', '🔍', '💡', '🔬']):
                print(colored(line, Colors.BRIGHT_CYAN + Colors.BOLD))
            elif '✓' in line or '✅' in line:
                print(colored(line, Colors.NETGUARD_SUCCESS))
            elif '✗' in line or '⚠️' in line:
                print(colored(line, Colors.NETGUARD_WARNING))
            elif 'BLOCKED' in line:
                print(colored(line, Colors.NETGUARD_ERROR))
            elif ':' in line and not line.startswith(' '):
                parts = line.split(':', 1)
                print(colored(parts[0] + ":", Colors.BRIGHT_WHITE + Colors.BOLD) + parts[1])
            else:
                print(line)
        
        print()
        print_separator("═", 80, Colors.NETGUARD_PRIMARY)
        print()
        
        print(colored("  Quick Actions: ", Colors.BRIGHT_WHITE + Colors.BOLD) +
              colored("[E]", Colors.NETGUARD_PRIMARY) + " Export  " +
              colored("[R]", Colors.NETGUARD_PRIMARY) + " Refresh  " +
              colored("[Q]", Colors.NETGUARD_PRIMARY) + " Back")
        
        choice = input(colored("\n  ➤ ", Colors.NETGUARD_PRIMARY)).strip().lower()
        
        if choice == 'e':
            self.export_stats_report()
        elif choice == 'r':
            self.show_statistics()
    
    def blocklist_menu(self):
        """ENHANCED blocklist management menu"""
        while True:
            clear_screen()
            print_header("🚫 BLOCKLIST MANAGEMENT CENTER", 80)
            
            blocked, allowed = self.blocklist.get_lists()
            
            # Stats box with progress bars
            print(colored("┌────────────────────────────────────────────────────────────┐", Colors.NETGUARD_PRIMARY))
            print(colored("│", Colors.NETGUARD_PRIMARY) + 
                  f"  🚫 Blocked Domains: {format_number(len(blocked))}".ljust(66) + 
                  colored("│", Colors.NETGUARD_PRIMARY))
            print(colored("│", Colors.NETGUARD_PRIMARY) + 
                  f"  ✅ Allowed Domains: {format_number(len(allowed))}".ljust(66) + 
                  colored("│", Colors.NETGUARD_PRIMARY))
            print(colored("│", Colors.NETGUARD_PRIMARY) + 
                  f"  📊 Queries Blocked: {format_number(self.blocklist.blocked_count)}".ljust(66) + 
                  colored("│", Colors.NETGUARD_PRIMARY))
            print(colored("└────────────────────────────────────────────────────────────┘", Colors.NETGUARD_PRIMARY))
            print()
            
            print_menu_item("1", "View Blocked Domains List", "🚫")
            print_menu_item("2", "View Allowlist (Whitelist)", "✅")
            print_menu_item("3", "➕ Add Domain to Blocklist", "➕")
            print_menu_item("4", "➕ Add Domain to Allowlist", "➕")
            print_menu_item("5", "➖ Remove from Blocklist", "➖")
            print_menu_item("6", "➖ Remove from Allowlist", "➖")
            print_menu_item("7", "🔍 Search Blocklist", "🔍")
            print_menu_item("8", "📥 Load Default Blocklist", "📥")
            print_menu_item("9", "📁 Import from File", "📁")
            print_menu_item("0", "◀ Back to Main Menu", "◀")
            
            print()
            choice = input(colored("  ➤ Choice [0-9]: ", Colors.NETGUARD_PRIMARY + Colors.BOLD)).strip()
            
            if choice == '1':
                self.view_blocked_domains()
            elif choice == '2':
                self.view_allowed_domains()
            elif choice == '3':
                self.add_blocked_domain()
            elif choice == '4':
                self.add_allowed_domain()
            elif choice == '5':
                self.remove_blocked_domain()
            elif choice == '6':
                self.remove_allowed_domain()
            elif choice == '7':
                self.search_blocklist()
            elif choice == '8':
                self.load_default_blocklist()
            elif choice == '9':
                self.import_blocklist_file()
            elif choice == '0':
                break
    
    def view_blocked_domains(self):
        """View blocked domains with SMART pagination"""
        clear_screen()
        print_header("🚫 BLOCKED DOMAINS", 80)
        
        blocked, _ = self.blocklist.get_lists()
        blocked = sorted(blocked)
        
        if not blocked:
            print_warning("No blocked domains")
            input(colored("\n  Press Enter...", Colors.DIM))
            return
        
        page_size = 25
        total_pages = (len(blocked) + page_size - 1) // page_size
        current_page = 1
        
        while True:
            clear_screen()
            print_header(f"🚫 BLOCKED DOMAINS - Page {current_page}/{total_pages}", 80)
            
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(blocked))
            
            # Two-column layout for better space usage
            for i in range(start_idx, end_idx, 2):
                num1 = colored(f"{i+1:4d}.", Colors.DIM)
                domain1 = colored(blocked[i][:35], Colors.BRIGHT_WHITE)
                
                if i+1 < end_idx:
                    num2 = colored(f"{i+2:4d}.", Colors.DIM)
                    domain2 = colored(blocked[i+1][:35], Colors.BRIGHT_WHITE)
                    print(f"  {num1} {domain1.ljust(42)}  {num2} {domain2}")
                else:
                    print(f"  {num1} {domain1}")
            
            print()
            print_separator("─", 80, Colors.NETGUARD_PRIMARY)
            print(f"  Total: {format_number(len(blocked))} blocked domains")
            print()
            
            # Navigation
            nav_parts = []
            if current_page > 1:
                nav_parts.append(colored("[P]", Colors.NETGUARD_PRIMARY) + " Prev")
            if current_page < total_pages:
                nav_parts.append(colored("[N]", Colors.NETGUARD_PRIMARY) + " Next")
            nav_parts.append(colored("[G]", Colors.NETGUARD_PRIMARY) + " Go to page")
            nav_parts.append(colored("[Q]", Colors.NETGUARD_PRIMARY) + " Quit")
            
            print("  " + "  ".join(nav_parts))
            
            choice = input(colored("\n  ➤ ", Colors.NETGUARD_PRIMARY)).strip().lower()
            
            if choice == 'n' and current_page < total_pages:
                current_page += 1
            elif choice == 'p' and current_page > 1:
                current_page -= 1
            elif choice == 'g':
                try:
                    page = int(input(colored("  Page number: ", Colors.NETGUARD_PRIMARY)))
                    if 1 <= page <= total_pages:
                        current_page = page
                    else:
                        print_error(f"Must be 1-{total_pages}")
                        time.sleep(1)
                except:
                    print_error("Invalid number")
                    time.sleep(1)
            elif choice == 'q':
                break
    
    def view_allowed_domains(self):
        """View allowed domains"""
        clear_screen()
        print_header("✅ ALLOWED DOMAINS (WHITELIST)", 80)
        
        _, allowed = self.blocklist.get_lists()
        allowed = sorted(allowed)
        
        if not allowed:
            print_warning("No allowed domains")
        else:
            for i, domain in enumerate(allowed, start=1):
                num_str = colored(f"{i:4d}.", Colors.DIM)
                domain_str = colored(domain, Colors.NETGUARD_SUCCESS)
                print(f"  {num_str} {domain_str}")
            print()
            print(f"  Total: {format_number(len(allowed))} domains")
        
        print()
        input(colored("  Press Enter...", Colors.DIM))
    
    def add_blocked_domain(self):
        """Add domain with validation"""
        print()
        domain = input(colored("  ➤ Domain to block: ", Colors.NETGUARD_PRIMARY + Colors.BOLD)).strip().lower()
        
        if domain:
            if '.' not in domain:
                print_error("Invalid! Must contain at least one dot")
                time.sleep(2)
                return
            
            animate_loading("Adding domain", 1)
            self.blocklist.add_blocked(domain)
            print_success(f"'{domain}' blocked!")
        else:
            print_warning("Cancelled")
        
        time.sleep(1.5)
    
    def add_allowed_domain(self):
        """Add to allowlist"""
        print()
        domain = input(colored("  ➤ Domain to allow: ", Colors.NETGUARD_PRIMARY + Colors.BOLD)).strip().lower()
        
        if domain:
            animate_loading("Adding domain", 1)
            self.blocklist.add_allowed(domain)
            print_success(f"'{domain}' allowed!")
        else:
            print_warning("Cancelled")
        
        time.sleep(1.5)
    
    def remove_blocked_domain(self):
        """Remove from blocklist"""
        print()
        domain = input(colored("  ➤ Domain to unblock: ", Colors.NETGUARD_PRIMARY + Colors.BOLD)).strip().lower()
        
        if domain:
            animate_loading("Removing", 1)
            self.blocklist.remove_blocked(domain)
            print_success(f"'{domain}' unblocked!")
        else:
            print_warning("Cancelled")
        
        time.sleep(1.5)
    
    def remove_allowed_domain(self):
        """Remove from allowlist"""
        print()
        domain = input(colored("  ➤ Domain to remove: ", Colors.NETGUARD_PRIMARY + Colors.BOLD)).strip().lower()
        
        if domain:
            animate_loading("Removing", 1)
            self.blocklist.remove_allowed(domain)
            print_success(f"'{domain}' removed!")
        else:
            print_warning("Cancelled")
        
        time.sleep(1.5)
    
    def search_blocklist(self):
        """Search with HIGHLIGHTING"""
        print()
        search_term = input(colored("  ➤ Search: ", Colors.NETGUARD_PRIMARY + Colors.BOLD)).strip().lower()
        
        if not search_term:
            print_warning("Cancelled")
            time.sleep(1)
            return
        
        animate_loading("Searching", 1)
        
        blocked, _ = self.blocklist.get_lists()
        results = [d for d in blocked if search_term in d.lower()]
        
        clear_screen()
        print_header(f"🔍 SEARCH: '{search_term}'", 80)
        
        if not results:
            print_warning("No matches found")
        else:
            for i, domain in enumerate(sorted(results)[:50], start=1):
                # Highlight match
                highlighted = domain.replace(search_term, 
                    colored(search_term, Colors.NETGUARD_WARNING + Colors.BOLD))
                num_str = colored(f"{i:4d}.", Colors.DIM)
                print(f"  {num_str} {highlighted}")
            
            if len(results) > 50:
                print()
                print_info(f"... and {len(results) - 50} more")
            
            print()
            print(f"  Found: {format_number(len(results))} domains")
        
        print()
        input(colored("  Press Enter...", Colors.DIM))
    
    def load_default_blocklist(self):
        """Load defaults"""
        print()
        confirm = input(colored("  ➤ Load defaults? [y/N]: ", 
                               Colors.NETGUARD_WARNING + Colors.BOLD)).strip().lower()
        
        if confirm == 'y':
            animate_loading("Loading", 2)
            self.blocklist.load_default_blocklist()
            blocked, _ = self.blocklist.get_lists()
            print_success(f"Loaded! Total: {format_number(len(blocked))}")
        else:
            print_warning("Cancelled")
        
        time.sleep(2)
    
    def import_blocklist_file(self):
        """Import from file"""
        print()
        filename = input(colored("  ➤ File path: ", Colors.NETGUARD_PRIMARY + Colors.BOLD)).strip()
        
        if not filename:
            print_warning("Cancelled")
            time.sleep(1)
            return
        
        if not os.path.exists(filename):
            print_error(f"Not found: {filename}")
            time.sleep(2)
            return
        
        animate_loading("Importing", 2)
        count = self.blocklist.import_from_file(filename)
        
        if count > 0:
            print_success(f"Imported {format_number(count)} domains!")
        else:
            print_error("Failed or empty")
        
        time.sleep(2)
    
    def show_alerts(self):
        """ENHANCED alerts display"""
        clear_screen()
        print_header("⚠️  SECURITY ALERTS MONITOR", 80)
        
        alerts = self.anomaly_detector.get_alerts()
        
        if not alerts:
            print_success("No alerts! All clear")
            print()
            print_info("Monitoring for:")
            print(colored("  • Excessive queries", Colors.DIM))
            print(colored("  • Suspicious domains", Colors.DIM))
            print(colored("  • DGA patterns", Colors.DIM))
        else:
            print(f"  {colored(len(alerts), Colors.NETGUARD_ERROR + Colors.BOLD)} alert(s):\n")
            
            for alert in reversed(alerts):
                severity = alert['severity']
                timestamp = datetime.datetime.fromtimestamp(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                
                if severity == 'HIGH':
                    color = Colors.NETGUARD_ERROR + Colors.BOLD
                    icon = "🔴"
                elif severity == 'MEDIUM':
                    color = Colors.NETGUARD_WARNING + Colors.BOLD
                    icon = "🟡"
                else:
                    color = Colors.NETGUARD_INFO
                    icon = "🔵"
                
                print(f"  {icon} {colored(f'[{timestamp}]', Colors.DIM)} {colored(f'[{severity}]', color)}")
                print(f"      {alert['message']}")
                print()
        
        print_separator("─", 80, Colors.NETGUARD_PRIMARY)
        print()
        
        print(colored("[C]", Colors.NETGUARD_PRIMARY) + " Clear  " + 
              colored("[R]", Colors.NETGUARD_PRIMARY) + " Refresh  " + 
              colored("[Q]", Colors.NETGUARD_PRIMARY) + " Back")
        
        choice = input(colored("\n  ➤ ", Colors.NETGUARD_PRIMARY)).strip().lower()
        
        if choice == 'c':
            self.anomaly_detector.alerts.clear()
            print_success("Cleared!")
            time.sleep(1)
        elif choice == 'r':
            self.show_alerts()
    
    def cache_menu(self):
        """ULTIMATE cache control"""
        while True:
            clear_screen()
            print_header("⚡ CACHE CONTROL PANEL", 80)
            
            cache_stats = self.dns_cache.get_stats()
            
            status = colored("● ON", Colors.NETGUARD_SUCCESS + Colors.BOLD) if self.dns_cache.enabled else colored("● OFF", Colors.NETGUARD_ERROR + Colors.BOLD)
            toggle_text = "Disable Cache" if self.dns_cache.enabled else "Enable Cache"
            
            # Stats box
            print(colored("┌────────────────────────────────────────────────────────────┐", Colors.NETGUARD_PRIMARY))
            print(colored("│", Colors.NETGUARD_PRIMARY) + f"  Status: {status}".ljust(66) + colored("│", Colors.NETGUARD_PRIMARY))
            print(colored("│", Colors.NETGUARD_PRIMARY) + f"  Size: {format_number(cache_stats['size'])} / {format_number(cache_stats['max_size'])}".ljust(74) + colored("│", Colors.NETGUARD_PRIMARY))
            print(colored("│", Colors.NETGUARD_PRIMARY) + f"  Hits: {format_number(cache_stats['hits'])}".ljust(66) + colored("│", Colors.NETGUARD_PRIMARY))
            print(colored("│", Colors.NETGUARD_PRIMARY) + f"  Misses: {format_number(cache_stats['misses'])}".ljust(66) + colored("│", Colors.NETGUARD_PRIMARY))
            print(colored("│", Colors.NETGUARD_PRIMARY) + f"  Hit Rate: {format_percentage(cache_stats['hit_rate'])}".ljust(68) + colored("│", Colors.NETGUARD_PRIMARY))
            print(colored("└────────────────────────────────────────────────────────────┘", Colors.NETGUARD_PRIMARY))
            print()
            
            # Progress bar
            if cache_stats['max_size'] > 0:
                bar = create_progress_bar(cache_stats['size'], cache_stats['max_size'], 50)
                print(f"  Usage: {bar}")
                print()
            
            print_menu_item("1", toggle_text, "🔀")
            print_menu_item("2", "Clear Cache", "🗑️")
            print_menu_item("3", "Refresh", "🔄")
            print_menu_item("0", "Back", "◀")
            
            print()
            choice = input(colored("  ➤ [0-3]: ", Colors.NETGUARD_PRIMARY + Colors.BOLD)).strip()
            
            if choice == '1':
                self.dns_cache.enabled = not self.dns_cache.enabled
                print_success("Cache " + ("ENABLED" if self.dns_cache.enabled else "DISABLED"))
                time.sleep(1.5)
            elif choice == '2':
                confirm = input(colored("  ⚠️  Clear? [y/N]: ", Colors.NETGUARD_WARNING)).strip().lower()
                if confirm == 'y':
                    self.dns_cache.clear()
                    print_success("Cleared!")
                    time.sleep(1.5)
            elif choice == '3':
                animate_loading("Refreshing", 1)
            elif choice == '0':
                break
    
    def export_menu(self):
        """Export menu"""
        while True:
            clear_screen()
            print_header("💾 EXPORT & BACKUP", 80)
            
            print_menu_item("1", "Export Logs (CSV)", "📊")
            print_menu_item("2", "Export Statistics", "📈")
            print_menu_item("3", "Export Blocklist", "🚫")
            print_menu_item("0", "Back", "◀")
            
            print()
            choice = input(colored("  ➤ [0-3]: ", Colors.NETGUARD_PRIMARY + Colors.BOLD)).strip()
            
            if choice == '1':
                self.export_logs_csv()
            elif choice == '2':
                self.export_stats_report()
            elif choice == '3':
                self.export_blocklist()
            elif choice == '0':
                break
    
    def export_logs_csv(self):
        """Export CSV"""
        if not self.all_logs:
            print()
            print_warning("No logs")
            time.sleep(1.5)
            return
        
        filename = f"dns_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        print()
        animate_loading("Exporting", 2)
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'IP', 'Domain', 'Type', 'Details', 'Success', 'Blocked', 'Cached'])
                writer.writerows(self.all_logs)
            
            print_success(f"{format_number(len(self.all_logs))} → {colored(filename, Colors.BRIGHT_CYAN)}")
        except Exception as e:
            print_error(f"Failed: {e}")
        
        time.sleep(2)
    
    def export_stats_report(self):
        """Export stats"""
        filename = f"stats_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        print()
        animate_loading("Generating", 2)
        
        if export_stats_to_file(self.all_logs, filename):
            print_success(f"Saved → {colored(filename, Colors.BRIGHT_CYAN)}")
        else:
            print_error("Failed")
        
        time.sleep(2)
    
    def export_blocklist(self):
        """Export blocklist"""
        filename = f"blocklist_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        blocked, _ = self.blocklist.get_lists()
        
        print()
        animate_loading("Exporting", 2)
        
        try:
            with open(filename, 'w') as f:
                f.write(f"# NetGuard Blocklist - {datetime.datetime.now()}\n")
                f.write(f"# Total: {len(blocked)}\n\n")
                for domain in sorted(blocked):
                    f.write(f"{domain}\n")
            
            print_success(f"{format_number(len(blocked))} → {colored(filename, Colors.BRIGHT_CYAN)}")
        except Exception as e:
            print_error(f"Failed: {e}")
        
        time.sleep(2)
    
    def settings_menu(self):
        """Advanced settings"""
        while True:
            clear_screen()
            print_header("🔧 ADVANCED SETTINGS", 80)
            
            stats = self.stats_tracker.get_stats()
            uptime = str(datetime.timedelta(seconds=int(stats['uptime'])))
            
            print(colored("┌────────────────────────────────────────────────────────────┐", Colors.NETGUARD_INFO))
            print(colored("│", Colors.NETGUARD_INFO) +
                  f" Uptime: {colored(uptime, Colors.BRIGHT_CYAN)}".ljust(73) +
                  colored("│", Colors.NETGUARD_INFO))

            qps_str = f"{stats['queries_per_second']:.2f}"
            print(colored("│", Colors.NETGUARD_INFO) +
                  f" QPS:    {colored(qps_str, Colors.BRIGHT_CYAN)}".ljust(73) +
                  colored("│", Colors.NETGUARD_INFO))

            avg_str = f"{stats['avg_time']:.1f}ms"
            print(colored("│", Colors.NETGUARD_INFO) +
                  f" Avg:    {colored(avg_str, Colors.BRIGHT_CYAN)}".ljust(73) +
                  colored("│", Colors.NETGUARD_INFO))

            print(colored("└────────────────────────────────────────────────────────────┘", Colors.NETGUARD_INFO))
            print()
            
            print_menu_item("1", "Clear Logs", "🗑️")
            print_menu_item("2", "Clear Alerts", "🗑️")
            print_menu_item("3", "System Info", "ℹ️")
            print_menu_item("0", "Back", "◀")
            
            print()
            choice = input(colored("  ➤ [0-3]: ", Colors.NETGUARD_PRIMARY + Colors.BOLD)).strip()
            
            if choice == '1':
                confirm = input(colored("  ⚠️  Clear logs? [y/N]: ", Colors.NETGUARD_WARNING)).strip().lower()
                if confirm == 'y':
                    self.all_logs.clear()
                    print_success("Cleared!")
                    time.sleep(1.5)
            elif choice == '2':
                confirm = input(colored("  ⚠️  Clear alerts? [y/N]: ", Colors.NETGUARD_WARNING)).strip().lower()
                if confirm == 'y':
                    self.anomaly_detector.alerts.clear()
                    print_success("Cleared!")
                    time.sleep(1.5)
            elif choice == '3':
                self.show_system_info()
            elif choice == '0':
                break
    
    def show_system_info(self):
        """System info"""
        import platform
        import socket
        
        clear_screen()
        print_header("ℹ️  SYSTEM INFORMATION", 80)
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "Unknown"
        
        print(colored("  Application:", Colors.BRIGHT_WHITE + Colors.BOLD))
        print(f"    NetGuard DNS Monitor {colored(VERSION, Colors.BRIGHT_CYAN)}")
        print()
        
        print(colored("  System:", Colors.BRIGHT_WHITE + Colors.BOLD))
        print(f"    OS: {colored(platform.system() + ' ' + platform.release(), Colors.BRIGHT_CYAN)}")
        print(f"    Python: {colored(platform.python_version(), Colors.BRIGHT_CYAN)}")
        print(f"    IP: {colored(local_ip, Colors.NETGUARD_SUCCESS)}")
        print()
        
        print(colored("  DNS Server:", Colors.BRIGHT_WHITE + Colors.BOLD))
        print(f"    Port: {colored('53', Colors.BRIGHT_CYAN)}")
        print(f"    Primary: {colored('8.8.8.8', Colors.BRIGHT_CYAN)}")
        print(f"    Backup: {colored('1.1.1.1', Colors.BRIGHT_CYAN)}")
        
        print()
        print_separator("─", 80, Colors.NETGUARD_PRIMARY)
        input(colored("\n  Press Enter...", Colors.DIM))
    
    def exit_cli(self):
        """EPIC goodbye"""
        clear_screen()
        print()
        
        goodbye = """
  ╔══════════════════════════════════════════════════════════════╗
  ║                                                              ║
  ║                    Thank You!                                ║
  ║              🛡️  NetGuard DNS Monitor  🛡️                     ║
  ║                                                              ║
  ║                  Stay Protected!                             ║
  ║                                                              ║
  ╚══════════════════════════════════════════════════════════════╝
"""
        print(gradient_text(goodbye, Colors.NETGUARD_PRIMARY, Colors.NETGUARD_SECONDARY))
        
        stats = self.stats_tracker.get_stats()
        print()
        print(colored("  Session Summary:", Colors.BRIGHT_WHITE + Colors.BOLD))
        print(f"    Queries: {format_number(stats['total'])}")
        print(f"    Blocked: {format_number(stats['blocked'])}")
        print(f"    Uptime: {colored(str(datetime.timedelta(seconds=int(stats['uptime']))), Colors.BRIGHT_CYAN)}")
        print()
        
        print(colored("  Author: Jhapendra kandel ", Colors.DIM))
        print(colored("  Softwarica College (Coventry University)", Colors.DIM))
        print()
        
        self.running = False
        time.sleep(2)
        sys.exit(0)


# ═══════════════════════════════════════════════════════════════════════════
#                         ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def run_cli(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector):
    """Main entry point - Start the ULTIMATE CLI"""
    try:
        cli = DNSMonitorCLI(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector)
        cli.run()
    except KeyboardInterrupt:
        print()
        print_success("Terminated gracefully")
        sys.exit(0)
    except Exception as e:
        print()
        print_error(f"Error: {e}")
        sys.exit(1)