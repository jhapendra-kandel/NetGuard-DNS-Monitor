# NetGuard DNS Monitor - this is the gui file for our project
# basically this whole file creates the tkinter window with all the tabs and buttons
# without this file user wont see anything just terminal output which is boring
# so this file is very important for the visual part of our project

# Author: 4A 68 61 70 65 6E 64 72 61 20 6B 61 6E 64 65 6C
# Project: 1st Year Python Programming
# Institution: Softwarica College of IT & E-Commerce (Coventry University)

VERSION = "2.3.0"

# tkinter is the gui library that comes with python no need to install separately
import tkinter as tk
# ttk gives us better looking widgets than normal tkinter ones
from tkinter import ttk, messagebox, filedialog, simpledialog, scrolledtext
# queue for getting log data from dns server thread safely
import queue
# csv module for exporting logs to csv file
import csv
import datetime
import threading
# requests is for downloading blocklist from github urls
import requests
import os
import json
# importing our stats computing function from stats.py file
from stats import compute_stats
# matplotlib is for creating the pie chart and bar chart in statistics tab
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# counter is for counting domain queries and stuff for charts
from collections import Counter

# this is where we save gui settings like cache on/off so it remembers after restart
CONFIG_FILE = 'netguard_config.json'


class DNSMonitorGUI:
    # this is the main gui class that creates everything you see on screen
    # it takes all the components from main.py and connects them to gui widgets
    def __init__(self, log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector):
        # storing all the components so we can use them in different methods
        self.log_queue = log_queue
        self.all_logs = all_logs
        self.stats_tracker = stats_tracker
        self.dns_cache = dns_cache
        self.blocklist = blocklist
        self.anomaly_detector = anomaly_detector
        # filter text is what user types in the search box to filter logs
        self.filter_text = ""
        # filter type is for filtering by query type like A, AAAA etc
        self.filter_type = "All"
        # when paused we stop updating logs in gui
        self.paused = False
        # tracking when we last updated stats so we dont refresh too often
        self.last_stats_update = 0
        # remembering scroll position so stats tab doesnt jump to top on refresh
        self.stats_scroll_position = 0
        
        # loading saved settings before creating widgets because we need cache state first
        self.load_config()
        
        # applying the saved cache state to actual dns cache object
        self.dns_cache.enabled = self.cache_enabled
        
        # all our dark theme colors defined here in one place
        # so if we want to change color scheme we just change these values
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
        
        # creating the main tkinter window
        self.root = tk.Tk()
        self.root.title("🛡️ NetGuard DNS Monitor v2.2")
        # setting default window size and minimum size so it doesnt get too small
        self.root.geometry("1200x900")
        self.root.minsize(1000, 700)
        
        # applying our dark theme to all widgets
        self.apply_theme()
        
        # main container that holds everything inside the window
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill='both', expand=True)
        
        # creating all the different parts of gui one by one
        self.create_header()
        
        self.create_menu()
        
        # control bar has cache toggle and quick stats at the top
        self.create_control_bar()
        
        # notebook is the tabbed interface with logs stats blocklist alerts tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=(5, 10))
        
        # when user switches tab we want to know so we can refresh that tabs data
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        # creating all 4 tabs for our application
        self.create_logs_tab()
        self.create_stats_tab()
        self.create_blocklist_tab()
        self.create_alerts_tab()
        
        # status bar at very bottom shows if server is running or paused
        self.create_status_bar()
        
        # starting the gui update loop that runs every 500ms
        self.update_gui()
    
    def load_config(self):
        """Load saved configuration from JSON file"""
        # trying to load saved settings, if file doesnt exist we use defaults
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.cache_enabled = config.get('cache_enabled', True)
            else:
                # first time running so cache is enabled by default
                self.cache_enabled = True
        except:
            self.cache_enabled = True
    
    def save_config(self):
        """Save configuration to JSON file"""
        # saving current settings so they persist after closing the app
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({'cache_enabled': self.cache_enabled}, f)
        except:
            pass
    
    def apply_theme(self):
        """Apply comprehensive dark theme"""
        # this function sets up the dark theme for all ttk widgets
        # without this everything would look like default ugly grey windows style
        style = ttk.Style()
        style.theme_use('clam')
        
        # setting base style for all widgets
        style.configure('.', background=self.bg_color, foreground=self.fg_color)
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.fg_color, font=('Segoe UI', 10))
        
        # label frame styling with border
        style.configure('TLabelframe', background=self.bg_color, foreground=self.fg_color, 
                       bordercolor=self.border_color, relief='solid')
        style.configure('TLabelframe.Label', background=self.bg_color, foreground=self.accent_color, 
                       font=('Segoe UI', 10, 'bold'))
        
        # notebook tabs styling - selected tab gets accent color
        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.bg_tertiary, foreground=self.fg_secondary, 
                       padding=[15, 8], font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab', 
                 background=[('selected', self.accent_color), ('active', self.bg_secondary)],
                 foreground=[('selected', self.bg_color), ('active', self.fg_color)])
        
        # button styling with hover effects
        style.configure('TButton', background=self.accent_color, foreground=self.bg_color, 
                       font=('Segoe UI', 9, 'bold'), padding=[12, 6], borderwidth=0)
        style.map('TButton', 
                 background=[('active', self.accent_secondary), ('pressed', '#007766')],
                 foreground=[('active', self.fg_color)])
        
        # special button styles for different actions
        style.configure('Accent.TButton', background=self.accent_color, foreground=self.bg_color)
        
        # danger button is red color for destructive actions like delete
        style.configure('Danger.TButton', background=self.error_color, foreground=self.fg_color)
        style.map('Danger.TButton', background=[('active', '#cc3344')])
        
        # entry field where user types text
        style.configure('TEntry', fieldbackground=self.bg_tertiary, foreground=self.fg_color,
                       insertcolor=self.fg_color, bordercolor=self.border_color, padding=5)
        
        # combobox is the dropdown selector for query type filter
        style.configure('TCombobox', fieldbackground=self.bg_tertiary, foreground=self.fg_color,
                       background=self.bg_tertiary, arrowcolor=self.fg_color)
        style.map('TCombobox', fieldbackground=[('readonly', self.bg_tertiary)])
        
        # treeview is the table that shows dns logs
        style.configure('Treeview', background=self.bg_secondary, foreground=self.fg_color,
                       fieldbackground=self.bg_secondary, borderwidth=0, font=('Consolas', 9))
        style.configure('Treeview.Heading', background=self.bg_tertiary, foreground=self.accent_color,
                       font=('Segoe UI', 9, 'bold'), borderwidth=0)
        style.map('Treeview', background=[('selected', self.accent_color)],
                 foreground=[('selected', self.bg_color)])
        
        # scrollbar styling to match dark theme
        style.configure('Vertical.TScrollbar', background=self.bg_tertiary, 
                       troughcolor=self.bg_secondary, borderwidth=0, arrowcolor=self.fg_color)
        style.map('Vertical.TScrollbar', background=[('active', self.accent_color)])
        
        # progress bar used when importing blocklist
        style.configure('TProgressbar', background=self.accent_color, troughcolor=self.bg_tertiary)
        
        # separator line between sections
        style.configure('TSeparator', background=self.border_color)
        
        # setting the main window background color
        self.root.configure(bg=self.bg_color)
    
    def create_header(self):
        """Create application header"""
        # this is the top bar with logo and title
        header_frame = tk.Frame(self.main_container, bg=self.bg_secondary, height=60)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # left side has the app name and version
        title_frame = tk.Frame(header_frame, bg=self.bg_secondary)
        title_frame.pack(side='left', padx=20, pady=10)
        
        title_label = tk.Label(title_frame, text="🛡️ NetGuard", font=('Segoe UI', 18, 'bold'),
                              bg=self.bg_secondary, fg=self.accent_color)
        title_label.pack(side='left')
        
        subtitle_label = tk.Label(title_frame, text="DNS Monitor v2.2", font=('Segoe UI', 12),
                                 bg=self.bg_secondary, fg=self.fg_secondary)
        subtitle_label.pack(side='left', padx=(10, 0))
        
        # right side shows current time like a clock
        info_frame = tk.Frame(header_frame, bg=self.bg_secondary)
        info_frame.pack(side='right', padx=20, pady=10)
        
        self.time_label = tk.Label(info_frame, text="", font=('Consolas', 10),
                                   bg=self.bg_secondary, fg=self.fg_secondary)
        self.time_label.pack(side='right')
        
        # start the clock updating every second
        self.update_time()
    
    def update_time(self):
        """Update time display"""
        # updating the clock label every 1 second so it shows current time
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"⏰ {current_time}")
        self.root.after(1000, self.update_time)
    
    def create_control_bar(self):
        """Create control bar with cache toggle and other controls"""
        # this bar sits below header and has cache control, quick stats and network status
        control_frame = tk.Frame(self.main_container, bg=self.bg_color)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # cache control section - user can enable/disable cache from here
        cache_frame = tk.LabelFrame(control_frame, text="⚡ Cache Control", 
                                    bg=self.bg_secondary, fg=self.accent_color,
                                    font=('Segoe UI', 9, 'bold'), bd=1, relief='solid')
        cache_frame.pack(side='left', padx=5, pady=5, ipadx=10, ipady=5)
        
        cache_inner = tk.Frame(cache_frame, bg=self.bg_secondary)
        cache_inner.pack(padx=10, pady=5)
        
        # showing current cache state with green or red indicator
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
        
        # quick stats section shows total queries blocked and cached count at a glance
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
        
        # separator between stats numbers
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
        
        # network status shows if dns server is active or paused
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
        # flipping cache state and saving to config file
        self.cache_enabled = not self.cache_enabled
        self.dns_cache.enabled = self.cache_enabled
        self.save_config()
        
        # updating the gui to show new cache state
        if self.cache_enabled:
            self.cache_status_label.config(text="● ENABLED", fg=self.success_color)
            self.cache_toggle_btn.config(text="Disable")
            messagebox.showinfo("Cache Enabled", 
                              "DNS caching is now ENABLED.\n\n"
                              "Queries will be cached for faster responses.")
        else:
            self.cache_status_label.config(text="● DISABLED", fg=self.error_color)
            self.cache_toggle_btn.config(text="Enable")
            # when disabling cache we also clear existing cached data
            self.dns_cache.clear()
            messagebox.showinfo("Cache Disabled", 
                              "DNS caching is now DISABLED.\n\n"
                              "All queries will go directly to upstream DNS.\n"
                              "Existing cache has been cleared.")
        
    def create_menu(self):
        """Create application menu"""
        # creating the menu bar at top of window with all the dropdown menus
        menubar = tk.Menu(self.root, bg=self.bg_secondary, fg=self.fg_color,
                         activebackground=self.accent_color, activeforeground=self.bg_color,
                         font=('Segoe UI', 9))
        self.root.config(menu=menubar)
        
        # file menu has export and clear options
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_secondary, fg=self.fg_color,
                           activebackground=self.accent_color, activeforeground=self.bg_color)
        menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(label="📤 Export Logs (CSV)", command=self.export_logs)
        file_menu.add_command(label="📊 Export Statistics", command=self.export_statistics)
        file_menu.add_command(label="🗑️ Clear Logs", command=self.clear_logs)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Exit", command=self.on_closing)
        
        # view menu has pause and refresh options
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_secondary, fg=self.fg_color,
                           activebackground=self.accent_color, activeforeground=self.bg_color)
        menubar.add_cascade(label="👁️ View", menu=view_menu)
        view_menu.add_command(label="⏸️ Pause/Resume Logging", command=self.toggle_pause)
        view_menu.add_command(label="🔄 Refresh Statistics", command=self.force_refresh_stats)
        
        # cache menu for cache related operations
        cache_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_secondary, fg=self.fg_color,
                            activebackground=self.accent_color, activeforeground=self.bg_color)
        menubar.add_cascade(label="⚡ Cache", menu=cache_menu)
        cache_menu.add_command(label="🔀 Toggle Cache", command=self.toggle_cache)
        cache_menu.add_command(label="🗑️ Clear Cache", command=self.clear_cache)
        cache_menu.add_command(label="📊 Cache Statistics", command=self.show_cache_stats)
        
        # blocklist menu for importing and managing blocked domains
        blocklist_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_secondary, fg=self.fg_color,
                                activebackground=self.accent_color, activeforeground=self.bg_color)
        menubar.add_cascade(label="🚫 Blocklist", menu=blocklist_menu)
        blocklist_menu.add_command(label="📁 Import from File", command=self.import_blocklist_file)
        blocklist_menu.add_command(label="🌐 Import from GitHub", command=self.import_github_blocklist)
        blocklist_menu.add_command(label="📥 Load Default Blocklist", command=self.load_default_blocklist)
        blocklist_menu.add_command(label="⚡ Load Preinstalled (64K)", command=self.load_preinstalled_blocklist)
        blocklist_menu.add_separator()
        blocklist_menu.add_command(label="💾 Export Blocklist", command=self.export_blocklist)
        
        # help menu with about and github help info
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_secondary, fg=self.fg_color,
                           activebackground=self.accent_color, activeforeground=self.bg_color)
        menubar.add_cascade(label="❓ Help", menu=help_menu)
        help_menu.add_command(label="ℹ️ About", command=self.show_about)
        help_menu.add_command(label="📚 GitHub Blocklists Help", command=self.show_github_help)
        
    def create_logs_tab(self):
        """Create logs tab with dark theme"""
        # this is the first tab where user sees real time dns queries coming in
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text='  📋 Live Logs  ')
        
        # filter section at top so user can search for specific domains or ips
        filter_frame = tk.Frame(logs_frame, bg=self.bg_color)
        filter_frame.pack(fill='x', padx=10, pady=10)
        
        # wrapping filter controls in a nice container box
        filter_container = tk.Frame(filter_frame, bg=self.bg_secondary, bd=1, relief='solid')
        filter_container.pack(fill='x')
        
        filter_inner = tk.Frame(filter_container, bg=self.bg_secondary)
        filter_inner.pack(fill='x', padx=15, pady=10)
        
        tk.Label(filter_inner, text="🔍 Filter:", bg=self.bg_secondary, fg=self.fg_color,
                font=('Segoe UI', 10)).pack(side='left', padx=(0, 5))
        
        # text entry where user types domain or ip to search
        self.filter_entry = tk.Entry(filter_inner, width=35, bg=self.bg_tertiary, fg=self.fg_color,
                                     insertbackground=self.fg_color, font=('Consolas', 10),
                                     relief='flat', bd=5)
        self.filter_entry.pack(side='left', padx=5)
        # filtering happens as user types not just when pressing enter
        self.filter_entry.bind('<KeyRelease>', self.apply_filter)
        
        tk.Label(filter_inner, text="Type:", bg=self.bg_secondary, fg=self.fg_color,
                font=('Segoe UI', 10)).pack(side='left', padx=(20, 5))
        
        # dropdown to filter by query type like A record AAAA etc
        self.type_filter = ttk.Combobox(filter_inner, width=10, 
                                        values=['All', 'A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'PTR'],
                                        state='readonly', font=('Consolas', 10))
        self.type_filter.set('All')
        self.type_filter.pack(side='left', padx=5)
        self.type_filter.bind('<<ComboboxSelected>>', self.apply_filter)
        
        ttk.Button(filter_inner, text="Clear Filter", 
                  command=self.clear_filter).pack(side='left', padx=15)
        
        # the main table area where logs are displayed
        tree_frame = tk.Frame(logs_frame, bg=self.bg_color)
        tree_frame.pack(expand=True, fill='both', padx=10, pady=(0, 10))
        
        # adding scrollbars both vertical and horizontal for the table
        y_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical')
        y_scrollbar.pack(side='right', fill='y')
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal')
        x_scrollbar.pack(side='bottom', fill='x')
        
        # creating the treeview table with all the columns we need
        self.tree = ttk.Treeview(tree_frame, 
                                 columns=('Timestamp', 'Source IP', 'Query Domain', 
                                         'Type', 'Details', 'Status'),
                                 show='headings',
                                 yscrollcommand=y_scrollbar.set,
                                 xscrollcommand=x_scrollbar.set)
        
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        # setting up each column with proper width and alignment
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
        
        # different colors for different log types so user can see at glance
        # green for success, red for failed, orange for blocked, blue for cached
        self.tree.tag_configure('success', foreground=self.success_color)
        self.tree.tag_configure('failed', foreground=self.error_color)
        self.tree.tag_configure('blocked', foreground=self.warning_color)
        self.tree.tag_configure('cached', foreground=self.info_color)
        
    def create_stats_tab(self):
        """Create statistics tab with dark theme"""
        # second tab shows all the statistics and charts about dns queries
        stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(stats_tab, text='  📊 Statistics  ')
        
        # top bar with refresh button
        top_bar = tk.Frame(stats_tab, bg=self.bg_secondary)
        top_bar.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(top_bar, text="🔄 Refresh Statistics", 
                  command=self.silent_refresh_stats).pack(side='left', padx=10, pady=5)
        
        tk.Label(top_bar, text="Auto-refresh: Every 10s when tab active", 
                font=('Segoe UI', 9, 'italic'), bg=self.bg_secondary, 
                fg=self.fg_secondary).pack(side='left', padx=10, pady=5)
        
        # making the stats area scrollable because it can get very long with charts
        canvas_frame = tk.Frame(stats_tab, bg=self.bg_color)
        canvas_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        canvas = tk.Canvas(canvas_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        self.stats_frame = tk.Frame(canvas, bg=self.bg_color)
        
        # this makes the scroll region update when content changes size
        self.stats_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        self.stats_canvas_window = canvas.create_window((0, 0), window=self.stats_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.stats_canvas = canvas
        self.stats_scrollbar = scrollbar
        
        # enabling mouse wheel scrolling so user can scroll with mouse wheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # saving scroll position so when stats refresh it doesnt jump back to top
        def on_scroll(*args):
            self.stats_scroll_position = canvas.yview()[0]
            scrollbar.set(*args)
        
        canvas.configure(yscrollcommand=on_scroll)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # showing loading message until first data comes in
        loading_frame = tk.Frame(self.stats_frame, bg=self.bg_color)
        loading_frame.pack(fill='both', expand=True, pady=50)
        
        tk.Label(loading_frame, text="📊", font=("Segoe UI", 48), 
                bg=self.bg_color, fg=self.accent_color).pack()
        tk.Label(loading_frame, text="Loading Statistics...", 
                font=("Segoe UI", 14), bg=self.bg_color, fg=self.fg_color).pack(pady=10)
    
    def on_tab_changed(self, event):
        """Handle tab change"""
        # when user clicks on statistics tab we refresh the stats immediately
        selected_tab = self.notebook.index(self.notebook.select())
        if selected_tab == 1:
            self.silent_refresh_stats()
    
    def update_stats_display(self):
        """Update statistics display"""
        # only update if we have actual data to show
        if not self.all_logs:
            return
        
        # remembering where user was scrolled to before we refresh
        saved_position = self.stats_scroll_position
        
        # removing all old widgets and rebuilding fresh
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # header for the stats section
        header_frame = tk.Frame(self.stats_frame, bg=self.bg_secondary)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(header_frame, text="📈 DNS Query Statistics", font=('Segoe UI', 16, 'bold'),
                bg=self.bg_secondary, fg=self.accent_color).pack(pady=10)
        
        # getting the stats text from our stats.py compute function
        stats_text = compute_stats(self.all_logs)
        
        # displaying the stats in a read only text widget
        text_frame = tk.Frame(self.stats_frame, bg=self.bg_secondary, bd=1, relief='solid')
        text_frame.pack(fill='x', padx=5, pady=5)
        
        stats_display = tk.Text(text_frame, wrap='word', height=25, 
                               font=('Consolas', 10), bg=self.bg_secondary, fg=self.fg_color,
                               relief='flat', borderwidth=15, insertbackground=self.fg_color)
        stats_display.insert('1.0', stats_text)
        # making it read only so user cant accidentally edit the stats
        stats_display.config(state='disabled')
        stats_display.pack(fill='both', expand=True)
        
        # adding the pie chart and bar chart below the text stats
        self.create_charts()
        
        # restoring scroll position after a small delay so widgets have time to render
        self.root.after(100, lambda: self.stats_canvas.yview_moveto(saved_position))
    
    def silent_refresh_stats(self):
        """Refresh without popup"""
        # just refreshing stats without showing any popup message to user
        self.update_stats_display()
    
    def force_refresh_stats(self):
        """Force refresh with confirmation"""
        # this one shows a popup confirming stats were refreshed
        self.update_stats_display()
        messagebox.showinfo("Statistics Refreshed", 
                           "Statistics have been updated with latest data.")
    
    def create_charts(self):
        """Create charts with dark theme"""
        # creating matplotlib charts for visual representation of dns data
        # only if we have data to show otherwise skip
        if not self.all_logs:
            return
        
        try:
            # container for all charts
            charts_frame = tk.Frame(self.stats_frame, bg=self.bg_color)
            charts_frame.pack(fill='x', padx=5, pady=10)
            
            # first chart is pie chart showing distribution of query types
            # like how many A records vs AAAA vs CNAME etc
            type_counter = Counter(log[3] for log in self.all_logs)
            if type_counter:
                pie_frame = tk.Frame(charts_frame, bg=self.bg_secondary, bd=1, relief='solid')
                pie_frame.pack(fill='x', pady=5)
                
                # creating the figure with dark background to match our theme
                fig = Figure(figsize=(7, 5), dpi=100, facecolor=self.bg_secondary)
                ax = fig.add_subplot(111)
                ax.set_facecolor(self.bg_secondary)
                
                # nice colors for each slice of the pie
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
                
                # making percentage text bold and dark so it shows on colored slices
                for autotext in autotexts:
                    autotext.set_color(self.bg_color)
                    autotext.set_fontweight('bold')
                
                ax.set_title('DNS Query Types Distribution', color=self.fg_color, 
                           fontsize=14, fontweight='bold', pad=20)
                
                fig.tight_layout()
                
                # embedding matplotlib chart into tkinter window
                canvas = FigureCanvasTkAgg(fig, master=pie_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(pady=10)
            
            # second chart is horizontal bar chart showing top 10 most requested domains
            domain_counter = Counter(log[2] for log in self.all_logs)
            top_domains = domain_counter.most_common(10)
            if top_domains:
                bar_frame = tk.Frame(charts_frame, bg=self.bg_secondary, bd=1, relief='solid')
                bar_frame.pack(fill='x', pady=5)
                
                domains, counts = zip(*top_domains)
                # cutting long domain names so they fit nicely in chart
                domains = [d[:35] + '...' if len(d) > 35 else d for d in domains]
                
                fig = Figure(figsize=(9, 6), dpi=100, facecolor=self.bg_secondary)
                ax = fig.add_subplot(111)
                ax.set_facecolor(self.bg_secondary)
                
                # creating horizontal bars with our accent color
                bars = ax.barh(domains, counts, color=self.accent_color, edgecolor=self.bg_secondary)
                
                # adding the count number at end of each bar so its easy to read
                for bar, count in zip(bars, counts):
                    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                           f'{count}', va='center', color=self.fg_color, fontsize=9)
                
                ax.set_title('Top 10 Requested Domains', color=self.fg_color, 
                           fontsize=14, fontweight='bold', pad=20)
                ax.set_xlabel('Request Count', color=self.fg_color, fontsize=11)
                
                # making axis labels white so they visible on dark background
                ax.tick_params(axis='x', colors=self.fg_color)
                ax.tick_params(axis='y', colors=self.fg_color)
                
                for spine in ax.spines.values():
                    spine.set_color(self.border_color)
                
                # inverting y axis so highest count domain is at top
                ax.invert_yaxis()
                fig.tight_layout()
                
                canvas = FigureCanvasTkAgg(fig, master=bar_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(pady=10)
                
        except Exception as e:
            # if chart creation fails we just print error and continue
            # we dont want chart error to crash the whole gui
            print(f"Error creating charts: {e}")
    
    def create_blocklist_tab(self):
        """Create blocklist tab with dark theme"""
        # third tab where user manages blocked and allowed domains
        blocklist_frame = ttk.Frame(self.notebook)
        self.notebook.add(blocklist_frame, text='  🚫 Blocklist  ')
        
        # row of buttons at top for all blocklist actions
        btn_frame = tk.Frame(blocklist_frame, bg=self.bg_secondary)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        btn_inner = tk.Frame(btn_frame, bg=self.bg_secondary)
        btn_inner.pack(pady=8)
        
        # all the action buttons for blocklist management
        ttk.Button(btn_inner, text="➕ Block Domain", 
                  command=self.add_blocked_domain).pack(side='left', padx=5)
        ttk.Button(btn_inner, text="✅ Allow Domain", 
                  command=self.add_allowed_domain).pack(side='left', padx=5)
        ttk.Button(btn_inner, text="📁 Import File", 
                  command=self.import_blocklist_file).pack(side='left', padx=5)
        ttk.Button(btn_inner, text="🌐 Import GitHub", 
                  command=self.import_github_blocklist).pack(side='left', padx=5)
        ttk.Button(btn_inner, text="⚡ Load Preinstalled (64K)", 
                  command=self.load_preinstalled_blocklist).pack(side='left', padx=5)
        ttk.Button(btn_inner, text="📥 Load Defaults", 
                  command=self.load_default_blocklist).pack(side='left', padx=5)
        ttk.Button(btn_inner, text="💾 Export", 
                  command=self.export_blocklist).pack(side='left', padx=5)
        
        # main area split into two halves - blocked on left, allowed on right
        lists_frame = tk.Frame(blocklist_frame, bg=self.bg_color)
        lists_frame.pack(expand=True, fill='both', padx=10, pady=(0, 10))
        
        # left side - blocked domains list with search and remove
        blocked_container = tk.LabelFrame(lists_frame, text="🚫 Blocked Domains", 
                                          bg=self.bg_secondary, fg=self.error_color,
                                          font=('Segoe UI', 10, 'bold'))
        blocked_container.pack(side='left', expand=True, fill='both', padx=(0, 5))
        
        # search bar for blocked domains so user can find specific domain quickly
        search_frame = tk.Frame(blocked_container, bg=self.bg_secondary)
        search_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(search_frame, text="🔍", bg=self.bg_secondary, fg=self.fg_color).pack(side='left')
        self.blocked_search = tk.Entry(search_frame, bg=self.bg_tertiary, fg=self.fg_color,
                                       insertbackground=self.fg_color, relief='flat', bd=5)
        self.blocked_search.pack(side='left', fill='x', expand=True, padx=5)
        # filtering list as user types in search box
        self.blocked_search.bind('<KeyRelease>', lambda e: self.filter_blocked_list())
        
        # the actual list of blocked domains with scrollbar
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
        
        # bottom section with count label and remove button
        bottom_frame = tk.Frame(blocked_container, bg=self.bg_secondary)
        bottom_frame.pack(fill='x', padx=10, pady=10)
        
        self.blocked_count_label = tk.Label(bottom_frame, text="Count: 0",
                                            bg=self.bg_secondary, fg=self.fg_color,
                                            font=('Segoe UI', 9, 'bold'))
        self.blocked_count_label.pack(side='left')
        
        ttk.Button(bottom_frame, text="Remove Selected", 
                  command=self.remove_blocked).pack(side='right')
        
        # right side - allowed domains list (whitelist)
        # domains here will never get blocked even if they match blocklist
        allowed_container = tk.LabelFrame(lists_frame, text="✅ Allowed Domains (Whitelist)", 
                                          bg=self.bg_secondary, fg=self.success_color,
                                          font=('Segoe UI', 10, 'bold'))
        allowed_container.pack(side='left', expand=True, fill='both', padx=(5, 0))
        
        # search bar for allowed domains
        search_frame2 = tk.Frame(allowed_container, bg=self.bg_secondary)
        search_frame2.pack(fill='x', padx=10, pady=10)
        
        tk.Label(search_frame2, text="🔍", bg=self.bg_secondary, fg=self.fg_color).pack(side='left')
        self.allowed_search = tk.Entry(search_frame2, bg=self.bg_tertiary, fg=self.fg_color,
                                       insertbackground=self.fg_color, relief='flat', bd=5)
        self.allowed_search.pack(side='left', fill='x', expand=True, padx=5)
        self.allowed_search.bind('<KeyRelease>', lambda e: self.filter_allowed_list())
        
        # allowed domains listbox with scrollbar
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
        
        # bottom of allowed list with count and remove button
        bottom_frame2 = tk.Frame(allowed_container, bg=self.bg_secondary)
        bottom_frame2.pack(fill='x', padx=10, pady=10)
        
        self.allowed_count_label = tk.Label(bottom_frame2, text="Count: 0",
                                            bg=self.bg_secondary, fg=self.fg_color,
                                            font=('Segoe UI', 9, 'bold'))
        self.allowed_count_label.pack(side='left')
        
        ttk.Button(bottom_frame2, text="Remove Selected", 
                  command=self.remove_allowed).pack(side='right')
        
        # loading and showing current blocklist data in the listboxes
        self.update_blocklist_display()
    
    def filter_blocked_list(self):
        """Filter blocked list"""
        # getting what user typed and filtering the blocked list based on that
        search_term = self.blocked_search.get().lower()
        self.update_blocklist_display(blocked_filter=search_term)
    
    def filter_allowed_list(self):
        """Filter allowed list"""
        # same thing but for allowed list filtering
        search_term = self.allowed_search.get().lower()
        self.update_blocklist_display(allowed_filter=search_term)
    
    def create_alerts_tab(self):
        """Create alerts tab with dark theme"""
        # fourth tab shows security alerts from anomaly detector
        # like if someone is doing ddos or visiting suspicious domains
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text='  ⚠️ Security Alerts  ')
        
        # buttons to clear and refresh alerts
        ctrl_frame = tk.Frame(alerts_frame, bg=self.bg_secondary)
        ctrl_frame.pack(fill='x', padx=10, pady=10)
        
        ctrl_inner = tk.Frame(ctrl_frame, bg=self.bg_secondary)
        ctrl_inner.pack(pady=8)
        
        ttk.Button(ctrl_inner, text="🗑️ Clear All Alerts", 
                  command=self.clear_alerts).pack(side='left', padx=5)
        ttk.Button(ctrl_inner, text="🔄 Refresh", 
                  command=self.update_alerts).pack(side='left', padx=5)
        
        # text area where alerts are displayed with colored severity levels
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
        
        # setting up text tags for different severity levels with different colors
        # HIGH is red, MEDIUM is orange, LOW is blue
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
        # thin bar at very bottom of window showing server status
        self.status_bar = tk.Frame(self.main_container, bg=self.bg_tertiary, height=30)
        self.status_bar.pack(fill='x', side='bottom')
        self.status_bar.pack_propagate(False)
        
        # left side shows running or paused status
        self.status_label = tk.Label(self.status_bar, text="● DNS Monitor Running", 
                                     bg=self.bg_tertiary, fg=self.success_color,
                                     font=('Segoe UI', 9))
        self.status_label.pack(side='left', padx=15)
        
        # right side shows cache status and total query count
        self.status_details = tk.Label(self.status_bar, text="", 
                                       bg=self.bg_tertiary, fg=self.fg_secondary,
                                       font=('Consolas', 9))
        self.status_details.pack(side='right', padx=15)
    
    def update_logs(self):
        """Update logs with batch processing limit"""
        # if logging is paused we skip updating
        if self.paused:
            return
        
        # we process max 50 log entries per update cycle to keep gui responsive
        # if we try to process all at once gui might freeze
        batch = 0
        max_batch = 50
        while not self.log_queue.empty() and batch < max_batch:
            try:
                item = self.log_queue.get_nowait()
                batch += 1
                
                # checking if its an alert or a normal log entry
                if isinstance(item, tuple) and item[0] == 'ALERT':
                    self.display_alert(item[1])
                else:
                    # unpacking the log entry tuple into individual variables
                    timestamp, ip, domain, qtype, details, success, blocked, cached = item
                    
                    # applying text filter - skip if doesnt match search term
                    if self.filter_text and self.filter_text.lower() not in domain.lower() and \
                       self.filter_text.lower() not in ip.lower():
                        continue
                    
                    # applying type filter - skip if doesnt match selected query type
                    if self.filter_type != "All" and qtype != self.filter_type:
                        continue
                    
                    # deciding which color tag and status text to use based on result
                    if blocked:
                        tag, status = 'blocked', 'BLOCKED'
                    elif cached:
                        tag, status = 'cached', 'CACHED'
                    elif success:
                        tag, status = 'success', 'SUCCESS'
                    else:
                        tag, status = 'failed', 'FAILED'
                    
                    # inserting at position 0 so newest logs appear at top
                    self.tree.insert('', 0, values=(timestamp, ip, domain, qtype, details, status), 
                                    tags=(tag,))
                    
                    # keeping only 1000 rows in table so gui doesnt get slow
                    if len(self.tree.get_children()) > 1000:
                        self.tree.delete(self.tree.get_children()[-1])
            
            except queue.Empty:
                break
            except Exception as e:
                print(f"Error updating logs: {e}")
    
    def update_gui(self):
        """Main GUI update"""
        # this is the main update loop that runs every 500ms
        # it updates logs, stats, alerts and status bar
        self.update_logs()
        
        # auto refresh stats tab every 10 seconds but only when its the active tab
        current_time = datetime.datetime.now().timestamp()
        if self.notebook.index(self.notebook.select()) == 1:
            if current_time - self.last_stats_update > 10:
                self.update_stats_display()
                self.last_stats_update = current_time
        
        # auto refresh alerts when alerts tab is active
        if self.notebook.index(self.notebook.select()) == 3:
            self.update_alerts()
        
        # updating the status bar and quick stats with latest numbers
        stats = self.stats_tracker.get_stats()
        cache_stats = self.dns_cache.get_stats()
        
        cache_status = "ON" if self.cache_enabled else "OFF"
        
        # changing status indicator based on whether logging is paused or not
        if self.paused:
            self.status_label.config(text="⏸ PAUSED", fg=self.warning_color)
            self.network_status_label.config(text="● Paused", fg=self.warning_color)
        else:
            self.status_label.config(text="● Running", fg=self.success_color)
            self.network_status_label.config(text="● Active", fg=self.success_color)
        
        # updating the right side of status bar with cache and query info
        self.status_details.config(
            text=f"Cache: {cache_status} ({cache_stats['hit_rate']:.1f}% hit) | "
                 f"Total: {stats['total']:,} queries"
        )
        
        # updating the quick stats numbers in control bar
        self.stat_queries.config(text=f"Queries: {stats['total']:,}")
        self.stat_blocked.config(text=f"Blocked: {stats['blocked']:,}")
        self.stat_cached.config(text=f"Cached: {stats['cached']:,}")
        
        # scheduling next update after 500ms
        self.root.after(500, self.update_gui)
    
    def update_alerts(self):
        """Update alerts"""
        # getting latest alerts from anomaly detector
        alerts = self.anomaly_detector.get_alerts()
        
        # if no alerts nothing to show
        if not alerts:
            return
        
        # clearing old alerts text and rebuilding
        self.alerts_text.delete(1.0, tk.END)
        
        if not alerts:
            # showing message that everything is fine no threats detected
            self.alerts_text.insert(tk.END, "✅ No security alerts detected.\n\n", 'header')
            self.alerts_text.insert(tk.END, "The system is monitoring for:\n\n")
            self.alerts_text.insert(tk.END, "  • Excessive queries (DDoS indicators)\n")
            self.alerts_text.insert(tk.END, "  • Suspicious domain keywords\n")
            self.alerts_text.insert(tk.END, "  • DGA (Domain Generation Algorithm) patterns\n")
        else:
            # showing all alerts with severity color coding
            self.alerts_text.insert(tk.END, f"⚠️ {len(alerts)} Security Alert(s)\n\n", 'header')
            for alert in reversed(alerts):
                severity = alert['severity']
                timestamp = datetime.datetime.fromtimestamp(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                self.alerts_text.insert(tk.END, f"[{timestamp}] ", 'header')
                self.alerts_text.insert(tk.END, f"[{severity}] ", severity)
                self.alerts_text.insert(tk.END, f"{alert['message']}\n\n")
    
    def update_blocklist_display(self, blocked_filter='', allowed_filter=''):
        """Update blocklist display"""
        # getting current lists from blocklist manager
        blocked, allowed = self.blocklist.get_lists()
        
        # updating blocked domains listbox with optional search filter
        self.blocked_listbox.delete(0, tk.END)
        filtered_blocked = [d for d in sorted(blocked) if blocked_filter.lower() in d.lower()]
        for domain in filtered_blocked:
            self.blocked_listbox.insert(tk.END, domain)
        self.blocked_count_label.config(text=f"Count: {len(blocked):,} (showing: {len(filtered_blocked):,})")
        
        # updating allowed domains listbox with optional search filter
        self.allowed_listbox.delete(0, tk.END)
        filtered_allowed = [d for d in sorted(allowed) if allowed_filter.lower() in d.lower()]
        for domain in filtered_allowed:
            self.allowed_listbox.insert(tk.END, domain)
        self.allowed_count_label.config(text=f"Count: {len(allowed):,} (showing: {len(filtered_allowed):,})")
    
    def load_preinstalled_blocklist(self):
        """Show instructions for loading preinstalled blocklist manually"""
        # we show instructions instead of loading directly because loading 64k domains
        # at once can crash the app so manual method is safer
        instructions = """⚡ LOAD PREINSTALLED BLOCKLIST (64K Domains)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ IMPORTANT: Loading large lists directly may crash the app!

To safely use the preinstalled 64K blocklist, follow these steps:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 STEP 1: Open the App Folder
   • Navigate to where NetGuard is installed
   • You should see all the program files there

📄 STEP 2: Find the Preinstalled Blocklist
   • Look for: preinstalled-blocklist.json
   • This file contains 64,300+ ad/tracking domains

📋 STEP 3: Copy the Contents
   • Open preinstalled-blocklist.json with Notepad
   • Select All (Ctrl+A) and Copy (Ctrl+C)

📝 STEP 4: Paste into Your Blocklist
   • Open blocklist.json with Notepad
   • Replace all contents with what you copied
   • Or merge the lists if you have custom domains

💾 STEP 5: Save and Restart
   • Save blocklist.json (Ctrl+S)
   • Close and restart NetGuard DNS Monitor

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ BENEFITS:
   • ~72% ad-blocking coverage
   • No app lag or crashes
   • Fast startup after restart

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        messagebox.showinfo("Load Preinstalled Blocklist - Instructions", instructions)
    
    def import_github_blocklist(self):
        """Import from GitHub with crash warning and manual instructions"""
        # first showing warning because large github blocklists can crash the app
        warning_msg = """⚠️ WARNING - APP MAY CRASH!

Importing large blocklists from GitHub may cause the app to become unresponsive or crash completely.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 RECOMMENDED MANUAL METHOD:

1. Download the blocklist file from GitHub manually
2. Convert to JSON format (array of domains):
   ["domain1.com", "domain2.com", "domain3.com"]
3. Open blocklist.json in the app folder with Notepad
4. Paste the domains and save
5. Restart NetGuard DNS Monitor

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This manual method is:
✅ Faster loading
✅ No app crashes
✅ Works with any size list

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Do you still want to try the automatic import?
(Not recommended for large lists)"""
        
        result = messagebox.askyesno("⚠️ Import Warning", warning_msg)
        
        if not result:
            return
        
        # creating a popup dialog for user to enter the github url
        dialog = tk.Toplevel(self.root)
        dialog.title("Import from GitHub")
        dialog.geometry("650x450")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # dialog header
        header = tk.Frame(dialog, bg=self.bg_secondary)
        header.pack(fill='x', padx=0, pady=0)
        
        tk.Label(header, text="🌐 Import Blocklist from GitHub", 
                font=('Segoe UI', 14, 'bold'), bg=self.bg_secondary, 
                fg=self.accent_color).pack(pady=15)
        
        # main content area with url input and popular lists
        content = tk.Frame(dialog, bg=self.bg_color)
        content.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Label(content, text="Enter GitHub Blocklist URL:", 
                font=('Segoe UI', 10), bg=self.bg_color, fg=self.fg_color).pack(anchor='w', pady=(10, 5))
        
        # url input field with default stevenblack url already filled in
        url_entry = tk.Entry(content, width=70, bg=self.bg_tertiary, fg=self.fg_color,
                            insertbackground=self.fg_color, font=('Consolas', 10),
                            relief='flat', bd=8)
        url_entry.pack(fill='x', pady=5)
        url_entry.insert(0, "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts")
        
        # showing some popular blocklist urls for reference
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
        
        # import and cancel buttons at bottom
        btn_frame = tk.Frame(dialog, bg=self.bg_color)
        btn_frame.pack(fill='x', padx=20, pady=15)
        
        def do_import():
            # this function runs when user clicks import button
            url = url_entry.get().strip()
            if not url:
                messagebox.showwarning("No URL", "Please enter a URL")
                return
            
            # showing progress bar while downloading
            progress = ttk.Progressbar(btn_frame, mode='indeterminate')
            progress.pack(fill='x', pady=10)
            progress.start()
            
            # running import on separate thread so gui doesnt freeze while downloading
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
        """Import from file with crash warning and manual instructions"""
        # same crash warning as github import because large files can crash too
        warning_msg = """⚠️ WARNING - APP MAY CRASH!

Importing large blocklist files may cause the app to become unresponsive or crash completely.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 RECOMMENDED MANUAL METHOD:

1. Open your blocklist file with Notepad
2. Convert to JSON format (array of domains):
   ["domain1.com", "domain2.com", "domain3.com"]
3. Open blocklist.json in the app folder with Notepad
4. Paste the domains and save
5. Restart NetGuard DNS Monitor

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This manual method is:
✅ Faster loading
✅ No app crashes
✅ Works with any size list

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Do you still want to try the automatic import?
(Not recommended for large files)"""
        
        result = messagebox.askyesno("⚠️ Import Warning", warning_msg)
        
        if not result:
            return
        
        # opening file dialog so user can pick the blocklist text file
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
        # letting user save their blocklist to a text file for backup or sharing
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
        # popup asking user to type a domain name to block
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
        # popup asking user to type a domain to whitelist
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
        # removing the selected domain from blocked list
        selection = self.blocked_listbox.curselection()
        if selection:
            domain = self.blocked_listbox.get(selection[0])
            self.blocklist.remove_blocked(domain)
            self.update_blocklist_display()
    
    def remove_allowed(self):
        """Remove allowed"""
        # removing the selected domain from allowed list
        selection = self.allowed_listbox.curselection()
        if selection:
            domain = self.allowed_listbox.get(selection[0])
            self.blocklist.remove_allowed(domain)
            self.update_blocklist_display()
    
    def load_default_blocklist(self):
        """Load defaults"""
        # loading the built in default blocklist with common ad domains
        self.blocklist.load_default_blocklist()
        self.update_blocklist_display()
        blocked, _ = self.blocklist.get_lists()
        messagebox.showinfo("Loaded", f"Loaded {len(blocked):,} domains.")
    
    def display_alert(self, alert):
        """Display alert"""
        # showing a single alert in the alerts text widget with proper formatting
        timestamp = datetime.datetime.fromtimestamp(alert['timestamp']).strftime('%H:%M:%S')
        severity = alert['severity']
        self.alerts_text.insert(tk.END, f"[{timestamp}] ", 'header')
        self.alerts_text.insert(tk.END, f"[{severity}] ", severity)
        self.alerts_text.insert(tk.END, f"{alert['message']}\n\n")
        # scrolling to bottom so newest alert is visible
        self.alerts_text.see(tk.END)
    
    def clear_alerts(self):
        """Clear alerts"""
        # asking user to confirm before clearing all alerts
        if messagebox.askyesno("Clear", "Clear all alerts?"):
            self.alerts_text.delete(1.0, tk.END)
            self.anomaly_detector.alerts.clear()
    
    def apply_filter(self, event=None):
        """Apply filter"""
        # applying the search filter to logs table
        # this clears the table and re-adds only matching entries
        self.filter_text = self.filter_entry.get().strip()
        self.filter_type = self.type_filter.get()
        
        # clearing all current rows first
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # going through last 1000 logs and adding ones that match filter
        for log in reversed(self.all_logs[-1000:]):
            timestamp, ip, domain, qtype, details, success, blocked, cached = log
            
            # checking if log matches text filter
            if self.filter_text:
                if self.filter_text.lower() not in domain.lower() and \
                   self.filter_text.lower() not in ip.lower():
                    continue
            
            # checking if log matches type filter
            if self.filter_type != "All" and qtype != self.filter_type:
                continue
            
            # deciding tag and status based on what happened with the query
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
        # resetting all filter fields back to default and showing all logs
        self.filter_entry.delete(0, tk.END)
        self.type_filter.set('All')
        self.filter_text = ""
        self.filter_type = "All"
        self.apply_filter()
    
    def export_logs(self):
        """Export logs"""
        # exporting all dns logs to csv file so user can analyze in excel
        if not self.all_logs:
            messagebox.showinfo("No Data", "No logs to export.")
            return
        
        # asking user where to save the csv file
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"dns_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # writing header row first
                    writer.writerow(['Timestamp', 'Source IP', 'Domain', 'Type', 
                                   'Details', 'Success', 'Blocked', 'Cached'])
                    # writing all log entries
                    writer.writerows(self.all_logs)
                messagebox.showinfo("Success", f"Exported {len(self.all_logs):,} logs")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def export_statistics(self):
        """Export stats"""
        # exporting statistics report to a text file
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
        # clearing all logs from memory and from the gui table
        if messagebox.askyesno("Confirm", "Clear all logs?"):
            self.all_logs.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)
            messagebox.showinfo("Cleared", "All logs cleared.")
    
    def clear_cache(self):
        """Clear cache"""
        # clearing all cached dns responses
        if messagebox.askyesno("Confirm", "Clear DNS cache?"):
            self.dns_cache.clear()
            messagebox.showinfo("Success", "DNS cache cleared.")
    
    def show_cache_stats(self):
        """Show cache stats"""
        # showing popup with detailed cache statistics
        stats = self.dns_cache.get_stats()
        cache_status = "Enabled" if self.cache_enabled else "Disabled"
        
        # giving a rating based on how good the cache hit rate is
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
        # toggling between paused and running state for log updates
        self.paused = not self.paused
        status = "PAUSED" if self.paused else "RESUMED"
        messagebox.showinfo("Status", f"Logging {status}")
    
    def show_github_help(self):
        """Show GitHub help"""
        # showing help info about how to use github blocklists
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
        # about dialog with project information
        about_text = """NetGuard DNS Monitor v2.2

Institution: Softwarica College of IT & E-Commerce
Affiliation: Coventry University, UK
Author: 4A 68 61 70 65 6E 64 72 61 20 6B 61 6E 64 65 6C

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
        # saving settings and closing the window properly
        self.save_config()
        self.root.destroy()
    
    def run(self):
        """Run GUI"""
        # setting up close handler and starting the tkinter main loop
        # mainloop keeps the window open and responsive until user closes it
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


# this function is called from main.py to create and start the gui
# it creates instance of our gui class and runs it
def create_gui(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector):
    """Create and run GUI"""
    app = DNSMonitorGUI(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector)
    app.run()
