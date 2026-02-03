# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import queue
import csv
from stats import compute_stats
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import datetime
import os

def create_bar_chart(all_logs, chart_type='ip'):
    """Create bar charts for visualization"""
    if chart_type == 'ip':
        counter = Counter(log[1] for log in all_logs)
        title = 'Top 10 Active IPs'
        xlabel = 'Source IPs'
        color = 'skyblue'
    elif chart_type == 'domain':
        counter = Counter(log[2] for log in all_logs)
        title = 'Top 10 Requested Domains'
        xlabel = 'Domains'
        color = 'lightcoral'
    elif chart_type == 'status':
        status_map = {
            'safe': 'Safe',
            'blocked_domain': 'Blocked Domain',
            'blocked_ip': 'Blocked IP',
            'failed': 'Failed'
        }
        counter = Counter(status_map.get(log[5], 'Other') for log in all_logs)
        title = 'Query Status Distribution'
        xlabel = 'Status'
        color = 'lightgreen'
    else:
        return None

    top_items = counter.most_common(10)
    if not top_items:
        return None

    labels, values = zip(*top_items)
    
    # Truncate long labels
    labels = [label[:20] + '...' if len(label) > 20 else label for label in labels]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=color, edgecolor='black', alpha=0.7)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=9)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    return fig

def update_logs(tree, log_queue, paused):
    """Update log display from queue"""
    if paused[0]:
        return
    try:
        while True:
            log = log_queue.get_nowait()
            iid = tree.insert('', 0, values=log[:-1])
            status = log[-1]
            if status in ['blocked_ip', 'blocked_domain']:
                tree.item(iid, tags=('malicious',))
            elif status == 'safe':
                tree.item(iid, tags=('safe',))
            elif status == 'failed':
                tree.item(iid, tags=('failed',))
    except queue.Empty:
        pass

def update_gui(root, tree, log_queue, all_logs, stats_frame, domain_listbox, ip_listbox, 
               domain_blocklist, ip_blacklist, paused, notebook):
    """Main GUI update loop"""
    update_logs(tree, log_queue, paused)
    
    # Update blocklists display
    domain_listbox.delete(0, tk.END)
    for domain in domain_blocklist:
        domain_listbox.insert(tk.END, domain)
    
    ip_listbox.delete(0, tk.END)
    for ip in ip_blacklist:
        ip_listbox.insert(tk.END, ip)
    
    # Auto-refresh stats when stats tab is selected
    current_tab = notebook.index(notebook.select())
    if current_tab == 1:  # Stats tab (index 1)
        update_stats(stats_frame, all_logs)
    
    root.after(100, update_gui, root, tree, log_queue, all_logs, stats_frame, 
               domain_listbox, ip_listbox, domain_blocklist, ip_blacklist, paused, notebook)

def update_stats(stats_frame, all_logs):
    """Update statistics display with charts"""
    # Clear previous widgets
    for widget in stats_frame.winfo_children():
        widget.destroy()
    
    # Create scrollable frame for stats
    canvas = tk.Canvas(stats_frame)
    scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Add text statistics
    stats_text = compute_stats(all_logs)
    text_widget = tk.Text(scrollable_frame, wrap='word', height=25, width=80, 
                          font=('Courier', 10), bg='#f0f0f0')
    text_widget.insert(tk.END, stats_text)
    text_widget.config(state='disabled')
    text_widget.pack(pady=10, padx=10)
    
    # Add charts if there are logs
    if all_logs:
        # Status distribution pie chart
        status_fig = create_bar_chart(all_logs, 'status')
        if status_fig:
            status_canvas = FigureCanvasTkAgg(status_fig, master=scrollable_frame)
            status_canvas.draw()
            status_canvas.get_tk_widget().pack(pady=10, padx=10)
        
        # Top IPs chart
        ip_fig = create_bar_chart(all_logs, 'ip')
        if ip_fig:
            ip_canvas = FigureCanvasTkAgg(ip_fig, master=scrollable_frame)
            ip_canvas.draw()
            ip_canvas.get_tk_widget().pack(pady=10, padx=10)
        
        # Top domains chart
        domain_fig = create_bar_chart(all_logs, 'domain')
        if domain_fig:
            domain_canvas = FigureCanvasTkAgg(domain_fig, master=scrollable_frame)
            domain_canvas.draw()
            domain_canvas.get_tk_widget().pack(pady=10, padx=10)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def save_blocklists(domain_blocklist, ip_blacklist):
    """Save blocklists to files"""
    try:
        with open('domain_blocklist.txt', 'w') as f:
            for domain in domain_blocklist:
                f.write(f"{domain}\n")
        
        with open('ip_blacklist.txt', 'w') as f:
            for ip in ip_blacklist:
                f.write(f"{ip}\n")
        
        return True
    except Exception as e:
        print(f"Error saving blocklists: {e}")
        return False

