# NetGuard DNS Monitor - CLI Interface
# Command line interface for the DNS monitoring application
# This provides a terminal-based alternative to the GUI

# Author: 4A 68 61 70 65 6E 64 72 61 20 6B 61 6E 64 65 6C
# Project: 1st Year Python Programming
# Institution: Softwarica College of IT & E-Commerce (Coventry University)

VERSION = "2.2.0"

import os
import sys
import time
import datetime
import csv
import signal

# importing stats computation from our stats module
from stats import compute_stats, export_stats_to_file


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal styling"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    
    # foreground colors
    BLACK = '\033[30m'
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
    
    # background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def colored(text, color):
    """Return colored text"""
    return color + str(text) + Colors.RESET


def print_header(title):
    """Print a styled header"""
    width = 70
    print()
    print(colored("=" * width, Colors.CYAN))
    print(colored("  " + title, Colors.BRIGHT_CYAN + Colors.BOLD))
    print(colored("=" * width, Colors.CYAN))
    print()


def print_separator():
    """Print a separator line"""
    print(colored("-" * 70, Colors.DIM))


def print_menu_item(number, text, icon=""):
    """Print a menu item"""
    num_colored = colored("[" + number + "]", Colors.BRIGHT_CYAN)
    print("  " + num_colored + " " + icon + " " + text)


