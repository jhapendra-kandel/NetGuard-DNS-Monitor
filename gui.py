import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import queue
import csv
import datetime
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
        
        self.root = tk.Tk()
        self.root.title("🛡️ DNS Network Activity Monitor")
        self.root.geometry("1100x800")
        
        self.create_menu()
        
        self.status_bar = tk.Label(self.root, text="DNS Monitor Running", 
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        self.create_logs_tab()
        self.create_stats_tab()
        self.create_blocklist_tab()
        self.create_alerts_tab()
        
        self.update_gui()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Logs (CSV)", command=self.export_logs)
        file_menu.add_command(label="Clear Logs", command=self.clear_logs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Pause/Resume", command=self.toggle_pause)
        
        cache_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cache", menu=cache_menu)
        cache_menu.add_command(label="Clear Cache", command=self.clear_cache)
        cache_menu.add_command(label="Cache Statistics", command=self.show_cache_stats)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
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
                                        values=['All', 'A', 'AAAA', 'CNAME', 'MX', 'TXT'],
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
        
        self.tree.column('Timestamp', width=150)
        self.tree.column('Source IP', width=120)
        self.tree.column('Query Domain', width=300)
        self.tree.column('Type', width=70)
        self.tree.column('Details', width=180)
        self.tree.column('Status', width=80)
        
        self.tree.pack(expand=True, fill='both')
        
        self.tree.tag_configure('success', foreground='green')
        self.tree.tag_configure('failed', foreground='red')
        self.tree.tag_configure('blocked', foreground='orange')
        self.tree.tag_configure('cached', foreground='blue')
        
    def create_stats_tab(self):
        stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(stats_tab, text='📊 Statistics & Analytics')
        
        # FIXED: Proper scrollbar implementation
        canvas = tk.Canvas(stats_tab, bg='white')
        scrollbar = ttk.Scrollbar(stats_tab, orient="vertical", command=canvas.yview)
        self.stats_frame = ttk.Frame(canvas)
        
        # Configure scroll region when content changes
        self.stats_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.stats_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(self.stats_frame, text="Waiting for DNS activity...", 
                font=("Arial", 12)).pack(pady=20)
    
    def create_blocklist_tab(self):
        blocklist_frame = ttk.Frame(self.notebook)
        self.notebook.add(blocklist_frame, text='🚫 Blocklist Manager')
        
        # Control buttons
        btn_frame = ttk.Frame(blocklist_frame)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame, text="➕ Add Blocked Domain", 
                  command=self.add_blocked_domain).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="➕ Add Allowed Domain", 
                  command=self.add_allowed_domain).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Load Default Ads/Trackers", 
                  command=self.load_default_blocklist).pack(side='left', padx=5)
        
        # Lists frame
        lists_frame = ttk.Frame(blocklist_frame)
        lists_frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Blocked list
        blocked_frame = ttk.LabelFrame(lists_frame, text="Blocked Domains", padding=10)
        blocked_frame.pack(side='left', expand=True, fill='both', padx=5)
        
        self.blocked_listbox = tk.Listbox(blocked_frame, selectmode=tk.SINGLE)
        self.blocked_listbox.pack(expand=True, fill='both')
        
        ttk.Button(blocked_frame, text="Remove Selected", 
                  command=self.remove_blocked).pack(pady=5)
        
        # Allowed list
        allowed_frame = ttk.LabelFrame(lists_frame, text="Allowed Domains", padding=10)
        allowed_frame.pack(side='left', expand=True, fill='both', padx=5)
        
        self.allowed_listbox = tk.Listbox(allowed_frame, selectmode=tk.SINGLE)
        self.allowed_listbox.pack(expand=True, fill='both')
        
        ttk.Button(allowed_frame, text="Remove Selected", 
                  command=self.remove_allowed).pack(pady=5)
        
        self.update_blocklist_display()
    
    def create_alerts_tab(self):
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text='⚠️ Security Alerts')
        
        # Info label
        info_label = ttk.Label(alerts_frame, 
                              text="Real-time anomaly detection and security alerts",
                              font=('Arial', 10, 'bold'))
        info_label.pack(pady=10)
        
        # Alerts display
        alerts_text_frame = ttk.Frame(alerts_frame)
        alerts_text_frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(alerts_text_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.alerts_text = tk.Text(alerts_text_frame, wrap='word', 
                                   yscrollcommand=scrollbar.set, 
                                   font=('Courier', 9))
        scrollbar.config(command=self.alerts_text.yview)
        self.alerts_text.pack(expand=True, fill='both')
        
        self.alerts_text.tag_configure('HIGH', foreground='red', font=('Courier', 9, 'bold'))
        self.alerts_text.tag_configure('MEDIUM', foreground='orange', font=('Courier', 9, 'bold'))
        self.alerts_text.tag_configure('LOW', foreground='blue')
        
        ttk.Button(alerts_frame, text="Clear Alerts", 
                  command=self.clear_alerts).pack(pady=5)
    
    def apply_filter(self):
        self.filter_text = self.filter_entry.get().lower()
        self.filter_type = self.type_filter.get()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for log in reversed(self.all_logs):
            if self.matches_filter(log):
                self.insert_log_entry(log)
    
    def matches_filter(self, log):
        timestamp, src_ip, query_name, query_type, details, success, blocked, cached = log
        
        if self.filter_text:
            if not (self.filter_text in query_name.lower() or 
                   self.filter_text in src_ip.lower()):
                return False
        
        if self.filter_type != 'All' and query_type != self.filter_type:
            return False
        
        return True
    
    def clear_filter(self):
        self.filter_entry.delete(0, tk.END)
        self.type_filter.set('All')
        self.apply_filter()
    
    def insert_log_entry(self, log):
        timestamp, src_ip, query_name, query_type, details, success, blocked, cached = log
        
        if blocked:
            status = '🚫'
            tag = 'blocked'
        elif cached:
            status = '💾'
            tag = 'cached'
        elif success:
            status = '✓'
            tag = 'success'
        else:
            status = '✗'
            tag = 'failed'
        
        self.tree.insert('', 0, 
                        values=(timestamp, src_ip, query_name, query_type, details, status),
                        tags=(tag,))
    
    def update_logs(self):
        if self.paused:
            return
        
        count = 0
        try:
            while count < 50:
                item = self.log_queue.get_nowait()
                
                # Handle alerts
                if item[0] == 'ALERT':
                    self.display_alert(item[1])
                else:
                    # Regular log entry
                    if self.matches_filter(item):
                        self.insert_log_entry(item)
                count += 1
        except queue.Empty:
            pass
    
    def update_stats(self):
        # Only update every 2 seconds to avoid performance issues
        current_time = datetime.datetime.now().timestamp()
        if current_time - self.last_stats_update < 2:
            return
        
        self.last_stats_update = current_time
        
        if self.notebook.index(self.notebook.select()) != 1:
            return
        
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Performance metrics
        perf_stats = self.stats_tracker.get_stats()
        cache_stats = self.dns_cache.get_stats()
        
        metrics_frame = ttk.LabelFrame(self.stats_frame, text="📈 Performance Metrics", padding=10)
        metrics_frame.pack(fill='x', padx=10, pady=5)
        
        metrics_text = f"""Total Queries: {perf_stats['total']:,}
Failed Queries: {perf_stats['failed']:,} ({perf_stats['failed']/max(perf_stats['total'], 1)*100:.1f}%)
Blocked Queries: {perf_stats['blocked']:,} ({perf_stats['blocked']/max(perf_stats['total'], 1)*100:.1f}%)
Cached Queries: {perf_stats['cached']:,} ({perf_stats['cached']/max(perf_stats['total'], 1)*100:.1f}%)
Average Response Time: {perf_stats['avg_time']:.2f} ms
Success Rate: {(perf_stats['total']-perf_stats['failed'])/max(perf_stats['total'], 1)*100:.1f}%

Cache Hit Rate: {cache_stats['hit_rate']:.1f}% ({cache_stats['hits']}/{cache_stats['hits'] + cache_stats['misses']} hits)
Cache Size: {cache_stats['size']} entries"""
        
        tk.Label(metrics_frame, text=metrics_text, justify='left', 
                font=('Courier', 10)).pack(anchor='w')
        
        # Activity summary
        summary_frame = ttk.LabelFrame(self.stats_frame, text="📋 Activity Summary", padding=10)
        summary_frame.pack(fill='x', padx=10, pady=5)
        
        stats_text = tk.Text(summary_frame, wrap='word', height=12, state='normal')
        stats_text.insert(tk.END, compute_stats(self.all_logs))
        stats_text.config(state='disabled')
        stats_text.pack(fill='x')
        
        self.create_charts()
    
    def create_charts(self):
        if not self.all_logs:
            return
        
        # Query types
        type_counter = Counter(log[3] for log in self.all_logs)
        if type_counter:
            fig = Figure(figsize=(5, 3.5), dpi=100)
            ax = fig.add_subplot(111)
            ax.pie(list(type_counter.values()), labels=list(type_counter.keys()),
                   autopct='%1.1f%%', startangle=90)
            ax.set_title('Query Types Distribution')
            
            canvas = FigureCanvasTkAgg(fig, master=self.stats_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10, fill='both', expand=True)
        
        # Top domains
        domain_counter = Counter(log[2] for log in self.all_logs)
        top_domains = domain_counter.most_common(10)
        if top_domains:
            domains, counts = zip(*top_domains)
            
            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.barh(domains, counts, color='skyblue')
            ax.set_title('Top 10 Requested Domains')
            ax.set_xlabel('Request Count')
            ax.invert_yaxis()
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=self.stats_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10, fill='both', expand=True)
    
    def update_gui(self):
        self.update_logs()
        
        if self.notebook.index(self.notebook.select()) == 1:
            self.update_stats()
        
        total = self.stats_tracker.get_stats()['total']
        blocked = self.stats_tracker.get_stats()['blocked']
        cached = self.stats_tracker.get_stats()['cached']
        status_text = f"Queries: {total:,} | Blocked: {blocked:,} | Cached: {cached:,} | "
        status_text += "PAUSED" if self.paused else "Running ✓"
        self.status_bar.config(text=status_text)
        
        self.root.after(500, self.update_gui)
    
    def add_blocked_domain(self):
        domain = simpledialog.askstring("Add Blocked Domain", "Enter domain to block:")
        if domain:
            self.blocklist.add_blocked(domain)
            self.update_blocklist_display()
            messagebox.showinfo("Success", f"Blocked: {domain}")
    
    def add_allowed_domain(self):
        domain = simpledialog.askstring("Add Allowed Domain", "Enter domain to allow:")
        if domain:
            self.blocklist.add_allowed(domain)
            self.update_blocklist_display()
            messagebox.showinfo("Success", f"Allowed: {domain}")
    
    def remove_blocked(self):
        selection = self.blocked_listbox.curselection()
        if selection:
            domain = self.blocked_listbox.get(selection[0])
            self.blocklist.remove_blocked(domain)
            self.update_blocklist_display()
    
    def remove_allowed(self):
        selection = self.allowed_listbox.curselection()
        if selection:
            domain = self.allowed_listbox.get(selection[0])
            self.blocklist.remove_allowed(domain)
            self.update_blocklist_display()
    
    def load_default_blocklist(self):
        self.blocklist.load_default_blocklist()
        self.update_blocklist_display()
        messagebox.showinfo("Success", "Loaded default ad/tracker blocklist")
    
    def update_blocklist_display(self):
        blocked, allowed = self.blocklist.get_lists()
        
        self.blocked_listbox.delete(0, tk.END)
        for domain in sorted(blocked):
            self.blocked_listbox.insert(tk.END, domain)
        
        self.allowed_listbox.delete(0, tk.END)
        for domain in sorted(allowed):
            self.allowed_listbox.insert(tk.END, domain)
    
    def display_alert(self, alert):
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        severity = alert['severity']
        message = f"[{timestamp}] [{severity}] {alert['message']}\n"
        
        self.alerts_text.insert(tk.END, message, severity)
        self.alerts_text.see(tk.END)
    
    def clear_alerts(self):
        self.alerts_text.delete(1.0, tk.END)
    
    def export_logs(self):
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
                messagebox.showinfo("Success", f"Exported {len(self.all_logs)} logs")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def clear_logs(self):
        if messagebox.askyesno("Confirm", "Clear all logs?"):
            self.all_logs.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)
    
    def clear_cache(self):
        if messagebox.askyesno("Confirm", "Clear DNS cache?"):
            self.dns_cache.cache.clear()
            messagebox.showinfo("Success", "DNS cache cleared")
    
    def show_cache_stats(self):
        stats = self.dns_cache.get_stats()
        msg = f"""DNS Cache Statistics:
        
Cache Size: {stats['size']} entries
Cache Hits: {stats['hits']:,}
Cache Misses: {stats['misses']:,}
Hit Rate: {stats['hit_rate']:.1f}%

A higher hit rate means better performance!"""
        messagebox.showinfo("Cache Statistics", msg)
    
    def toggle_pause(self):
        self.paused = not self.paused
        status = "PAUSED" if self.paused else "Running"
        messagebox.showinfo("Status", f"Logging {status}")
    
    def show_about(self):
        about_text = """DNS Network Activity Monitor v2.0
Final Year Cybersecurity Project

Features:
• Real-time DNS query monitoring
• DNS caching for improved performance
• Blocklist/Allowlist management
• Anomaly detection & security alerts
• Traffic analysis & statistics
• CSV export capabilities

This tool helps monitor network activity,
block unwanted domains, and detect potential
security threats in real-time."""
        
        messagebox.showinfo("About", about_text)
    
    def run(self):
        self.root.mainloop()

def create_gui(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector):
    app = DNSMonitorGUI(log_queue, all_logs, stats_tracker, dns_cache, blocklist, anomaly_detector)
    app.run()