def load_blocklists(domain_blocklist, ip_blacklist):
    """Load blocklists from files"""
    try:
        if os.path.exists('domain_blocklist.txt'):
            with open('domain_blocklist.txt', 'r') as f:
                for line in f:
                    domain = line.strip()
                    if domain and domain not in domain_blocklist:
                        domain_blocklist.append(domain)
        
        if os.path.exists('ip_blacklist.txt'):
            with open('ip_blacklist.txt', 'r') as f:
                for line in f:
                    ip = line.strip()
                    if ip and ip not in ip_blacklist:
                        ip_blacklist.append(ip)
        
        print(f"Loaded {len(domain_blocklist)} domains and {len(ip_blacklist)} IPs")
        return True
    except Exception as e:
        print(f"Error loading blocklists: {e}")
        return False

def add_domain(entry, listbox, blocklist):
    """Add domain to blocklist"""
    domain = entry.get().strip().lower()
    if domain and domain not in blocklist:
        blocklist.append(domain)
        listbox.insert(tk.END, domain)
        save_blocklists(blocklist, [])  # Save after adding
        messagebox.showinfo("Success", f"Added domain: {domain}")
    elif domain in blocklist:
        messagebox.showwarning("Duplicate", f"Domain already in blocklist: {domain}")
    entry.delete(0, tk.END)

def remove_domain(listbox, blocklist):
    """Remove domain from blocklist"""
    selected = listbox.curselection()
    if selected:
        domain = listbox.get(selected[0])
        blocklist.remove(domain)
        listbox.delete(selected[0])
        save_blocklists(blocklist, [])  # Save after removing
        messagebox.showinfo("Removed", f"Removed domain: {domain}")

def add_ip(entry, listbox, blocklist):
    """Add IP to blacklist"""
    ip = entry.get().strip()
    if ip and ip not in blocklist:
        # Basic IP validation
        parts = ip.split('.')
        if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            blocklist.append(ip)
            listbox.insert(tk.END, ip)
            save_blocklists([], blocklist)  # Save after adding
            messagebox.showinfo("Success", f"Added IP: {ip}")
        else:
            messagebox.showerror("Invalid IP", "Please enter a valid IPv4 address")
    elif ip in blocklist:
        messagebox.showwarning("Duplicate", f"IP already in blacklist: {ip}")
    entry.delete(0, tk.END)

def remove_ip(listbox, blocklist):
    """Remove IP from blacklist"""
    selected = listbox.curselection()
    if selected:
        ip = listbox.get(selected[0])
        blocklist.remove(ip)
        listbox.delete(selected[0])
        save_blocklists([], blocklist)  # Save after removing
        messagebox.showinfo("Removed", f"Removed IP: {ip}")