class DNSMonitorCLI:
    """Command Line Interface for NetGuard DNS Monitor"""
    
    def __init__(self, log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector):
        self.log_queue = log_queue
        self.all_logs = all_logs
        self.stats_tracker = stats_tracker
        self.dns_cache = dns_cache
        self.blocklist = blocklist
        self.anomaly_detector = anomaly_detector
        
        self.running = True
        self.live_mode = False
        
        # handle ctrl+c gracefully
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C"""
        self.live_mode = False
        self.running = True
        print(colored("\n\n  Interrupted! Returning to menu...", Colors.YELLOW))
        time.sleep(1)
    
    def run(self):
        """Main CLI loop"""
        while self.running:
            self.show_main_menu()
    
    def show_main_menu(self):
        """Display main menu"""
        clear_screen()
        self.print_banner()
        
        print_header("  MAIN MENU")
        
        # quick stats display
        stats = self.stats_tracker.get_stats()
        cache_stats = self.dns_cache.get_stats()
        
        # format stats values
        total_queries = "{:,}".format(stats['total'])
        blocked_queries = "{:,}".format(stats['blocked'])
        cached_queries = "{:,}".format(stats['cached'])
        
        # cache status
        if self.dns_cache.enabled:
            cache_status = colored("ON", Colors.GREEN)
        else:
            cache_status = colored("OFF", Colors.RED)
        
        print("  " + colored("Quick Stats:", Colors.BRIGHT_WHITE + Colors.BOLD))
        print("    Queries: " + colored(total_queries, Colors.BRIGHT_GREEN) + "  |  " +
              "Blocked: " + colored(blocked_queries, Colors.BRIGHT_RED) + "  |  " +
              "Cached: " + colored(cached_queries, Colors.BRIGHT_BLUE) + "  |  " +
              "Cache: " + cache_status)
        print()
        print_separator()
        print()
        
        print_menu_item("1", "Live DNS Logs", "")
        print_menu_item("2", "View Statistics", "")
        print_menu_item("3", "Blocklist Management", "")
        print_menu_item("4", "Security Alerts", "")
        print_menu_item("5", "Cache Control", "")
        print_menu_item("6", "Export Data", "")
        print_menu_item("7", "Settings", "")
        print_menu_item("0", "Exit", "")
        
        print()
        print_separator()
        
        choice = input(colored("\n  Enter choice [0-7]: ", Colors.BRIGHT_CYAN)).strip()
        
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
        elif choice == '0':
            self.exit_cli()
        else:
            print(colored("  Invalid choice!", Colors.RED))
            time.sleep(1)
    
    def print_banner(self):
        """Print small banner for menus"""
        print()
        banner_text = colored("  NetGuard DNS Monitor v2.2  ", Colors.BRIGHT_CYAN + Colors.BOLD)
        mode_text = colored("| CLI Mode", Colors.DIM)
        print(banner_text + mode_text)
        print()
    
    def show_live_logs(self):
        """Show live DNS logs"""
        clear_screen()
        print_header(" LIVE DNS LOGS")
        
        print(colored("  Showing real-time DNS queries...", Colors.DIM))
        print(colored("  Press Ctrl+C to return to menu", Colors.YELLOW))
        print()
        print_separator()
        
        # print header row
        header = "{:<12} {:<16} {:<40} {:<6} {:<10}".format("TIME", "SOURCE IP", "DOMAIN", "TYPE", "STATUS")
        print(colored(header, Colors.BRIGHT_WHITE + Colors.BOLD))
        print_separator()
        
        self.live_mode = True
        last_count = len(self.all_logs)
        
        try:
            while self.live_mode:
                # check for new logs
                current_count = len(self.all_logs)
                
                if current_count > last_count:
                    # display new logs
                    new_logs = self.all_logs[last_count:current_count]
                    
                    for log in new_logs:
                        timestamp, ip, domain, qtype, details, success, blocked, cached = log
                        
                        # format time to show only time part
                        if ' ' in timestamp:
                            time_str = timestamp.split(' ')[1][:8]
                        else:
                            time_str = timestamp[:8]
                        
                        # truncate domain if too long
                        if len(domain) > 38:
                            domain = domain[:35] + "..."
                        
                        # determine status and color
                        if blocked:
                            status = "BLOCKED"
                            color = Colors.BRIGHT_RED
                        elif cached:
                            status = "CACHED"
                            color = Colors.BRIGHT_BLUE
                        elif success:
                            status = "OK"
                            color = Colors.BRIGHT_GREEN
                        else:
                            status = "FAILED"
                            color = Colors.RED
                        
                        line = "{:<12} {:<16} {:<40} {:<6} ".format(time_str, ip, domain, qtype)
                        status_colored = colored("{:<10}".format(status), color)
                        print(line + status_colored)
                    
                    last_count = current_count
                
                time.sleep(0.2)
                
        except KeyboardInterrupt:
            pass
        
        self.live_mode = False
        print()
        print(colored("  Returning to menu...", Colors.YELLOW))
        time.sleep(1)
    
    def show_statistics(self):
        """Show statistics"""
        clear_screen()
        print_header(" DNS STATISTICS")
        
        if not self.all_logs:
            print(colored("  No data available yet.", Colors.YELLOW))
            print(colored("  Configure devices to use this DNS server to start monitoring.", Colors.DIM))
        else:
            # get stats from our stats module
            stats_text = compute_stats(self.all_logs)
            
            # print with color formatting
            for line in stats_text.split('\n'):
                if line.startswith('===') or line.startswith('---'):
                    print(colored(line, Colors.CYAN))
                elif line.startswith('📊') or line.startswith('🌐') or line.startswith('📱'):
                    print(colored(line, Colors.BRIGHT_CYAN + Colors.BOLD))
                elif line.startswith('🚫') or line.startswith('🔍') or line.startswith('💡'):
                    print(colored(line, Colors.BRIGHT_CYAN + Colors.BOLD))
                elif line.startswith('🔬'):
                    print(colored(line, Colors.BRIGHT_CYAN + Colors.BOLD))
                elif '✓' in line or '✅' in line:
                    print(colored(line, Colors.GREEN))
                elif '✗' in line or '⚠️' in line:
                    print(colored(line, Colors.YELLOW))
                elif 'BLOCKED' in line or '🚫' in line:
                    print(colored(line, Colors.RED))
                else:
                    print(line)
        
        print()
        print_separator()
        input(colored("\n  Press Enter to continue...", Colors.DIM))
    
    def blocklist_menu(self):
        """Blocklist management menu"""
        while True:
            clear_screen()
            print_header(" BLOCKLIST MANAGEMENT")
            
            blocked, allowed = self.blocklist.get_lists()
            blocked_count = "{:,}".format(len(blocked))
            allowed_count = "{:,}".format(len(allowed))
            
            print("  Blocked domains: " + colored(blocked_count, Colors.RED))
            print("  Allowed domains: " + colored(allowed_count, Colors.GREEN))
            print()
            print_separator()
            print()
            
            print_menu_item("1", "View Blocked Domains", "")
            print_menu_item("2", "View Allowed Domains", "")
            print_menu_item("3", "Add Domain to Blocklist", "")
            print_menu_item("4", "Add Domain to Allowlist", "")
            print_menu_item("5", "Remove from Blocklist", "")
            print_menu_item("6", "Remove from Allowlist", "")
            print_menu_item("7", "Search Blocklist", "")
            print_menu_item("8", "Load Default Blocklist", "")
            print_menu_item("9", "Import from File", "")
            print_menu_item("0", "Back to Main Menu", "")
            
            print()
            choice = input(colored("  Enter choice [0-9]: ", Colors.BRIGHT_CYAN)).strip()
            
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
        """View blocked domains with pagination"""
        clear_screen()
        print_header(" BLOCKED DOMAINS")
        
        blocked, _ = self.blocklist.get_lists()
        blocked = sorted(blocked)
        
        if not blocked:
            print(colored("  No blocked domains.", Colors.YELLOW))
            input(colored("\n  Press Enter to continue...", Colors.DIM))
            return
        
        page_size = 20
        total_pages = (len(blocked) + page_size - 1) // page_size
        current_page = 1
        
        while True:
            clear_screen()
            title = " BLOCKED DOMAINS (Page {}/{})".format(current_page, total_pages)
            print_header(title)
            
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(blocked))
            
            for i, domain in enumerate(blocked[start_idx:end_idx], start=start_idx + 1):
                num_str = colored("{:4d}.".format(i), Colors.DIM)
                print("  " + num_str + " " + domain)
            
            print()
            print_separator()
            total_str = "{:,}".format(len(blocked))
            print("  Total: " + colored(total_str, Colors.RED) + " domains")
            print()
            print("  " + colored("[N]", Colors.CYAN) + " Next  " + 
                  colored("[P]", Colors.CYAN) + " Previous  " + 
                  colored("[Q]", Colors.CYAN) + " Quit")
            
            choice = input(colored("\n  Choice: ", Colors.BRIGHT_CYAN)).strip().lower()
            
            if choice == 'n' and current_page < total_pages:
                current_page += 1
            elif choice == 'p' and current_page > 1:
                current_page -= 1
            elif choice == 'q':
                break
    
    def view_allowed_domains(self):
        """View allowed domains"""
        clear_screen()
        print_header(" ALLOWED DOMAINS (WHITELIST)")
        
        _, allowed = self.blocklist.get_lists()
        allowed = sorted(allowed)
        
        if not allowed:
            print(colored("  No allowed domains.", Colors.YELLOW))
        else:
            for i, domain in enumerate(allowed, start=1):
                num_str = colored("{:4d}.".format(i), Colors.DIM)
                domain_str = colored(domain, Colors.GREEN)
                print("  " + num_str + " " + domain_str)
            print()
            total_str = "{:,}".format(len(allowed))
            print("  Total: " + colored(total_str, Colors.GREEN) + " domains")
        
        input(colored("\n  Press Enter to continue...", Colors.DIM))
    
    def add_blocked_domain(self):
        """Add domain to blocklist"""
        print()
        domain = input(colored("  Enter domain to block: ", Colors.BRIGHT_CYAN)).strip().lower()
        
        if domain:
            self.blocklist.add_blocked(domain)
            print(colored("  Added '" + domain + "' to blocklist.", Colors.GREEN))
        else:
            print(colored("  Cancelled.", Colors.YELLOW))
        
        time.sleep(1)
    
    def add_allowed_domain(self):
        """Add domain to allowlist"""
        print()
        domain = input(colored("  Enter domain to allow: ", Colors.BRIGHT_CYAN)).strip().lower()
        
        if domain:
            self.blocklist.add_allowed(domain)
            print(colored("  Added '" + domain + "' to allowlist.", Colors.GREEN))
        else:
            print(colored("  Cancelled.", Colors.YELLOW))
        
        time.sleep(1)
    
    def remove_blocked_domain(self):
        """Remove domain from blocklist"""
        print()
        domain = input(colored("  Enter domain to unblock: ", Colors.BRIGHT_CYAN)).strip().lower()
        
        if domain:
            self.blocklist.remove_blocked(domain)
            print(colored("  Removed '" + domain + "' from blocklist.", Colors.GREEN))
        else:
            print(colored("  Cancelled.", Colors.YELLOW))
        
        time.sleep(1)
    
    def remove_allowed_domain(self):
        """Remove domain from allowlist"""
        print()
        domain = input(colored("  Enter domain to remove from allowlist: ", Colors.BRIGHT_CYAN)).strip().lower()
        
        if domain:
            self.blocklist.remove_allowed(domain)
            print(colored("  Removed '" + domain + "' from allowlist.", Colors.GREEN))
        else:
            print(colored("  Cancelled.", Colors.YELLOW))
        
        time.sleep(1)
    
    def search_blocklist(self):
        """Search blocklist"""
        print()
        search_term = input(colored("  Enter search term: ", Colors.BRIGHT_CYAN)).strip().lower()
        
        if not search_term:
            print(colored("  Cancelled.", Colors.YELLOW))
            time.sleep(1)
            return
        
        blocked, _ = self.blocklist.get_lists()
        results = [d for d in blocked if search_term in d.lower()]
        
        clear_screen()
        title = " SEARCH RESULTS: '" + search_term + "'"
        print_header(title)
        
        if not results:
            print(colored("  No matching domains found.", Colors.YELLOW))
        else:
            for i, domain in enumerate(sorted(results)[:50], start=1):
                # highlight matching part
                highlighted = domain.replace(search_term, colored(search_term, Colors.BRIGHT_YELLOW + Colors.BOLD))
                num_str = colored("{:4d}.".format(i), Colors.DIM)
                print("  " + num_str + " " + highlighted)
            
            if len(results) > 50:
                remaining = len(results) - 50
                print(colored("\n  ... and " + str(remaining) + " more results", Colors.DIM))
            
            print()
            result_count = "{:,}".format(len(results))
            print("  Found: " + colored(result_count, Colors.GREEN) + " matching domains")
        
        input(colored("\n  Press Enter to continue...", Colors.DIM))
    
    def load_default_blocklist(self):
        """Load default blocklist"""
        print()
        confirm = input(colored("  Load default ad/tracker blocklist? [y/N]: ", Colors.BRIGHT_CYAN)).strip().lower()
        
        if confirm == 'y':
            self.blocklist.load_default_blocklist()
            blocked, _ = self.blocklist.get_lists()
            count_str = "{:,}".format(len(blocked))
            print(colored("  Loaded default blocklist. Total: " + count_str + " domains", Colors.GREEN))
        else:
            print(colored("  Cancelled.", Colors.YELLOW))
        
        time.sleep(1.5)
    
    def import_blocklist_file(self):
        """Import blocklist from file"""
        print()
        filename = input(colored("  Enter file path: ", Colors.BRIGHT_CYAN)).strip()
        
        if not filename:
            print(colored("  Cancelled.", Colors.YELLOW))
            time.sleep(1)
            return
        
        if not os.path.exists(filename):
            print(colored("  File not found: " + filename, Colors.RED))
            time.sleep(1.5)
            return
        
        count = self.blocklist.import_from_file(filename)
        count_str = "{:,}".format(count)
        print(colored("  Imported " + count_str + " domains from file.", Colors.GREEN))
        time.sleep(1.5)
    
    def show_alerts(self):
        """Show security alerts"""
        clear_screen()
        print_header(" SECURITY ALERTS")
        
        alerts = self.anomaly_detector.get_alerts()
        
        if not alerts:
            print(colored("  No security alerts detected.", Colors.GREEN))
            print()
            print(colored("  The system monitors for:", Colors.DIM))
            print(colored("    - Excessive queries (DDoS indicators)", Colors.DIM))
            print(colored("    - Suspicious domain keywords", Colors.DIM))
            print(colored("    - DGA (Domain Generation Algorithm) patterns", Colors.DIM))
        else:
            alert_count = str(len(alerts))
            print("  " + colored(alert_count, Colors.RED) + " security alert(s) detected:\n")
            
            for alert in reversed(alerts):
                severity = alert['severity']
                timestamp = datetime.datetime.fromtimestamp(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                
                if severity == 'HIGH':
                    sev_color = Colors.BRIGHT_RED
                elif severity == 'MEDIUM':
                    sev_color = Colors.BRIGHT_YELLOW
                else:
                    sev_color = Colors.BRIGHT_BLUE
                
                time_str = colored("[" + timestamp + "]", Colors.DIM)
                sev_str = colored("[" + severity + "]", sev_color)
                print("  " + time_str + " " + sev_str)
                print("    " + alert['message'])
                print()
        
        print_separator()
        print()
        print("  " + colored("[C]", Colors.CYAN) + " Clear Alerts  " + 
              colored("[R]", Colors.CYAN) + " Refresh  " + 
              colored("[Q]", Colors.CYAN) + " Quit")
        
        choice = input(colored("\n  Choice: ", Colors.BRIGHT_CYAN)).strip().lower()
        
        if choice == 'c':
            self.anomaly_detector.alerts.clear()
            print(colored("  Alerts cleared.", Colors.GREEN))
            time.sleep(1)
        elif choice == 'r':
            self.show_alerts()
    
    def cache_menu(self):
        """Cache control menu"""
        while True:
            clear_screen()
            print_header(" CACHE CONTROL")
            
            cache_stats = self.dns_cache.get_stats()
            
            if self.dns_cache.enabled:
                status = colored("ENABLED", Colors.GREEN)
            else:
                status = colored("DISABLED", Colors.RED)
            
            size_str = "{:,}".format(cache_stats['size'])
            max_size_str = "{:,}".format(cache_stats['max_size'])
            hits_str = "{:,}".format(cache_stats['hits'])
            misses_str = "{:,}".format(cache_stats['misses'])
            hit_rate_str = "{:.1f}%".format(cache_stats['hit_rate'])
            
            print("  Cache Status: " + status)
            print("  Cache Size: " + colored(size_str, Colors.CYAN) + " / " + max_size_str + " entries")
            print("  Cache Hits: " + colored(hits_str, Colors.GREEN))
            print("  Cache Misses: " + colored(misses_str, Colors.YELLOW))
            print("  Hit Rate: " + colored(hit_rate_str, Colors.BRIGHT_CYAN))
            print()
            print_separator()
            print()
            
            if self.dns_cache.enabled:
                toggle_text = "Disable Cache"
            else:
                toggle_text = "Enable Cache"
            
            print_menu_item("1", toggle_text, "")
            print_menu_item("2", "Clear Cache", "")
            print_menu_item("3", "Refresh Stats", "")
            print_menu_item("0", "Back to Main Menu", "")
            
            print()
            choice = input(colored("  Enter choice [0-3]: ", Colors.BRIGHT_CYAN)).strip()
            
            if choice == '1':
                self.dns_cache.enabled = not self.dns_cache.enabled
                if self.dns_cache.enabled:
                    print(colored("  Cache ENABLED", Colors.GREEN))
                else:
                    print(colored("  Cache DISABLED", Colors.YELLOW))
                time.sleep(1)
            elif choice == '2':
                self.dns_cache.clear()
                print(colored("  Cache cleared.", Colors.GREEN))
                time.sleep(1)
            elif choice == '3':
                continue
            elif choice == '0':
                break
    
    def export_menu(self):
        """Export data menu"""
        while True:
            clear_screen()
            print_header(" EXPORT DATA")
            
            print_menu_item("1", "Export Logs to CSV", "")
            print_menu_item("2", "Export Statistics Report", "")
            print_menu_item("3", "Export Blocklist", "")
            print_menu_item("0", "Back to Main Menu", "")
            
            print()
            choice = input(colored("  Enter choice [0-3]: ", Colors.BRIGHT_CYAN)).strip()
            
            if choice == '1':
                self.export_logs_csv()
            elif choice == '2':
                self.export_stats_report()
            elif choice == '3':
                self.export_blocklist()
            elif choice == '0':
                break
    
    def export_logs_csv(self):
        """Export logs to CSV"""
        if not self.all_logs:
            print(colored("\n  No logs to export.", Colors.YELLOW))
            time.sleep(1.5)
            return
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = "dns_logs_" + timestamp + ".csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Source IP', 'Domain', 'Type', 
                               'Details', 'Success', 'Blocked', 'Cached'])
                writer.writerows(self.all_logs)
            
            log_count = "{:,}".format(len(self.all_logs))
            print(colored("\n  Exported " + log_count + " logs to " + filename, Colors.GREEN))
        except Exception as e:
            print(colored("\n  Export failed: " + str(e), Colors.RED))
        
        time.sleep(1.5)
    
    def export_stats_report(self):
        """Export statistics report"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = "dns_stats_" + timestamp + ".txt"
        
        if export_stats_to_file(self.all_logs, filename):
            print(colored("\n  Statistics exported to " + filename, Colors.GREEN))
        else:
            print(colored("\n  Export failed.", Colors.RED))
        
        time.sleep(1.5)
    
    def export_blocklist(self):
        """Export blocklist"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = "blocklist_" + timestamp + ".txt"
        blocked, _ = self.blocklist.get_lists()
        
        try:
            with open(filename, 'w') as f:
                f.write("# NetGuard DNS Monitor - Blocklist Export\n")
                f.write("# Generated: " + str(datetime.datetime.now()) + "\n")
                f.write("# Total: " + str(len(blocked)) + " domains\n\n")
                for domain in sorted(blocked):
                    f.write(domain + "\n")
            
            count_str = "{:,}".format(len(blocked))
            print(colored("\n  Exported " + count_str + " domains to " + filename, Colors.GREEN))
        except Exception as e:
            print(colored("\n  Export failed: " + str(e), Colors.RED))
        
        time.sleep(1.5)
    
    def settings_menu(self):
        """Settings menu"""
        while True:
            clear_screen()
            print_header(" SETTINGS")
            
            stats = self.stats_tracker.get_stats()
            
            # show system info
            uptime_str = "{:.0f}".format(stats['uptime'])
            qps_str = "{:.2f}".format(stats['queries_per_second'])
            avg_time_str = "{:.1f}".format(stats['avg_time'])
            
            print(colored("  System Information:", Colors.BRIGHT_WHITE + Colors.BOLD))
            print("    Uptime: " + colored(uptime_str, Colors.CYAN) + " seconds")
            print("    Queries/sec: " + colored(qps_str, Colors.CYAN))
            print("    Avg Response: " + colored(avg_time_str, Colors.CYAN) + " ms")
            print()
            print_separator()
            print()
            
            print_menu_item("1", "Clear All Logs", "")
            print_menu_item("2", "Clear All Alerts", "")
            print_menu_item("3", "Reset Statistics", "")
            print_menu_item("4", "System Information", "")
            print_menu_item("0", "Back to Main Menu", "")
            
            print()
            choice = input(colored("  Enter choice [0-4]: ", Colors.BRIGHT_CYAN)).strip()
            
            if choice == '1':
                confirm = input(colored("  Clear all logs? [y/N]: ", Colors.YELLOW)).strip().lower()
                if confirm == 'y':
                    self.all_logs.clear()
                    print(colored("  Logs cleared.", Colors.GREEN))
                    time.sleep(1)
            elif choice == '2':
                confirm = input(colored("  Clear all alerts? [y/N]: ", Colors.YELLOW)).strip().lower()
                if confirm == 'y':
                    self.anomaly_detector.alerts.clear()
                    print(colored("  Alerts cleared.", Colors.GREEN))
                    time.sleep(1)
            elif choice == '3':
                print(colored("  Note: Statistics reset requires restart.", Colors.YELLOW))
                time.sleep(1.5)
            elif choice == '4':
                self.show_system_info()
            elif choice == '0':
                break
    
    def show_system_info(self):
        """Show system information"""
        import platform
        import socket
        
        clear_screen()
        print_header(" SYSTEM INFORMATION")
        
        # get local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "Unable to determine"
        
        print(colored("  Application:", Colors.BRIGHT_WHITE + Colors.BOLD))
        print("    Version: " + colored(VERSION, Colors.CYAN))
        print("    Mode: " + colored("CLI", Colors.CYAN))
        print()
        
        print(colored("  System:", Colors.BRIGHT_WHITE + Colors.BOLD))
        platform_str = platform.system() + " " + platform.release()
        print("    Platform: " + colored(platform_str, Colors.CYAN))
        print("    Python: " + colored(platform.python_version(), Colors.CYAN))
        print("    Local IP: " + colored(local_ip, Colors.CYAN))
        print()
        
        print(colored("  DNS Server:", Colors.BRIGHT_WHITE + Colors.BOLD))
        print("    Port: " + colored("53", Colors.CYAN))
        print("    Primary DNS: " + colored("8.8.8.8", Colors.CYAN))
        print("    Backup DNS: " + colored("1.1.1.1", Colors.CYAN))
        
        print()
        print_separator()
        input(colored("\n  Press Enter to continue...", Colors.DIM))
    
    def exit_cli(self):
        """Exit CLI"""
        clear_screen()
        print()
        print(colored("  Thank you for using NetGuard DNS Monitor!", Colors.BRIGHT_CYAN))
        print(colored("  Goodbye!", Colors.GREEN))
        print()
        self.running = False
        sys.exit(0)


def run_cli(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector):
    """Entry point for CLI mode"""
    cli = DNSMonitorCLI(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector)
    cli.run()