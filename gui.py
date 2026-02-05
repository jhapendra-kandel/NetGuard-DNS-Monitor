"""
NetGuard DNS Monitor - Enhanced GUI Interface
Tkinter-based GUI with AJAX-like updates, cache control, and improved UX

Author: Jhapendra Kandel
Project: 1st Year Python Programming
Institution: Softwarica College of IT & E-Commerce (Coventry University)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, scrolledtext
import queue
import csv
import datetime
import threading
import requests
from stats import compute_stats
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter


class DNSMonitorGUI:
    def __init__(self, log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector):
        self.log_queue = log_queue
        self.all_logs = all_logs
        self.stats_tracker = stats_tracker
        self.dns_cache = dns_cache
        self.blocklist = blocklist
        self.anomaly_detector = anomaly_detector
        self.filter_text = ""
        self.filter_type = "All"
        self.paused = False
        self.last_stats_update = 0
        self.cache_enabled = True  # Cache control
        self.stats_scroll_position = 0  # Track scroll position
        
        self.root = tk.Tk()
        self.root.title("🛡️ NetGuard DNS Monitor v2.1")
        self.root.geometry("1150x850")
        
        self.create_menu()
        
        # Control bar at top
        self.create_control_bar()
        
        self.status_bar = tk.Label(self.root, text="DNS Monitor Running", 
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W, font=('Arial', 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        self.create_logs_tab()
        self.create_stats_tab()
        self.create_blocklist_tab()
        self.create_alerts_tab()
        
        self.update_gui()
        
    def create_control_bar(self):
        """Create control bar with cache toggle and other controls"""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        # Cache control
        cache_frame = ttk.LabelFrame(control_frame, text="Cache Control", padding=5)
        cache_frame.pack(side='left', padx=5)
        
        self.cache_status_label = ttk.Label(cache_frame, text="✓ Enabled", 
                                            foreground='green', font=('Arial', 9, 'bold'))
        self.cache_status_label.pack(side='left', padx=5)
        
        self.cache_toggle_btn = ttk.Button(cache_frame, text="Disable Cache", 
                                           command=self.toggle_cache)
        self.cache_toggle_btn.pack(side='left', padx=5)
        
        # Quick stats
        stats_frame = ttk.LabelFrame(control_frame, text="Quick Stats", padding=5)
        stats_frame.pack(side='left', padx=5)
        
        self.quick_stats_label = ttk.Label(stats_frame, text="Queries: 0 | Blocked: 0 | Cached: 0", 
                                           font=('Arial', 9))
        self.quick_stats_label.pack()
        
    def toggle_cache(self):
        """Toggle DNS caching on/off"""
        self.cache_enabled = not self.cache_enabled
        
        if self.cache_enabled:
            self.cache_status_label.config(text="✓ Enabled", foreground='green')
            self.cache_toggle_btn.config(text="Disable Cache")
            messagebox.showinfo("Cache Enabled", 
                              "DNS caching is now ENABLED.\n\n"
                              "Queries will be cached for faster responses.")
        else:
            self.cache_status_label.config(text="✗ Disabled", foreground='red')
            self.cache_toggle_btn.config(text="Enable Cache")
            # Clear existing cache
            self.dns_cache.clear()
            messagebox.showinfo("Cache Disabled", 
                              "DNS caching is now DISABLED.\n\n"
                              "All queries will go directly to upstream DNS.\n"
                              "Existing cache has been cleared.")
        
        # Update cache enabled flag in the cache object
        self.dns_cache.enabled = self.cache_enabled
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Logs (CSV)", command=self.export_logs)
        file_menu.add_command(label="Export Statistics", command=self.export_statistics)
        file_menu.add_command(label="Clear Logs", command=self.clear_logs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Pause/Resume Logging", command=self.toggle_pause)
        view_menu.add_command(label="Refresh Statistics", command=self.force_refresh_stats)
        
        cache_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cache", menu=cache_menu)
        cache_menu.add_command(label="Toggle Cache (Enable/Disable)", command=self.toggle_cache)
        cache_menu.add_command(label="Clear Cache", command=self.clear_cache)
        cache_menu.add_command(label="Cache Statistics", command=self.show_cache_stats)
        
        blocklist_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Blocklist", menu=blocklist_menu)
        blocklist_menu.add_command(label="Import from File", command=self.import_blocklist_file)
        blocklist_menu.add_command(label="Import from GitHub URL", command=self.import_github_blocklist)
        blocklist_menu.add_command(label="Load Default Blocklist", command=self.load_default_blocklist)
        blocklist_menu.add_separator()
        blocklist_menu.add_command(label="Export Blocklist", command=self.export_blocklist)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="GitHub Blocklists", command=self.show_github_help)
        
    def create_logs_tab(self):
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text='📋 Live Logs')
        
        filter_frame = ttk.Frame(logs_frame)
        filter_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Filter:").pack(side='left', padx=5)
        self.filter_entry = ttk.Entry(filter_frame, width=30)
        self.filter_entry.pack(side='left', padx=5)
        self.filter_entry.bind('<KeyRelease>', lambda e: self.apply_filter())
        
        ttk.Label(filter_frame, text="Type:").pack(side='left', padx=(20, 5))
        self.type_filter = ttk.Combobox(filter_frame, width=10, 
                                        values=['All', 'A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'PTR'],
                                        state='readonly')
        self.type_filter.set('All')
        self.type_filter.pack(side='left', padx=5)
        self.type_filter.bind('<<ComboboxSelected>>', lambda e: self.apply_filter())
        
        ttk.Button(filter_frame, text="Clear Filter", 
                  command=self.clear_filter).pack(side='left', padx=5)
        
        tree_frame = ttk.Frame(logs_frame)
        tree_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(tree_frame, 
                                 columns=('Timestamp', 'Source IP', 'Query Domain', 
                                         'Type', 'Details', 'Status'),
                                 show='headings',
                                 yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading('Timestamp', text='Timestamp')
        self.tree.heading('Source IP', text='Source IP')
        self.tree.heading('Query Domain', text='Query Domain')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Details', text='Details')
        self.tree.heading('Status', text='Status')
        
        self.tree.column('Timestamp', width=160)
        self.tree.column('Source IP', width=120)
        self.tree.column('Query Domain', width=300)
        self.tree.column('Type', width=70)
        self.tree.column('Details', width=200)
        self.tree.column('Status', width=100)
        
        self.tree.pack(expand=True, fill='both')
        
        self.tree.tag_configure('success', foreground='green')
        self.tree.tag_configure('failed', foreground='red')
        self.tree.tag_configure('blocked', foreground='orange')
        self.tree.tag_configure('cached', foreground='blue')
        
    def create_stats_tab(self):
        """Create statistics tab with AJAX-like updates (no auto-scroll)"""
        stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(stats_tab, text='📊 Statistics & Analytics')
        
        # Refresh button at top
        refresh_frame = ttk.Frame(stats_tab)
        refresh_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(refresh_frame, text="🔄 Refresh Statistics", 
                  command=self.force_refresh_stats).pack(side='left', padx=5)
        
        ttk.Label(refresh_frame, text="Auto-refresh: Every 10s when tab active", 
                 font=('Arial', 9, 'italic')).pack(side='left', padx=10)
        
        # Scrollable canvas for stats
        canvas = tk.Canvas(stats_tab, bg='white')
        scrollbar = ttk.Scrollbar(stats_tab, orient="vertical", command=canvas.yview)
        self.stats_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        self.stats_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        self.stats_canvas_window = canvas.create_window((0, 0), window=self.stats_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Save canvas and scrollbar references
        self.stats_canvas = canvas
        self.stats_scrollbar = scrollbar
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Track scroll position
        def on_scroll(*args):
            self.stats_scroll_position = canvas.yview()[0]
            scrollbar.set(*args)
        
        canvas.configure(yscrollcommand=on_scroll)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initial message
        tk.Label(self.stats_frame, text="Loading statistics...", 
                font=("Arial", 12)).pack(pady=20)
    
    def on_tab_changed(self, event):
        """Handle tab change event"""
        selected_tab = self.notebook.index(self.notebook.select())
        if selected_tab == 1:  # Statistics tab
            # Force refresh when switching to stats tab
            self.force_refresh_stats()
    
    def update_stats_display(self):
        """Update statistics display without resetting scroll position"""
        if not self.all_logs:
            return
        
        # Save current scroll position
        saved_position = self.stats_scroll_position
        
        # Clear old widgets
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Compute fresh stats
        stats_text = compute_stats(self.all_logs)
        
        # Create text widget for stats
        stats_display = tk.Text(self.stats_frame, wrap='word', height=30, 
                               font=('Courier', 9), bg='white', relief='flat')
        stats_display.insert('1.0', stats_text)
        stats_display.config(state='disabled')
        stats_display.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create charts
        self.create_charts()
        
        # Restore scroll position after a short delay (allows widgets to render)
        self.root.after(100, lambda: self.stats_canvas.yview_moveto(saved_position))
    
    def force_refresh_stats(self):
        """Force refresh statistics (manual refresh button)"""
        self.update_stats_display()
        messagebox.showinfo("Statistics Refreshed", 
                           "Statistics have been updated with latest data.")
        
    def create_blocklist_tab(self):
        """Enhanced blocklist tab with GitHub import"""
        blocklist_frame = ttk.Frame(self.notebook)
        self.notebook.add(blocklist_frame, text='🚫 Blocklist Manager')
        
        # Control buttons
        btn_frame = ttk.Frame(blocklist_frame)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame, text="➕ Add Blocked Domain", 
                  command=self.add_blocked_domain).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="➕ Add Allowed Domain", 
                  command=self.add_allowed_domain).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📁 Import from File", 
                  command=self.import_blocklist_file).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🌐 Import from GitHub", 
                  command=self.import_github_blocklist).pack(side='left', padx=5)
        
        btn_frame2 = ttk.Frame(blocklist_frame)
        btn_frame2.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Button(btn_frame2, text="🔄 Load Default Ads/Trackers", 
                  command=self.load_default_blocklist).pack(side='left', padx=5)
        ttk.Button(btn_frame2, text="💾 Export Blocklist", 
                  command=self.export_blocklist).pack(side='left', padx=5)
        
        # Lists frame
        lists_frame = ttk.Frame(blocklist_frame)
        lists_frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Blocked list
        blocked_frame = ttk.LabelFrame(lists_frame, text="Blocked Domains", padding=10)
        blocked_frame.pack(side='left', expand=True, fill='both', padx=5)
        
        # Search for blocked
        search_blocked_frame = ttk.Frame(blocked_frame)
        search_blocked_frame.pack(fill='x', pady=(0, 5))
        ttk.Label(search_blocked_frame, text="Search:").pack(side='left', padx=5)
        self.blocked_search = ttk.Entry(search_blocked_frame)
        self.blocked_search.pack(side='left', fill='x', expand=True, padx=5)
        self.blocked_search.bind('<KeyRelease>', lambda e: self.filter_blocked_list())
        
        blocked_scroll = ttk.Scrollbar(blocked_frame)
        blocked_scroll.pack(side='right', fill='y')
        
        self.blocked_listbox = tk.Listbox(blocked_frame, selectmode=tk.SINGLE,
                                          yscrollcommand=blocked_scroll.set)
        self.blocked_listbox.pack(expand=True, fill='both')
        blocked_scroll.config(command=self.blocked_listbox.yview)
        
        blocked_count_label = ttk.Label(blocked_frame, text="Count: 0", font=('Arial', 9, 'bold'))
        blocked_count_label.pack(pady=5)
        self.blocked_count_label = blocked_count_label
        
        ttk.Button(blocked_frame, text="Remove Selected", 
                  command=self.remove_blocked).pack(pady=5)
        
        # Allowed list
        allowed_frame = ttk.LabelFrame(lists_frame, text="Allowed Domains (Whitelist)", padding=10)
        allowed_frame.pack(side='left', expand=True, fill='both', padx=5)
        
        # Search for allowed
        search_allowed_frame = ttk.Frame(allowed_frame)
        search_allowed_frame.pack(fill='x', pady=(0, 5))
        ttk.Label(search_allowed_frame, text="Search:").pack(side='left', padx=5)
        self.allowed_search = ttk.Entry(search_allowed_frame)
        self.allowed_search.pack(side='left', fill='x', expand=True, padx=5)
        self.allowed_search.bind('<KeyRelease>', lambda e: self.filter_allowed_list())
        
        allowed_scroll = ttk.Scrollbar(allowed_frame)
        allowed_scroll.pack(side='right', fill='y')
        
        self.allowed_listbox = tk.Listbox(allowed_frame, selectmode=tk.SINGLE,
                                          yscrollcommand=allowed_scroll.set)
        self.allowed_listbox.pack(expand=True, fill='both')
        allowed_scroll.config(command=self.allowed_listbox.yview)
        
        allowed_count_label = ttk.Label(allowed_frame, text="Count: 0", font=('Arial', 9, 'bold'))
        allowed_count_label.pack(pady=5)
        self.allowed_count_label = allowed_count_label
        
        ttk.Button(allowed_frame, text="Remove Selected", 
                  command=self.remove_allowed).pack(pady=5)
        
        self.update_blocklist_display()
    
    def filter_blocked_list(self):
        """Filter blocked domains list based on search"""
        search_term = self.blocked_search.get().lower()
        self.update_blocklist_display(blocked_filter=search_term)
    
    def filter_allowed_list(self):
        """Filter allowed domains list based on search"""
        search_term = self.allowed_search.get().lower()
        self.update_blocklist_display(allowed_filter=search_term)
    
    def import_github_blocklist(self):
        """Import blocklist from GitHub URL"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Import from GitHub")
        dialog.geometry("600x400")
        
        ttk.Label(dialog, text="Enter GitHub Blocklist URL:", 
                 font=('Arial', 11, 'bold')).pack(pady=10)
        
        url_entry = ttk.Entry(dialog, width=70)
        url_entry.pack(padx=10, pady=5)
        
        # Pre-fill with popular blocklist
        url_entry.insert(0, "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts")
        
        ttk.Label(dialog, text="Popular Blocklists:", 
                 font=('Arial', 10, 'bold')).pack(pady=(15, 5))
        
        # List of popular blocklists
        lists_frame = ttk.Frame(dialog)
        lists_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        lists_text = scrolledtext.ScrolledText(lists_frame, height=10, wrap='word')
        lists_text.pack(fill='both', expand=True)
        
        popular_lists = """1. StevenBlack's Unified Hosts (Recommended)
   https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts
   
2. StevenBlack's + Fakenews
   https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews/hosts
   
3. AdAway Default Blocklist
   https://adaway.org/hosts.txt
   
4. Dan Pollock's Hosts
   https://someonewhocares.org/hosts/hosts
   
5. MVPS Hosts
   https://winhelp2002.mvps.org/hosts.txt

Click on a URL above, copy it, and paste into the field above."""
        
        lists_text.insert('1.0', popular_lists)
        lists_text.config(state='disabled')
        
        def do_import():
            url = url_entry.get().strip()
            if not url:
                messagebox.showwarning("No URL", "Please enter a URL")
                return
            
            # Show progress
            progress = ttk.Progressbar(dialog, mode='indeterminate')
            progress.pack(fill='x', padx=10, pady=10)
            progress.start()
            
            def import_thread():
                try:
                    count = self.blocklist.import_from_url(url)
                    progress.stop()
                    dialog.destroy()
                    self.update_blocklist_display()
                    messagebox.showinfo("Import Complete", 
                                       f"Successfully imported {count} domains from GitHub!")
                except Exception as e:
                    progress.stop()
                    messagebox.showerror("Import Failed", 
                                        f"Failed to import blocklist:\n{str(e)}")
            
            # Run import in thread to avoid blocking UI
            thread = threading.Thread(target=import_thread, daemon=True)
            thread.start()
        
        ttk.Button(dialog, text="Import", command=do_import).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()
    
    def import_blocklist_file(self):
        """Import blocklist from local file"""
        filename = filedialog.askopenfilename(
            title="Select Blocklist File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            count = self.blocklist.import_from_file(filename)
            self.update_blocklist_display()
            messagebox.showinfo("Import Complete", 
                               f"Imported {count} domains from {filename}")
    
    def export_blocklist(self):
        """Export current blocklist to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"blocklist_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            blocked, allowed = self.blocklist.get_lists()
            try:
                with open(filename, 'w') as f:
                    f.write("# NetGuard DNS Monitor - Blocklist Export\n")
                    f.write(f"# Generated: {datetime.datetime.now()}\n")
                    f.write(f"# Total domains: {len(blocked)}\n\n")
                    for domain in sorted(blocked):
                        f.write(f"{domain}\n")
                messagebox.showinfo("Export Complete", 
                                   f"Exported {len(blocked)} domains to {filename}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Error: {e}")
    
    def show_github_help(self):
        """Show help about GitHub blocklists"""
        help_text = """GitHub Blocklist Support

NetGuard DNS Monitor supports importing blocklists from GitHub and other URLs.

Popular Blocklists:

1. StevenBlack's Unified Hosts (Recommended)
   • Combines multiple reputable hosts files
   • Blocks ads, malware, and tracking
   • URL: https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts

2. How to Import:
   • Menu → Blocklist → Import from GitHub URL
   • Paste the URL
   • Click Import
   • Wait for download to complete

3. Supported Formats:
   • Hosts file format (IP domain)
   • Plain domain list (one per line)
   • Comments starting with # are ignored

4. Benefits:
   • Block thousands of ads and trackers
   • Improve privacy and security
   • Speed up browsing (fewer ads to load)
   • Reduce bandwidth usage

5. Note:
   • Large blocklists may take time to import
   • You can combine multiple sources
   • Use allowlist for sites you need"""
        
        messagebox.showinfo("GitHub Blocklists Help", help_text)
    
    def create_alerts_tab(self):
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text='⚠️ Security Alerts')
        
        # Controls
        ctrl_frame = ttk.Frame(alerts_frame)
        ctrl_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(ctrl_frame, text="Clear All Alerts", 
                  command=self.clear_alerts).pack(side='left', padx=5)
        ttk.Button(ctrl_frame, text="Refresh Alerts", 
                  command=self.update_alerts).pack(side='left', padx=5)
        
        # Alerts display
        alert_scroll = ttk.Scrollbar(alerts_frame)
        alert_scroll.pack(side='right', fill='y')
        
        self.alerts_text = tk.Text(alerts_frame, wrap='word', 
                                   yscrollcommand=alert_scroll.set,
                                   font=('Courier', 9))
        self.alerts_text.pack(expand=True, fill='both', padx=10, pady=5)
        alert_scroll.config(command=self.alerts_text.yview)
        
        # Color tags
        self.alerts_text.tag_configure('HIGH', foreground='red', font=('Courier', 9, 'bold'))
        self.alerts_text.tag_configure('MEDIUM', foreground='orange', font=('Courier', 9, 'bold'))
        self.alerts_text.tag_configure('LOW', foreground='blue', font=('Courier', 9, 'bold'))
    
    def update_logs(self):
        """Update logs display"""
        if self.paused:
            return
        
        while not self.log_queue.empty():
            try:
                item = self.log_queue.get_nowait()
                
                if isinstance(item, tuple) and item[0] == 'ALERT':
                    self.display_alert(item[1])
                else:
                    # Regular log entry
                    timestamp, ip, domain, qtype, details, success, blocked, cached = item
                    
                    # Apply filter
                    if self.filter_text and self.filter_text.lower() not in domain.lower() and \
                       self.filter_text.lower() not in ip.lower():
                        continue
                    
                    if self.filter_type != "All" and qtype != self.filter_type:
                        continue
                    
                    # Determine tag
                    if blocked:
                        tag = 'blocked'
                        status = 'BLOCKED'
                    elif cached:
                        tag = 'cached'
                        status = 'CACHED'
                    elif success:
                        tag = 'success'
                        status = 'SUCCESS'
                    else:
                        tag = 'failed'
                        status = 'FAILED'
                    
                    self.tree.insert('', 0, values=(timestamp, ip, domain, qtype, details, status), 
                                    tags=(tag,))
                    
                    # Limit tree size
                    if len(self.tree.get_children()) > 1000:
                        self.tree.delete(self.tree.get_children()[-1])
            
            except queue.Empty:
                break
            except Exception as e:
                print(f"Error updating logs: {e}")
    
    def update_gui(self):
        """Main GUI update loop - AJAX-like (no reload)"""
        self.update_logs()
        
        # Update stats only if on stats tab and enough time passed
        current_time = datetime.datetime.now().timestamp()
        if self.notebook.index(self.notebook.select()) == 1:  # Stats tab
            if current_time - self.last_stats_update > 10:  # Every 10 seconds
                self.update_stats_display()
                self.last_stats_update = current_time
        
        # Update alerts
        if self.notebook.index(self.notebook.select()) == 3:  # Alerts tab
            self.update_alerts()
        
        # Update status bar
        stats = self.stats_tracker.get_stats()
        cache_stats = self.dns_cache.get_stats()
        
        cache_status = "ON" if self.cache_enabled else "OFF"
        status_text = f"Queries: {stats['total']:,} | Blocked: {stats['blocked']:,} | "
        status_text += f"Cached: {stats['cached']:,} | Cache: {cache_status} ({cache_stats['hit_rate']:.1f}% hit rate) | "
        status_text += "PAUSED" if self.paused else "Running ✓"
        
        self.status_bar.config(text=status_text)
        
        # Update quick stats
        self.quick_stats_label.config(
            text=f"Queries: {stats['total']:,} | Blocked: {stats['blocked']:,} | Cached: {stats['cached']:,}"
        )
        
        # Schedule next update
        self.root.after(500, self.update_gui)
    
    def update_alerts(self):
        """Update alerts display"""
        alerts = self.anomaly_detector.get_alerts()
        
        # Don't clear if no new alerts
        if not alerts:
            return
        
        self.alerts_text.delete(1.0, tk.END)
        
        if not alerts:
            self.alerts_text.insert(tk.END, "No security alerts detected.\n\n")
            self.alerts_text.insert(tk.END, "The system is monitoring for:\n")
            self.alerts_text.insert(tk.END, "• Excessive queries (DDoS indicators)\n")
            self.alerts_text.insert(tk.END, "• Suspicious domain keywords\n")
            self.alerts_text.insert(tk.END, "• DGA (Domain Generation Algorithm) patterns\n")
        else:
            for alert in reversed(alerts):  # Most recent first
                severity = alert['severity']
                timestamp = datetime.datetime.fromtimestamp(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                message = f"[{timestamp}] [{severity}] {alert['message']}\n"
                self.alerts_text.insert(tk.END, message, severity)
                self.alerts_text.insert(tk.END, "\n")
    
    def create_charts(self):
        """Create statistics charts"""
        if not self.all_logs:
            return
        
        try:
            # Query types pie chart
            type_counter = Counter(log[3] for log in self.all_logs)
            if type_counter:
                fig = Figure(figsize=(6, 4), dpi=100)
                ax = fig.add_subplot(111)
                ax.pie(list(type_counter.values()), labels=list(type_counter.keys()),
                       autopct='%1.1f%%', startangle=90)
                ax.set_title('DNS Query Types Distribution')
                
                canvas = FigureCanvasTkAgg(fig, master=self.stats_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(pady=10, fill='both', expand=False)
            
            # Top domains bar chart
            domain_counter = Counter(log[2] for log in self.all_logs)
            top_domains = domain_counter.most_common(10)
            if top_domains:
                domains, counts = zip(*top_domains)
                # Truncate long domains
                domains = [d[:30] + '...' if len(d) > 30 else d for d in domains]
                
                fig = Figure(figsize=(8, 5), dpi=100)
                ax = fig.add_subplot(111)
                ax.barh(domains, counts, color='skyblue')
                ax.set_title('Top 10 Requested Domains')
                ax.set_xlabel('Request Count')
                ax.invert_yaxis()
                fig.tight_layout()
                
                canvas = FigureCanvasTkAgg(fig, master=self.stats_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(pady=10, fill='both', expand=False)
        except Exception as e:
            print(f"Error creating charts: {e}")
    
    def update_blocklist_display(self, blocked_filter='', allowed_filter=''):
        """Update blocklist display with optional filtering"""
        blocked, allowed = self.blocklist.get_lists()
        
        # Update blocked list
        self.blocked_listbox.delete(0, tk.END)
        filtered_blocked = [d for d in sorted(blocked) if blocked_filter.lower() in d.lower()]
        for domain in filtered_blocked:
            self.blocked_listbox.insert(tk.END, domain)
        self.blocked_count_label.config(text=f"Count: {len(blocked)} (showing: {len(filtered_blocked)})")
        
        # Update allowed list
        self.allowed_listbox.delete(0, tk.END)
        filtered_allowed = [d for d in sorted(allowed) if allowed_filter.lower() in d.lower()]
        for domain in filtered_allowed:
            self.allowed_listbox.insert(tk.END, domain)
        self.allowed_count_label.config(text=f"Count: {len(allowed)} (showing: {len(filtered_allowed)})")
    
    def add_blocked_domain(self):
        """Add domain to blocklist"""
        domain = simpledialog.askstring("Add Blocked Domain", 
                                       "Enter domain to block (e.g., ads.example.com):")
        if domain:
            domain = domain.strip().lower()
            self.blocklist.add_blocked(domain)
            self.update_blocklist_display()
            messagebox.showinfo("Domain Blocked", 
                               f"Domain '{domain}' and all its subdomains are now blocked.")
    
    def add_allowed_domain(self):
        """Add domain to allowlist"""
        domain = simpledialog.askstring("Add Allowed Domain", 
                                       "Enter domain to allow (overrides blocklist):")
        if domain:
            domain = domain.strip().lower()
            self.blocklist.add_allowed(domain)
            self.update_blocklist_display()
            messagebox.showinfo("Domain Allowed", 
                               f"Domain '{domain}' is now whitelisted (will not be blocked).")
    
    def remove_blocked(self):
        """Remove domain from blocklist"""
        selection = self.blocked_listbox.curselection()
        if selection:
            domain = self.blocked_listbox.get(selection[0])
            self.blocklist.remove_blocked(domain)
            self.update_blocklist_display()
    
    def remove_allowed(self):
        """Remove domain from allowlist"""
        selection = self.allowed_listbox.curselection()
        if selection:
            domain = self.allowed_listbox.get(selection[0])
            self.blocklist.remove_allowed(domain)
            self.update_blocklist_display()
    
    def load_default_blocklist(self):
        """Load default ad/tracker blocklist"""
        self.blocklist.load_default_blocklist()
        self.update_blocklist_display()
        blocked, _ = self.blocklist.get_lists()
        messagebox.showinfo("Default Blocklist Loaded", 
                           f"Loaded default blocklist with {len(blocked)} domains.\n\n"
                           "This includes common ad networks and trackers.")
    
    def display_alert(self, alert):
        """Display security alert"""
        timestamp = datetime.datetime.fromtimestamp(alert['timestamp']).strftime('%H:%M:%S')
        severity = alert['severity']
        message = f"[{timestamp}] [{severity}] {alert['message']}\n"
        
        self.alerts_text.insert(tk.END, message, severity)
        self.alerts_text.see(tk.END)
    
    def clear_alerts(self):
        """Clear all alerts"""
        if messagebox.askyesno("Clear Alerts", "Clear all security alerts?"):
            self.alerts_text.delete(1.0, tk.END)
            self.anomaly_detector.alerts.clear()
    
    def apply_filter(self):
        """Apply log filters"""
        self.filter_text = self.filter_entry.get()
        self.filter_type = self.type_filter.get()
    
    def clear_filter(self):
        """Clear all filters"""
        self.filter_entry.delete(0, tk.END)
        self.type_filter.set('All')
        self.filter_text = ""
        self.filter_type = "All"
    
    def export_logs(self):
        """Export logs to CSV"""
        if not self.all_logs:
            messagebox.showinfo("No Data", "No logs to export yet.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"dns_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Timestamp', 'Source IP', 'Query Domain', 
                                   'Type', 'Details', 'Success', 'Blocked', 'Cached'])
                    writer.writerows(self.all_logs)
                messagebox.showinfo("Success", f"Exported {len(self.all_logs)} logs to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def export_statistics(self):
        """Export statistics to text file"""
        from stats import export_stats_to_file
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"dns_stats_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            if export_stats_to_file(self.all_logs, filename):
                messagebox.showinfo("Success", f"Statistics exported to:\n{filename}")
            else:
                messagebox.showerror("Error", "Failed to export statistics")
    
    def clear_logs(self):
        """Clear all logs"""
        if messagebox.askyesno("Confirm", "Clear all logs? This cannot be undone."):
            self.all_logs.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)
            messagebox.showinfo("Logs Cleared", "All logs have been cleared.")
    
    def clear_cache(self):
        """Clear DNS cache"""
        if messagebox.askyesno("Confirm", "Clear DNS cache?"):
            self.dns_cache.clear()
            messagebox.showinfo("Success", "DNS cache cleared successfully.")
    
    def show_cache_stats(self):
        """Show cache statistics"""
        stats = self.dns_cache.get_stats()
        cache_status = "Enabled" if self.cache_enabled else "Disabled"
        
        msg = f"""DNS Cache Statistics:

Status: {cache_status}
Cache Size: {stats['size']:,} entries (max: {stats['max_size']:,})
Cache Hits: {stats['hits']:,}
Cache Misses: {stats['misses']:,}
Hit Rate: {stats['hit_rate']:.1f}%

Performance Impact:
• A higher hit rate means better performance
• Cached queries are ~95% faster (2ms vs 45ms)
• Current hit rate is {'EXCELLENT' if stats['hit_rate'] > 60 else 'GOOD' if stats['hit_rate'] > 40 else 'MODERATE'}"""
        
        messagebox.showinfo("Cache Statistics", msg)
    
    def toggle_pause(self):
        """Toggle logging pause"""
        self.paused = not self.paused
        status = "PAUSED" if self.paused else "RESUMED"
        messagebox.showinfo("Logging Status", f"Logging {status}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """NetGuard DNS Monitor v2.1

1st Year Python Programming Project
Introduction to Programming Module

Institution: Softwarica College of IT & E-Commerce
Affiliation: Coventry University, UK
Author: Jhapendra Kandel

Features:
• Real-time DNS query monitoring
• Advanced DNS caching (enable/disable)
• Strict domain/subdomain blocking
• GitHub blocklist support
• Anomaly detection & security alerts
• Traffic analysis & statistics
• CSV/TXT export capabilities

New in v2.1:
✓ AJAX-style updates (no auto-scroll)
✓ Cache enable/disable toggle
✓ Strict NXDOMAIN blocking
✓ GitHub blocklist import
✓ Enhanced statistics
✓ Better performance

This tool helps monitor network activity,
block unwanted domains, and detect potential
security threats in real-time."""
        
        messagebox.showinfo("About NetGuard DNS Monitor", about_text)
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()


def create_gui(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector):
    """Create and run the GUI"""
    app = DNSMonitorGUI(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector)
    app.run()