def import_domain_list(listbox, blocklist):
    """Import domains from file"""
    file = filedialog.askopenfilename(
        title="Select Domain List File",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if file:
        try:
            count = 0
            with open(file, 'r') as f:
                for line in f:
                    domain = line.strip().lower()
                    if domain and not domain.startswith('#') and domain not in blocklist:
                        blocklist.append(domain)
                        count += 1
            
            # Refresh listbox
            listbox.delete(0, tk.END)
            for domain in blocklist:
                listbox.insert(tk.END, domain)
            
            save_blocklists(blocklist, [])
            messagebox.showinfo("Success", f"Imported {count} domains")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import: {e}")

def export_logs(all_logs):
    """Export logs to CSV"""
    if not all_logs:
        messagebox.showinfo("No Data", "No logs to export yet.")
        return
    
    file = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if file:
        try:
            with open(file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Source IP', 'Query Domain', 'Type', 'Details', 'Status'])
                writer.writerows(all_logs)
            messagebox.showinfo("Success", f"Exported {len(all_logs)} logs to {file}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

def clear_logs(all_logs, tree):
    """Clear all logs"""
    if messagebox.askyesno("Confirm", "Clear all logs? This cannot be undone."):
        all_logs.clear()
        for item in tree.get_children():
            tree.delete(item)
        messagebox.showinfo("Cleared", "All logs cleared")

def create_gui(log_queue, all_logs, domain_blocklist, ip_blacklist):
    """Create main GUI"""
    root = tk.Tk()
    root.title("NetGuard DNS Monitor v1.0.0 - Network Security Dashboard")
    root.geometry("1200x900")
    
    # Load saved blocklists
    load_blocklists(domain_blocklist, ip_blacklist)
    
    # Create main notebook
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both', padx=5, pady=5)
    
    # ========== TAB 1: LIVE LOGS ==========
    logs_frame = ttk.Frame(notebook)
    notebook.add(logs_frame, text='📝 Live Logs')
    
    # Controls frame
    controls_frame = ttk.Frame(logs_frame)
    controls_frame.pack(fill='x', pady=5)
    
    # Treeview for logs
    tree_frame = ttk.Frame(logs_frame)
    tree_frame.pack(expand=True, fill='both', padx=5, pady=5)
    
    # Scrollbars
    tree_scroll_y = ttk.Scrollbar(tree_frame, orient='vertical')
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
    
    tree = ttk.Treeview(
        tree_frame,
        columns=('Timestamp', 'Source IP', 'Query Domain', 'Type', 'Details'),
        show='headings',
        yscrollcommand=tree_scroll_y.set,
        xscrollcommand=tree_scroll_x.set
    )
    
    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)
    
    # Column configuration
    tree.heading('Timestamp', text='Timestamp')
    tree.heading('Source IP', text='Source IP')
    tree.heading('Query Domain', text='Query Domain')
    tree.heading('Type', text='Type')
    tree.heading('Details', text='Details')
    
    tree.column('Timestamp', width=150)
    tree.column('Source IP', width=120)
    tree.column('Query Domain', width=300)
    tree.column('Type', width=80)
    tree.column('Details', width=200)
    
    tree.pack(side='left', expand=True, fill='both')
    tree_scroll_y.pack(side='right', fill='y')
    tree_scroll_x.pack(side='bottom', fill='x')
    
    # Tag colors
    tree.tag_configure('safe', background='#90EE90')
    tree.tag_configure('malicious', background='#FFB6C1')
    tree.tag_configure('failed', background='#FFE4B5')
    
    paused = [False]
    
    def toggle_pause():
        paused[0] = not paused[0]
        pause_btn.config(
            text="▶️ Resume Logs" if paused[0] else "⏸️ Pause Logs",
            style='Accent.TButton' if paused[0] else 'TButton'
        )
    
    # Control buttons
    pause_btn = ttk.Button(controls_frame, text="⏸️ Pause Logs", command=toggle_pause)
    pause_btn.pack(side='left', padx=5)
    
    export_btn = ttk.Button(controls_frame, text="💾 Export to CSV", 
                            command=lambda: export_logs(all_logs))
    export_btn.pack(side='left', padx=5)
    
    clear_btn = ttk.Button(controls_frame, text="🗑️ Clear Logs", 
                           command=lambda: clear_logs(all_logs, tree))
    clear_btn.pack(side='left', padx=5)
    
    # ========== TAB 2: STATISTICS ==========
    stats_frame = ttk.Frame(notebook)
    notebook.add(stats_frame, text='📊 Statistics')
    
    # Refresh button for stats
    refresh_stats_btn = ttk.Button(stats_frame, text="🔄 Refresh Statistics",
                                    command=lambda: update_stats(stats_frame, all_logs))
    refresh_stats_btn.pack(pady=5)
    
    # ========== TAB 3: BLOCKLISTS ==========
    block_frame = ttk.Frame(notebook)
    notebook.add(block_frame, text='🛡️ Blocklists')
    
    # Create two columns
    left_block_frame = ttk.Frame(block_frame)
    left_block_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
    
    right_block_frame = ttk.Frame(block_frame)
    right_block_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
    
    # Domain Blocklist Section
    domain_label = tk.Label(left_block_frame, text="🌐 Domain Blocklist", 
                            font=('Arial', 12, 'bold'))
    domain_label.pack(pady=5)
    
    domain_entry_frame = ttk.Frame(left_block_frame)
    domain_entry_frame.pack(fill='x', pady=5)
    
    domain_entry = tk.Entry(domain_entry_frame, width=30)
    domain_entry.pack(side='left', padx=5)
    
    add_domain_btn = ttk.Button(domain_entry_frame, text="➕ Add", 
                                command=lambda: add_domain(domain_entry, domain_listbox, domain_blocklist))
    add_domain_btn.pack(side='left', padx=2)
    
    import_domain_btn = ttk.Button(domain_entry_frame, text="📁 Import", 
                                   command=lambda: import_domain_list(domain_listbox, domain_blocklist))
    import_domain_btn.pack(side='left', padx=2)
    
    domain_scroll = ttk.Scrollbar(left_block_frame)
    domain_scroll.pack(side='right', fill='y')
    
    domain_listbox = tk.Listbox(left_block_frame, height=20, yscrollcommand=domain_scroll.set)
    domain_listbox.pack(fill='both', expand=True)
    domain_scroll.config(command=domain_listbox.yview)
    
    remove_domain_btn = ttk.Button(left_block_frame, text="❌ Remove Selected", 
                                   command=lambda: remove_domain(domain_listbox, domain_blocklist))
    remove_domain_btn.pack(pady=5)
    
    domain_count_label = tk.Label(left_block_frame, text="Total: 0 domains")
    domain_count_label.pack()
    
    # IP Blacklist Section
    ip_label = tk.Label(right_block_frame, text="🚫 IP Blacklist", 
                       font=('Arial', 12, 'bold'))
    ip_label.pack(pady=5)
    
    ip_entry_frame = ttk.Frame(right_block_frame)
    ip_entry_frame.pack(fill='x', pady=5)
    
    ip_entry = tk.Entry(ip_entry_frame, width=30)
    ip_entry.pack(side='left', padx=5)
    
    add_ip_btn = ttk.Button(ip_entry_frame, text="➕ Add", 
                           command=lambda: add_ip(ip_entry, ip_listbox, ip_blacklist))
    add_ip_btn.pack(side='left', padx=2)
    
    ip_scroll = ttk.Scrollbar(right_block_frame)
    ip_scroll.pack(side='right', fill='y')
    
    ip_listbox = tk.Listbox(right_block_frame, height=20, yscrollcommand=ip_scroll.set)
    ip_listbox.pack(fill='both', expand=True)
    ip_scroll.config(command=ip_listbox.yview)
    
    remove_ip_btn = ttk.Button(right_block_frame, text="❌ Remove Selected", 
                               command=lambda: remove_ip(ip_listbox, ip_blacklist))
    remove_ip_btn.pack(pady=5)
    
    ip_count_label = tk.Label(right_block_frame, text="Total: 0 IPs")
    ip_count_label.pack()
    
    # ========== STATUS BAR ==========
    status_bar = tk.Label(root, text="📡 Queries: 0 | 🛡️ Blocked: 0 | ⚡ Cache Hits: 0", 
                         bd=1, relief=tk.SUNKEN, anchor=tk.W, font=('Arial', 10))
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status_bar():
        total = len(all_logs)
        blocked = sum(1 for log in all_logs if log[-1] in ['blocked_ip', 'blocked_domain'])
        cached = sum(1 for log in all_logs if 'cached' in log[4].lower())
        
        domain_count_label.config(text=f"Total: {len(domain_blocklist)} domains")
        ip_count_label.config(text=f"Total: {len(ip_blacklist)} IPs")
        
        status_bar.config(
            text=f"📡 Queries: {total:,} | 🛡️ Blocked: {blocked:,} | ⚡ Cache: {cached:,} | "
                 f"🌐 Blocklist: {len(domain_blocklist)} | 🚫 IP Blacklist: {len(ip_blacklist)}"
        )
        root.after(2000, update_status_bar)
    
    update_status_bar()
    
    # Start GUI update loop
    root.after(100, update_gui, root, tree, log_queue, all_logs, stats_frame, 
               domain_listbox, ip_listbox, domain_blocklist, ip_blacklist, paused, notebook)
    
    # Save blocklists on exit
    def on_closing():
        save_blocklists(domain_blocklist, ip_blacklist)
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
    #test