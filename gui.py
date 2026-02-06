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
import os
import json
from stats import compute_stats
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter

CONFIG_FILE = 'netguard_config.json'


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
        self.stats_scroll_position = 0
        
        # Load saved configuration (must be before creating widgets)
        self.load_config()
        
        # Apply loaded cache state to dns_cache
        self.dns_cache.enabled = self.cache_enabled
        
        # Dark theme colors
        self.bg_color = '#0d0d0d'
        self.bg_secondary = '#1a1a1a'
        self.bg_tertiary = '#252525'
        self.fg_color = '#ffffff'
        self.fg_secondary = '#b0b0b0'
        self.accent_color = '#00d4aa'
        self.accent_secondary = '#0099cc'
        self.success_color = '#00ff88'
        self.error_color = '#ff4757'
        self.warning_color = '#ffa502'
        self.info_color = '#3498db'
        self.border_color = '#333333'
        
        self.root = tk.Tk()
        self.root.title("🛡️ NetGuard DNS Monitor v2.2")
        self.root.geometry("1200x900")
        self.root.minsize(1000, 700)
        
        # Apply dark theme
        self.apply_theme()
        
        # Create main container
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill='both', expand=True)
        
        # Header
        self.create_header()
        
        self.create_menu()
        
        # Control bar
        self.create_control_bar()
        
        # Notebook
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=(5, 10))
        
        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        self.create_logs_tab()
        self.create_stats_tab()
        self.create_blocklist_tab()
        self.create_alerts_tab()
        
        # Status bar
        self.create_status_bar()
        
        self.update_gui()
    
    def load_config(self):
        """Load saved configuration from JSON file"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.cache_enabled = config.get('cache_enabled', True)
            else:
                self.cache_enabled = True
        except:
            self.cache_enabled = True
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({'cache_enabled': self.cache_enabled}, f)
        except:
            pass
    
    def apply_theme(self):
        """Apply comprehensive dark theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure all ttk widgets
        style.configure('.', background=self.bg_color, foreground=self.fg_color)
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.fg_color, font=('Segoe UI', 10))
        
        # LabelFrame
        style.configure('TLabelframe', background=self.bg_color, foreground=self.fg_color, 
                       bordercolor=self.border_color, relief='solid')
        style.configure('TLabelframe.Label', background=self.bg_color, foreground=self.accent_color, 
                       font=('Segoe UI', 10, 'bold'))
        
        # Notebook
        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.bg_tertiary, foreground=self.fg_secondary, 
                       padding=[15, 8], font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab', 
                 background=[('selected', self.accent_color), ('active', self.bg_secondary)],
                 foreground=[('selected', self.bg_color), ('active', self.fg_color)])
        
        # Buttons
        style.configure('TButton', background=self.accent_color, foreground=self.bg_color, 
                       font=('Segoe UI', 9, 'bold'), padding=[12, 6], borderwidth=0)
        style.map('TButton', 
                 background=[('active', self.accent_secondary), ('pressed', '#007766')],
                 foreground=[('active', self.fg_color)])
        
        # Accent Button
        style.configure('Accent.TButton', background=self.accent_color, foreground=self.bg_color)
        
        # Danger Button
        style.configure('Danger.TButton', background=self.error_color, foreground=self.fg_color)
        style.map('Danger.TButton', background=[('active', '#cc3344')])
        
        # Entry
        style.configure('TEntry', fieldbackground=self.bg_tertiary, foreground=self.fg_color,
                       insertcolor=self.fg_color, bordercolor=self.border_color, padding=5)
        
        # Combobox
        style.configure('TCombobox', fieldbackground=self.bg_tertiary, foreground=self.fg_color,
                       background=self.bg_tertiary, arrowcolor=self.fg_color)
        style.map('TCombobox', fieldbackground=[('readonly', self.bg_tertiary)])
        
        # Treeview
        style.configure('Treeview', background=self.bg_secondary, foreground=self.fg_color,
                       fieldbackground=self.bg_secondary, borderwidth=0, font=('Consolas', 9))
        style.configure('Treeview.Heading', background=self.bg_tertiary, foreground=self.accent_color,
                       font=('Segoe UI', 9, 'bold'), borderwidth=0)
        style.map('Treeview', background=[('selected', self.accent_color)],
                 foreground=[('selected', self.bg_color)])
        
        # Scrollbar
        style.configure('Vertical.TScrollbar', background=self.bg_tertiary, 
                       troughcolor=self.bg_secondary, borderwidth=0, arrowcolor=self.fg_color)
        style.map('Vertical.TScrollbar', background=[('active', self.accent_color)])
        
        # Progressbar
        style.configure('TProgressbar', background=self.accent_color, troughcolor=self.bg_tertiary)
        
        # Separator
        style.configure('TSeparator', background=self.border_color)
        
        self.root.configure(bg=self.bg_color)
    
    def create_header(self):
        """Create application header"""
        header_frame = tk.Frame(self.main_container, bg=self.bg_secondary, height=60)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Logo and title
        title_frame = tk.Frame(header_frame, bg=self.bg_secondary)
        title_frame.pack(side='left', padx=20, pady=10)
        
        title_label = tk.Label(title_frame, text="🛡️ NetGuard", font=('Segoe UI', 18, 'bold'),
                              bg=self.bg_secondary, fg=self.accent_color)
        title_label.pack(side='left')
        
        subtitle_label = tk.Label(title_frame, text="DNS Monitor v2.2", font=('Segoe UI', 12),
                                 bg=self.bg_secondary, fg=self.fg_secondary)
        subtitle_label.pack(side='left', padx=(10, 0))
        
        # Right side info
        info_frame = tk.Frame(header_frame, bg=self.bg_secondary)
        info_frame.pack(side='right', padx=20, pady=10)
        
        self.time_label = tk.Label(info_frame, text="", font=('Consolas', 10),
                                   bg=self.bg_secondary, fg=self.fg_secondary)
        self.time_label.pack(side='right')
        
        self.update_time()
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"⏰ {current_time}")
        self.root.after(1000, self.update_time)
    
    def create_control_bar(self):
        """Create control bar with cache toggle and other controls"""
        control_frame = tk.Frame(self.main_container, bg=self.bg_color)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Cache control
        cache_frame = tk.LabelFrame(control_frame, text="⚡ Cache Control", 
                                    bg=self.bg_secondary, fg=self.accent_color,
                                    font=('Segoe UI', 9, 'bold'), bd=1, relief='solid')
        cache_frame.pack(side='left', padx=5, pady=5, ipadx=10, ipady=5)
        
        cache_inner = tk.Frame(cache_frame, bg=self.bg_secondary)
        cache_inner.pack(padx=10, pady=5)
        
        if self.cache_enabled:
            status_text = "● ENABLED"
            status_color = self.success_color
            btn_text = "Disable"
        else:
            status_text = "● DISABLED"
            status_color = self.error_color
            btn_text = "Enable"
        
        self.cache_status_label = tk.Label(cache_inner, text=status_text, 
                                           fg=status_color, bg=self.bg_secondary,
                                           font=('Segoe UI', 10, 'bold'))
        self.cache_status_label.pack(side='left', padx=5)
        
        self.cache_toggle_btn = ttk.Button(cache_inner, text=btn_text, 
                                           command=self.toggle_cache, width=8)
        self.cache_toggle_btn.pack(side='left', padx=5)
        
        # Quick stats
        stats_frame = tk.LabelFrame(control_frame, text="📊 Quick Stats", 
                                    bg=self.bg_secondary, fg=self.accent_color,
                                    font=('Segoe UI', 9, 'bold'), bd=1, relief='solid')
        stats_frame.pack(side='left', padx=5, pady=5, ipadx=10, ipady=5)
        
        stats_inner = tk.Frame(stats_frame, bg=self.bg_secondary)
        stats_inner.pack(padx=10, pady=5)
        
        self.stat_queries = tk.Label(stats_inner, text="Queries: 0", 
                                     fg=self.fg_color, bg=self.bg_secondary,
                                     font=('Consolas', 10))
        self.stat_queries.pack(side='left', padx=8)
        
        tk.Label(stats_inner, text="|", fg=self.border_color, bg=self.bg_secondary).pack(side='left')
        
        self.stat_blocked = tk.Label(stats_inner, text="Blocked: 0", 
                                     fg=self.warning_color, bg=self.bg_secondary,
                                     font=('Consolas', 10))
        self.stat_blocked.pack(side='left', padx=8)
        
        tk.Label(stats_inner, text="|", fg=self.border_color, bg=self.bg_secondary).pack(side='left')
        
        self.stat_cached = tk.Label(stats_inner, text="Cached: 0", 
                                    fg=self.info_color, bg=self.bg_secondary,
                                    font=('Consolas', 10))
        self.stat_cached.pack(side='left', padx=8)
        
        # Network status
        network_frame = tk.LabelFrame(control_frame, text="🌐 Network Status", 
                                      bg=self.bg_secondary, fg=self.accent_color,
                                      font=('Segoe UI', 9, 'bold'), bd=1, relief='solid')
        network_frame.pack(side='left', padx=5, pady=5, ipadx=10, ipady=5)
        
        network_inner = tk.Frame(network_frame, bg=self.bg_secondary)
        network_inner.pack(padx=10, pady=5)
        
        self.network_status_label = tk.Label(network_inner, text="● Active", 
                                             fg=self.success_color, bg=self.bg_secondary,
                                             font=('Segoe UI', 10, 'bold'))
        self.network_status_label.pack(side='left', padx=5)
        
    def toggle_cache(self):
        """Toggle DNS caching on/off"""
        self.cache_enabled = not self.cache_enabled
        self.dns_cache.enabled = self.cache_enabled
        self.save_config()
        
        if self.cache_enabled:
            self.cache_status_label.config(text="● ENABLED", fg=self.success_color)
            self.cache_toggle_btn.config(text="Disable")
            messagebox.showinfo("Cache Enabled", 
                              "DNS caching is now ENABLED.\n\n"
                              "Queries will be cached for faster responses.")
        else:
            self.cache_status_label.config(text="● DISABLED", fg=self.error_color)
            self.cache_toggle_btn.config(text="Enable")
            self.dns_cache.clear()
            messagebox.showinfo("Cache Disabled", 
                              "DNS caching is now DISABLED.\n\n"
                              "All queries will go directly to upstream DNS.\n"
                              "Existing cache has been cleared.")
        
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root, bg=self.bg_secondary, fg=self.fg_color,
                         activebackground=self.accent_color, activeforeground=self.bg_color,
                         font=('Segoe UI', 9))
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_secondary, fg=self.fg_color,
                           activebackground=self.accent_color, activeforeground=self.bg_color)
        menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(label="📤 Export Logs (CSV)", command=self.export_logs)
        file_menu.add_command(label="📊 Export Statistics", command=self.export_statistics)
        file_menu.add_command(label="🗑️ Clear Logs", command=self.clear_logs)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Exit", command=self.on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_secondary, fg=self.fg_color,
                           activebackground=self.accent_color, activeforeground=self.bg_color)
        menubar.add_cascade(label="👁️ View", menu=view_menu)
        view_menu.add_command(label="⏸️ Pause/Resume Logging", command=self.toggle_pause)
        view_menu.add_command(label="🔄 Refresh Statistics", command=self.force_refresh_stats)
        
        # Cache menu
        cache_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_secondary, fg=self.fg_color,
                            activebackground=self.accent_color, activeforeground=self.bg_color)
        menubar.add_cascade(label="⚡ Cache", menu=cache_menu)
        cache_menu.add_command(label="🔀 Toggle Cache", command=self.toggle_cache)
        cache_menu.add_command(label="🗑️ Clear Cache", command=self.clear_cache)
        cache_menu.add_command(label="📊 Cache Statistics", command=self.show_cache_stats)
        
        # Blocklist menu
        blocklist_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_secondary, fg=self.fg_color,
                                activebackground=self.accent_color, activeforeground=self.bg_color)
        menubar.add_cascade(label="🚫 Blocklist", menu=blocklist_menu)
        blocklist_menu.add_command(label="📁 Import from File", command=self.import_blocklist_file)
        blocklist_menu.add_command(label="🌐 Import from GitHub", command=self.import_github_blocklist)
        blocklist_menu.add_command(label="📥 Load Default Blocklist", command=self.load_default_blocklist)
        blocklist_menu.add_command(label="⚡ Load Preinstalled (64K)", command=self.load_preinstalled_blocklist)
        blocklist_menu.add_separator()
        blocklist_menu.add_command(label="💾 Export Blocklist", command=self.export_blocklist)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_secondary, fg=self.fg_color,
                           activebackground=self.accent_color, activeforeground=self.bg_color)
        menubar.add_cascade(label="❓ Help", menu=help_menu)
        help_menu.add_command(label="ℹ️ About", command=self.show_about)
        help_menu.add_command(label="📚 GitHub Blocklists Help", command=self.show_github_help)
        
    def create_logs_tab(self):
        """Create logs tab with dark theme"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text='  📋 Live Logs  ')
        
        # Filter frame
        filter_frame = tk.Frame(logs_frame, bg=self.bg_color)
        filter_frame.pack(fill='x', padx=10, pady=10)
        
        # Filter container
        filter_container = tk.Frame(filter_frame, bg=self.bg_secondary, bd=1, relief='solid')
        filter_container.pack(fill='x')
        
        filter_inner = tk.Frame(filter_container, bg=self.bg_secondary)
        filter_inner.pack(fill='x', padx=15, pady=10)
        
        tk.Label(filter_inner, text="🔍 Filter:", bg=self.bg_secondary, fg=self.fg_color,
                font=('Segoe UI', 10)).pack(side='left', padx=(0, 5))
        
        self.filter_entry = tk.Entry(filter_inner, width=35, bg=self.bg_tertiary, fg=self.fg_color,
                                     insertbackground=self.fg_color, font=('Consolas', 10),
                                     relief='flat', bd=5)
        self.filter_entry.pack(side='left', padx=5)
        self.filter_entry.bind('<KeyRelease>', self.apply_filter)
        
        tk.Label(filter_inner, text="Type:", bg=self.bg_secondary, fg=self.fg_color,
                font=('Segoe UI', 10)).pack(side='left', padx=(20, 5))
        
        self.type_filter = ttk.Combobox(filter_inner, width=10, 
                                        values=['All', 'A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'PTR'],
                                        state='readonly', font=('Consolas', 10))
        self.type_filter.set('All')
        self.type_filter.pack(side='left', padx=5)
        self.type_filter.bind('<<ComboboxSelected>>', self.apply_filter)
        
        ttk.Button(filter_inner, text="Clear Filter", 
                  command=self.clear_filter).pack(side='left', padx=15)
        
        # Tree frame
        tree_frame = tk.Frame(logs_frame, bg=self.bg_color)
        tree_frame.pack(expand=True, fill='both', padx=10, pady=(0, 10))
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical')
        y_scrollbar.pack(side='right', fill='y')
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal')
        x_scrollbar.pack(side='bottom', fill='x')
        
        self.tree = ttk.Treeview(tree_frame, 
                                 columns=('Timestamp', 'Source IP', 'Query Domain', 
                                         'Type', 'Details', 'Status'),
                                 show='headings',
                                 yscrollcommand=y_scrollbar.set,
                                 xscrollcommand=x_scrollbar.set)
        
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        # Configure columns
        columns = [
            ('Timestamp', 160, 'center'),
            ('Source IP', 120, 'center'),
            ('Query Domain', 320, 'w'),
            ('Type', 70, 'center'),
            ('Details', 220, 'w'),
            ('Status', 100, 'center')
        ]
        
        for col, width, anchor in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)
        
        self.tree.pack(expand=True, fill='both')
        
        # Configure tags with theme colors
        self.tree.tag_configure('success', foreground=self.success_color)
        self.tree.tag_configure('failed', foreground=self.error_color)
        self.tree.tag_configure('blocked', foreground=self.warning_color)
        self.tree.tag_configure('cached', foreground=self.info_color)
        
    def create_stats_tab(self):
        """Create statistics tab with dark theme"""
        stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(stats_tab, text='  📊 Statistics  ')
        
        # Top bar
        top_bar = tk.Frame(stats_tab, bg=self.bg_secondary)
        top_bar.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(top_bar, text="🔄 Refresh Statistics", 
                  command=self.silent_refresh_stats).pack(side='left', padx=10, pady=5)
        
        tk.Label(top_bar, text="Auto-refresh: Every 10s when tab active", 
                font=('Segoe UI', 9, 'italic'), bg=self.bg_secondary, 
                fg=self.fg_secondary).pack(side='left', padx=10, pady=5)
        
        # Scrollable canvas
        canvas_frame = tk.Frame(stats_tab, bg=self.bg_color)
        canvas_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        canvas = tk.Canvas(canvas_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        self.stats_frame = tk.Frame(canvas, bg=self.bg_color)
        
        self.stats_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        self.stats_canvas_window = canvas.create_window((0, 0), window=self.stats_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.stats_canvas = canvas
        self.stats_scrollbar = scrollbar
        
        # Mousewheel scrolling
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
        
        # Initial loading message
        loading_frame = tk.Frame(self.stats_frame, bg=self.bg_color)
        loading_frame.pack(fill='both', expand=True, pady=50)
        
        tk.Label(loading_frame, text="📊", font=("Segoe UI", 48), 
                bg=self.bg_color, fg=self.accent_color).pack()
        tk.Label(loading_frame, text="Loading Statistics...", 
                font=("Segoe UI", 14), bg=self.bg_color, fg=self.fg_color).pack(pady=10)
    
    def on_tab_changed(self, event):
        """Handle tab change"""
        selected_tab = self.notebook.index(self.notebook.select())
        if selected_tab == 1:
            self.silent_refresh_stats()
    
    def update_stats_display(self):
        """Update statistics display"""
        if not self.all_logs:
            return
        
        saved_position = self.stats_scroll_position
        
        # Clear old widgets
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Stats header
        header_frame = tk.Frame(self.stats_frame, bg=self.bg_secondary)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(header_frame, text="📈 DNS Query Statistics", font=('Segoe UI', 16, 'bold'),
                bg=self.bg_secondary, fg=self.accent_color).pack(pady=10)
        
        # Compute stats
        stats_text = compute_stats(self.all_logs)
        
        # Stats text display
        text_frame = tk.Frame(self.stats_frame, bg=self.bg_secondary, bd=1, relief='solid')
        text_frame.pack(fill='x', padx=5, pady=5)
        
        stats_display = tk.Text(text_frame, wrap='word', height=25, 
                               font=('Consolas', 10), bg=self.bg_secondary, fg=self.fg_color,
                               relief='flat', borderwidth=15, insertbackground=self.fg_color)
        stats_display.insert('1.0', stats_text)
        stats_display.config(state='disabled')
        stats_display.pack(fill='both', expand=True)
        
        # Charts
        self.create_charts()
        
        # Restore scroll
        self.root.after(100, lambda: self.stats_canvas.yview_moveto(saved_position))
    
    def silent_refresh_stats(self):
        """Refresh without popup"""
        self.update_stats_display()
    
    def force_refresh_stats(self):
        """Force refresh with confirmation"""
        self.update_stats_display()
        messagebox.showinfo("Statistics Refreshed", 
                           "Statistics have been updated with latest data.")
    
    def create_charts(self):
        """Create charts with dark theme"""
        if not self.all_logs:
            return
        
        try:
            # Chart container
            charts_frame = tk.Frame(self.stats_frame, bg=self.bg_color)
            charts_frame.pack(fill='x', padx=5, pady=10)
            
            # Pie chart - Query Types
            type_counter = Counter(log[3] for log in self.all_logs)
            if type_counter:
                pie_frame = tk.Frame(charts_frame, bg=self.bg_secondary, bd=1, relief='solid')
                pie_frame.pack(fill='x', pady=5)
                
                fig = Figure(figsize=(7, 5), dpi=100, facecolor=self.bg_secondary)
                ax = fig.add_subplot(111)
                ax.set_facecolor(self.bg_secondary)
                
                colors = ['#00d4aa', '#0099cc', '#ff6b6b', '#ffd93d', '#6bcb77', '#4d96ff', '#ff8fab']
                wedges, texts, autotexts = ax.pie(
                    list(type_counter.values()), 
                    labels=list(type_counter.keys()),
                    autopct='%1.1f%%', 
                    startangle=90,
                    colors=colors[:len(type_counter)],
                    textprops={'color': self.fg_color, 'fontsize': 10},
                    wedgeprops={'edgecolor': self.bg_secondary, 'linewidth': 2}
                )
                
                for autotext in autotexts:
                    autotext.set_color(self.bg_color)
                    autotext.set_fontweight('bold')
                
                ax.set_title('DNS Query Types Distribution', color=self.fg_color, 
                           fontsize=14, fontweight='bold', pad=20)
                
                fig.tight_layout()
                
                canvas = FigureCanvasTkAgg(fig, master=pie_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(pady=10)
            
            # Bar chart - Top Domains
            domain_counter = Counter(log[2] for log in self.all_logs)
            top_domains = domain_counter.most_common(10)
            if top_domains:
                bar_frame = tk.Frame(charts_frame, bg=self.bg_secondary, bd=1, relief='solid')
                bar_frame.pack(fill='x', pady=5)
                
                domains, counts = zip(*top_domains)
                domains = [d[:35] + '...' if len(d) > 35 else d for d in domains]
                
                fig = Figure(figsize=(9, 6), dpi=100, facecolor=self.bg_secondary)
                ax = fig.add_subplot(111)
                ax.set_facecolor(self.bg_secondary)
                
                bars = ax.barh(domains, counts, color=self.accent_color, edgecolor=self.bg_secondary)
                
                # Add value labels
                for bar, count in zip(bars, counts):
                    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                           f'{count}', va='center', color=self.fg_color, fontsize=9)
                
                ax.set_title('Top 10 Requested Domains', color=self.fg_color, 
                           fontsize=14, fontweight='bold', pad=20)
                ax.set_xlabel('Request Count', color=self.fg_color, fontsize=11)
                
                ax.tick_params(axis='x', colors=self.fg_color)
                ax.tick_params(axis='y', colors=self.fg_color)
                
                for spine in ax.spines.values():
                    spine.set_color(self.border_color)
                
                ax.invert_yaxis()
                fig.tight_layout()
                
                canvas = FigureCanvasTkAgg(fig, master=bar_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(pady=10)
                
        except Exception as e:
            print(f"Error creating charts: {e}")
    
    def create_blocklist_tab(self):
        """Create blocklist tab with dark theme"""
        blocklist_frame = ttk.Frame(self.notebook)
        self.notebook.add(blocklist_frame, text='  🚫 Blocklist  ')
        
        # Button bar
        btn_frame = tk.Frame(blocklist_frame, bg=self.bg_secondary)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        btn_inner = tk.Frame(btn_frame, bg=self.bg_secondary)
        btn_inner.pack(pady=8)
        
        ttk.Button(btn_inner, text="➕ Block Domain", 
                  command=self.add_blocked_domain).pack(side='left', padx=5)
        ttk.Button(btn_inner, text="✅ Allow Domain", 
                  command=self.add_allowed_domain).pack(side='left', padx=5)
        ttk.Button(btn_inner, text="📁 Import File", 
                  command=self.import_blocklist_file).pack(side='left', padx=5)
        ttk.Button(btn_inner, text="🌐 Import GitHub", 
                  command=self.import_github_blocklist).pack(side='left', padx=5)
        ttk.Button(btn_inner, text="⚡ Load Preinstalled (64K – Recommended)", 
                  command=self.load_preinstalled_blocklist).pack(side='left', padx=5)
        ttk.Button(btn_inner, text="📥 Load Defaults", 
                  command=self.load_default_blocklist).pack(side='left', padx=5)
        ttk.Button(btn_inner, text="💾 Export", 
                  command=self.export_blocklist).pack(side='left', padx=5)
        
        # Lists container
        lists_frame = tk.Frame(blocklist_frame, bg=self.bg_color)
        lists_frame.pack(expand=True, fill='both', padx=10, pady=(0, 10))
        
        # Blocked list
        blocked_container = tk.LabelFrame(lists_frame, text="🚫 Blocked Domains", 
                                          bg=self.bg_secondary, fg=self.error_color,
                                          font=('Segoe UI', 10, 'bold'))
        blocked_container.pack(side='left', expand=True, fill='both', padx=(0, 5))
        
        # Search
        search_frame = tk.Frame(blocked_container, bg=self.bg_secondary)
        search_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(search_frame, text="🔍", bg=self.bg_secondary, fg=self.fg_color).pack(side='left')
        self.blocked_search = tk.Entry(search_frame, bg=self.bg_tertiary, fg=self.fg_color,
                                       insertbackground=self.fg_color, relief='flat', bd=5)
        self.blocked_search.pack(side='left', fill='x', expand=True, padx=5)
        self.blocked_search.bind('<KeyRelease>', lambda e: self.filter_blocked_list())
        
        # Listbox
        list_frame = tk.Frame(blocked_container, bg=self.bg_secondary)
        list_frame.pack(expand=True, fill='both', padx=10, pady=(0, 5))
        
        blocked_scroll = ttk.Scrollbar(list_frame)
        blocked_scroll.pack(side='right', fill='y')
        
        self.blocked_listbox = tk.Listbox(list_frame, bg=self.bg_tertiary, fg=self.fg_color,
                                          selectbackground=self.accent_color,
                                          selectforeground=self.bg_color,
                                          font=('Consolas', 9), relief='flat',
                                          yscrollcommand=blocked_scroll.set)
        self.blocked_listbox.pack(expand=True, fill='both')
        blocked_scroll.config(command=self.blocked_listbox.yview)
        
        # Count and remove
        bottom_frame = tk.Frame(blocked_container, bg=self.bg_secondary)
        bottom_frame.pack(fill='x', padx=10, pady=10)
        
        self.blocked_count_label = tk.Label(bottom_frame, text="Count: 0",
                                            bg=self.bg_secondary, fg=self.fg_color,
                                            font=('Segoe UI', 9, 'bold'))
        self.blocked_count_label.pack(side='left')
        
        ttk.Button(bottom_frame, text="Remove Selected", 
                  command=self.remove_blocked).pack(side='right')
        
        # Allowed list
        allowed_container = tk.LabelFrame(lists_frame, text="✅ Allowed Domains (Whitelist)", 
                                          bg=self.bg_secondary, fg=self.success_color,
                                          font=('Segoe UI', 10, 'bold'))
        allowed_container.pack(side='left', expand=True, fill='both', padx=(5, 0))
        
        # Search
        search_frame2 = tk.Frame(allowed_container, bg=self.bg_secondary)
        search_frame2.pack(fill='x', padx=10, pady=10)
        
        tk.Label(search_frame2, text="🔍", bg=self.bg_secondary, fg=self.fg_color).pack(side='left')
        self.allowed_search = tk.Entry(search_frame2, bg=self.bg_tertiary, fg=self.fg_color,
                                       insertbackground=self.fg_color, relief='flat', bd=5)
        self.allowed_search.pack(side='left', fill='x', expand=True, padx=5)
        self.allowed_search.bind('<KeyRelease>', lambda e: self.filter_allowed_list())
        
        # Listbox
        list_frame2 = tk.Frame(allowed_container, bg=self.bg_secondary)
        list_frame2.pack(expand=True, fill='both', padx=10, pady=(0, 5))
        
        allowed_scroll = ttk.Scrollbar(list_frame2)
        allowed_scroll.pack(side='right', fill='y')
        
        self.allowed_listbox = tk.Listbox(list_frame2, bg=self.bg_tertiary, fg=self.fg_color,
                                          selectbackground=self.accent_color,
                                          selectforeground=self.bg_color,
                                          font=('Consolas', 9), relief='flat',
                                          yscrollcommand=allowed_scroll.set)
        self.allowed_listbox.pack(expand=True, fill='both')
        allowed_scroll.config(command=self.allowed_listbox.yview)
        
        # Count and remove
        bottom_frame2 = tk.Frame(allowed_container, bg=self.bg_secondary)
        bottom_frame2.pack(fill='x', padx=10, pady=10)
        
        self.allowed_count_label = tk.Label(bottom_frame2, text="Count: 0",
                                            bg=self.bg_secondary, fg=self.fg_color,
                                            font=('Segoe UI', 9, 'bold'))
        self.allowed_count_label.pack(side='left')
        
        ttk.Button(bottom_frame2, text="Remove Selected", 
                  command=self.remove_allowed).pack(side='right')
        
        self.update_blocklist_display()
    
    def filter_blocked_list(self):
        """Filter blocked list"""
        search_term = self.blocked_search.get().lower()
        self.update_blocklist_display(blocked_filter=search_term)
    
    def filter_allowed_list(self):
        """Filter allowed list"""
        search_term = self.allowed_search.get().lower()
        self.update_blocklist_display(allowed_filter=search_term)
    
    def create_alerts_tab(self):
        """Create alerts tab with dark theme"""
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text='  ⚠️ Security Alerts  ')
        
        # Control bar
        ctrl_frame = tk.Frame(alerts_frame, bg=self.bg_secondary)
        ctrl_frame.pack(fill='x', padx=10, pady=10)
        
        ctrl_inner = tk.Frame(ctrl_frame, bg=self.bg_secondary)
        ctrl_inner.pack(pady=8)
        
        ttk.Button(ctrl_inner, text="🗑️ Clear All Alerts", 
                  command=self.clear_alerts).pack(side='left', padx=5)
        ttk.Button(ctrl_inner, text="🔄 Refresh", 
                  command=self.update_alerts).pack(side='left', padx=5)
        
        # Alerts display
        alerts_container = tk.Frame(alerts_frame, bg=self.bg_color)
        alerts_container.pack(expand=True, fill='both', padx=10, pady=(0, 10))
        
        alert_scroll = ttk.Scrollbar(alerts_container)
        alert_scroll.pack(side='right', fill='y')
        
        self.alerts_text = tk.Text(alerts_container, wrap='word', 
                                   font=('Consolas', 10),
                                   bg=self.bg_secondary, fg=self.fg_color,
                                   relief='flat', borderwidth=15,
                                   yscrollcommand=alert_scroll.set)
        self.alerts_text.pack(expand=True, fill='both')
        alert_scroll.config(command=self.alerts_text.yview)
        
        # Tags
        self.alerts_text.tag_configure('HIGH', foreground=self.error_color, 
                                       font=('Consolas', 10, 'bold'))
        self.alerts_text.tag_configure('MEDIUM', foreground=self.warning_color, 
                                       font=('Consolas', 10, 'bold'))
        self.alerts_text.tag_configure('LOW', foreground=self.info_color, 
                                       font=('Consolas', 10, 'bold'))
        self.alerts_text.tag_configure('header', foreground=self.accent_color,
                                       font=('Consolas', 10, 'bold'))
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = tk.Frame(self.main_container, bg=self.bg_tertiary, height=30)
        self.status_bar.pack(fill='x', side='bottom')
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, text="● DNS Monitor Running", 
                                     bg=self.bg_tertiary, fg=self.success_color,
                                     font=('Segoe UI', 9))
        self.status_label.pack(side='left', padx=15)
        
        self.status_details = tk.Label(self.status_bar, text="", 
                                       bg=self.bg_tertiary, fg=self.fg_secondary,
                                       font=('Consolas', 9))
        self.status_details.pack(side='right', padx=15)
    
    def update_logs(self):
        """Update logs with batch processing limit"""
        if self.paused:
            return
        
        batch = 0
        max_batch = 50
        while not self.log_queue.empty() and batch < max_batch:
            try:
                item = self.log_queue.get_nowait()
                batch += 1
                
                if isinstance(item, tuple) and item[0] == 'ALERT':
                    self.display_alert(item[1])
                else:
                    timestamp, ip, domain, qtype, details, success, blocked, cached = item
                    
                    if self.filter_text and self.filter_text.lower() not in domain.lower() and \
                       self.filter_text.lower() not in ip.lower():
                        continue
                    
                    if self.filter_type != "All" and qtype != self.filter_type:
                        continue
                    
                    if blocked:
                        tag, status = 'blocked', 'BLOCKED'
                    elif cached:
                        tag, status = 'cached', 'CACHED'
                    elif success:
                        tag, status = 'success', 'SUCCESS'
                    else:
                        tag, status = 'failed', 'FAILED'
                    
                    self.tree.insert('', 0, values=(timestamp, ip, domain, qtype, details, status), 
                                    tags=(tag,))
                    
                    if len(self.tree.get_children()) > 1000:
                        self.tree.delete(self.tree.get_children()[-1])
            
            except queue.Empty:
                break
            except Exception as e:
                print(f"Error updating logs: {e}")
    
    def update_gui(self):
        """Main GUI update"""
        self.update_logs()
        
        current_time = datetime.datetime.now().timestamp()
        if self.notebook.index(self.notebook.select()) == 1:
            if current_time - self.last_stats_update > 10:
                self.update_stats_display()
                self.last_stats_update = current_time
        
        if self.notebook.index(self.notebook.select()) == 3:
            self.update_alerts()
        
        # Update status
        stats = self.stats_tracker.get_stats()
        cache_stats = self.dns_cache.get_stats()
        
        cache_status = "ON" if self.cache_enabled else "OFF"
        
        if self.paused:
            self.status_label.config(text="⏸ PAUSED", fg=self.warning_color)
            self.network_status_label.config(text="● Paused", fg=self.warning_color)
        else:
            self.status_label.config(text="● Running", fg=self.success_color)
            self.network_status_label.config(text="● Active", fg=self.success_color)
        
        self.status_details.config(
            text=f"Cache: {cache_status} ({cache_stats['hit_rate']:.1f}% hit) | "
                 f"Total: {stats['total']:,} queries"
        )
        
        # Update quick stats
        self.stat_queries.config(text=f"Queries: {stats['total']:,}")
        self.stat_blocked.config(text=f"Blocked: {stats['blocked']:,}")
        self.stat_cached.config(text=f"Cached: {stats['cached']:,}")
        
        self.root.after(500, self.update_gui)
    
    def update_alerts(self):
        """Update alerts"""
        alerts = self.anomaly_detector.get_alerts()
        
        if not alerts:
            return
        
        self.alerts_text.delete(1.0, tk.END)
        
        if not alerts:
            self.alerts_text.insert(tk.END, "✅ No security alerts detected.\n\n", 'header')
            self.alerts_text.insert(tk.END, "The system is monitoring for:\n\n")
            self.alerts_text.insert(tk.END, "  • Excessive queries (DDoS indicators)\n")
            self.alerts_text.insert(tk.END, "  • Suspicious domain keywords\n")
            self.alerts_text.insert(tk.END, "  • DGA (Domain Generation Algorithm) patterns\n")
        else:
            self.alerts_text.insert(tk.END, f"⚠️ {len(alerts)} Security Alert(s)\n\n", 'header')
            for alert in reversed(alerts):
                severity = alert['severity']
                timestamp = datetime.datetime.fromtimestamp(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                self.alerts_text.insert(tk.END, f"[{timestamp}] ", 'header')
                self.alerts_text.insert(tk.END, f"[{severity}] ", severity)
                self.alerts_text.insert(tk.END, f"{alert['message']}\n\n")
    
    def update_blocklist_display(self, blocked_filter='', allowed_filter=''):
        """Update blocklist display"""
        blocked, allowed = self.blocklist.get_lists()
        
        self.blocked_listbox.delete(0, tk.END)
        filtered_blocked = [d for d in sorted(blocked) if blocked_filter.lower() in d.lower()]
        for domain in filtered_blocked:
            self.blocked_listbox.insert(tk.END, domain)
        self.blocked_count_label.config(text=f"Count: {len(blocked):,} (showing: {len(filtered_blocked):,})")
        
        self.allowed_listbox.delete(0, tk.END)
        filtered_allowed = [d for d in sorted(allowed) if allowed_filter.lower() in d.lower()]
        for domain in filtered_allowed:
            self.allowed_listbox.insert(tk.END, domain)
        self.allowed_count_label.config(text=f"Count: {len(allowed):,} (showing: {len(filtered_allowed):,})")
    
    def load_preinstalled_blocklist(self):
        """Load preinstalled blocklist from local JSON file (fast local load)"""
        messagebox.showinfo("Loading", "Loading preinstalled blocklist...")
        
        try:
            with open('preinstalled-blocklist.json', 'r') as f:
                domains = json.load(f)
            
            for domain in domains:
                self.blocklist.add_blocked(domain)
            
            self.update_blocklist_display()
            messagebox.showinfo("Success", "Loaded 64,300 domains! Estimated ad-blocking ~72%")
        except FileNotFoundError:
            messagebox.showerror("Error", "preinstalled-blocklist.json not found in program folder.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load blocklist: {e}")
    
    def import_github_blocklist(self):
        """Import from GitHub"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Import from GitHub")
        dialog.geometry("650x450")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg=self.bg_secondary)
        header.pack(fill='x', padx=0, pady=0)
        
        tk.Label(header, text="🌐 Import Blocklist from GitHub", 
                font=('Segoe UI', 14, 'bold'), bg=self.bg_secondary, 
                fg=self.accent_color).pack(pady=15)
        
        # Content
        content = tk.Frame(dialog, bg=self.bg_color)
        content.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Label(content, text="Enter GitHub Blocklist URL:", 
                font=('Segoe UI', 10), bg=self.bg_color, fg=self.fg_color).pack(anchor='w', pady=(10, 5))
        
        url_entry = tk.Entry(content, width=70, bg=self.bg_tertiary, fg=self.fg_color,
                            insertbackground=self.fg_color, font=('Consolas', 10),
                            relief='flat', bd=8)
        url_entry.pack(fill='x', pady=5)
        url_entry.insert(0, "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts")
        
        tk.Label(content, text="Popular Blocklists:", font=('Segoe UI', 10, 'bold'),
                bg=self.bg_color, fg=self.accent_color).pack(anchor='w', pady=(15, 5))
        
        lists_text = tk.Text(content, height=10, wrap='word', bg=self.bg_secondary, 
                            fg=self.fg_color, font=('Consolas', 9), relief='flat', bd=10)
        lists_text.pack(fill='both', expand=True, pady=5)
        
        popular = """1. StevenBlack's Unified Hosts (Recommended)
   https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts
   
2. StevenBlack's + Fakenews
   https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews/hosts
   
3. AdAway Default Blocklist
   https://adaway.org/hosts.txt
   
4. Dan Pollock's Hosts
   https://someonewhocares.org/hosts/hosts"""
        
        lists_text.insert('1.0', popular)
        lists_text.config(state='disabled')
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg=self.bg_color)
        btn_frame.pack(fill='x', padx=20, pady=15)
        
        def do_import():
            url = url_entry.get().strip()
            if not url:
                messagebox.showwarning("No URL", "Please enter a URL")
                return
            
            progress = ttk.Progressbar(btn_frame, mode='indeterminate')
            progress.pack(fill='x', pady=10)
            progress.start()
            
            def import_thread():
                try:
                    count = self.blocklist.import_from_url(url)
                    progress.stop()
                    dialog.destroy()
                    self.update_blocklist_display()
                    messagebox.showinfo("Success", f"Imported {count:,} domains!")
                except Exception as e:
                    progress.stop()
                    messagebox.showerror("Error", f"Import failed:\n{str(e)}")
            
            threading.Thread(target=import_thread, daemon=True).start()
        
        ttk.Button(btn_frame, text="Import", command=do_import).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def import_blocklist_file(self):
        """Import from file"""
        filename = filedialog.askopenfilename(
            title="Select Blocklist File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            count = self.blocklist.import_from_file(filename)
            self.update_blocklist_display()
            messagebox.showinfo("Import Complete", f"Imported {count:,} domains")
    
    def export_blocklist(self):
        """Export blocklist"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"blocklist_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            blocked, _ = self.blocklist.get_lists()
            try:
                with open(filename, 'w') as f:
                    f.write("# NetGuard DNS Monitor - Blocklist Export\n")
                    f.write(f"# Generated: {datetime.datetime.now()}\n")
                    f.write(f"# Total: {len(blocked)} domains\n\n")
                    for domain in sorted(blocked):
                        f.write(f"{domain}\n")
                messagebox.showinfo("Success", f"Exported {len(blocked):,} domains")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def add_blocked_domain(self):
        """Add blocked domain"""
        domain = simpledialog.askstring("Block Domain", 
                                       "Enter domain to block (e.g., ads.example.com):",
                                       parent=self.root)
        if domain:
            domain = domain.strip().lower()
            self.blocklist.add_blocked(domain)
            self.update_blocklist_display()
            messagebox.showinfo("Blocked", f"'{domain}' is now blocked.")
    
    def add_allowed_domain(self):
        """Add allowed domain"""
        domain = simpledialog.askstring("Allow Domain", 
                                       "Enter domain to allow:",
                                       parent=self.root)
        if domain:
            domain = domain.strip().lower()
            self.blocklist.add_allowed(domain)
            self.update_blocklist_display()
            messagebox.showinfo("Allowed", f"'{domain}' is now whitelisted.")
    
    def remove_blocked(self):
        """Remove blocked"""
        selection = self.blocked_listbox.curselection()
        if selection:
            domain = self.blocked_listbox.get(selection[0])
            self.blocklist.remove_blocked(domain)
            self.update_blocklist_display()
    
    def remove_allowed(self):
        """Remove allowed"""
        selection = self.allowed_listbox.curselection()
        if selection:
            domain = self.allowed_listbox.get(selection[0])
            self.blocklist.remove_allowed(domain)
            self.update_blocklist_display()
    
    def load_default_blocklist(self):
        """Load defaults"""
        self.blocklist.load_default_blocklist()
        self.update_blocklist_display()
        blocked, _ = self.blocklist.get_lists()
        messagebox.showinfo("Loaded", f"Loaded {len(blocked):,} domains.")
    
    def display_alert(self, alert):
        """Display alert"""
        timestamp = datetime.datetime.fromtimestamp(alert['timestamp']).strftime('%H:%M:%S')
        severity = alert['severity']
        self.alerts_text.insert(tk.END, f"[{timestamp}] ", 'header')
        self.alerts_text.insert(tk.END, f"[{severity}] ", severity)
        self.alerts_text.insert(tk.END, f"{alert['message']}\n\n")
        self.alerts_text.see(tk.END)
    
    def clear_alerts(self):
        """Clear alerts"""
        if messagebox.askyesno("Clear", "Clear all alerts?"):
            self.alerts_text.delete(1.0, tk.END)
            self.anomaly_detector.alerts.clear()
    
    def apply_filter(self, event=None):
        """Apply filter"""
        self.filter_text = self.filter_entry.get().strip()
        self.filter_type = self.type_filter.get()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for log in reversed(self.all_logs[-1000:]):
            timestamp, ip, domain, qtype, details, success, blocked, cached = log
            
            if self.filter_text:
                if self.filter_text.lower() not in domain.lower() and \
                   self.filter_text.lower() not in ip.lower():
                    continue
            
            if self.filter_type != "All" and qtype != self.filter_type:
                continue
            
            if blocked:
                tag, status = 'blocked', 'BLOCKED'
            elif cached:
                tag, status = 'cached', 'CACHED'
            elif success:
                tag, status = 'success', 'SUCCESS'
            else:
                tag, status = 'failed', 'FAILED'
            
            self.tree.insert('', 0, values=(timestamp, ip, domain, qtype, details, status), tags=(tag,))
    
    def clear_filter(self):
        """Clear filter"""
        self.filter_entry.delete(0, tk.END)
        self.type_filter.set('All')
        self.filter_text = ""
        self.filter_type = "All"
        self.apply_filter()
    
    def export_logs(self):
        """Export logs"""
        if not self.all_logs:
            messagebox.showinfo("No Data", "No logs to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"dns_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Timestamp', 'Source IP', 'Domain', 'Type', 
                                   'Details', 'Success', 'Blocked', 'Cached'])
                    writer.writerows(self.all_logs)
                messagebox.showinfo("Success", f"Exported {len(self.all_logs):,} logs")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def export_statistics(self):
        """Export stats"""
        from stats import export_stats_to_file
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=f"dns_stats_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            if export_stats_to_file(self.all_logs, filename):
                messagebox.showinfo("Success", f"Statistics exported to:\n{filename}")
            else:
                messagebox.showerror("Error", "Export failed")
    
    def clear_logs(self):
        """Clear logs"""
        if messagebox.askyesno("Confirm", "Clear all logs?"):
            self.all_logs.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)
            messagebox.showinfo("Cleared", "All logs cleared.")
    
    def clear_cache(self):
        """Clear cache"""
        if messagebox.askyesno("Confirm", "Clear DNS cache?"):
            self.dns_cache.clear()
            messagebox.showinfo("Success", "DNS cache cleared.")
    
    def show_cache_stats(self):
        """Show cache stats"""
        stats = self.dns_cache.get_stats()
        cache_status = "Enabled" if self.cache_enabled else "Disabled"
        
        rating = 'EXCELLENT' if stats['hit_rate'] > 60 else 'GOOD' if stats['hit_rate'] > 40 else 'MODERATE'
        
        msg = f"""DNS Cache Statistics

Status: {cache_status}
Size: {stats['size']:,} / {stats['max_size']:,} entries
Hits: {stats['hits']:,}
Misses: {stats['misses']:,}
Hit Rate: {stats['hit_rate']:.1f}%

Performance: {rating}"""
        
        messagebox.showinfo("Cache Statistics", msg)
    
    def toggle_pause(self):
        """Toggle pause"""
        self.paused = not self.paused
        status = "PAUSED" if self.paused else "RESUMED"
        messagebox.showinfo("Status", f"Logging {status}")
    
    def show_github_help(self):
        """Show GitHub help"""
        help_text = """GitHub Blocklist Support

Popular Blocklists:

• StevenBlack's Unified Hosts
  Blocks ads, malware, and tracking
  
• AdAway Default Blocklist
  Mobile-focused ad blocking

How to Import:
1. Go to Blocklist → Import from GitHub
2. Paste the URL
3. Click Import

Benefits:
• Block thousands of ads
• Improve privacy
• Faster browsing"""
        
        messagebox.showinfo("GitHub Help", help_text)
    
    def show_about(self):
        """Show about"""
        about_text = """NetGuard DNS Monitor v2.2

Institution: Softwarica College of IT & E-Commerce
Affiliation: Coventry University, UK
Author: Jhapendra Kandel

Features:
• Real-time DNS monitoring
• Advanced caching
• Domain blocking
• GitHub blocklist support
• Anomaly detection
• Dark theme UI

1st Year Python Programming Project"""
        
        messagebox.showinfo("About", about_text)
    
    def on_closing(self):
        """Handle close"""
        self.save_config()
        self.root.destroy()
    
    def run(self):
        """Run GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


def create_gui(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector):
    """Create and run GUI"""
    app = DNSMonitorGUI(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector)
    app.run()