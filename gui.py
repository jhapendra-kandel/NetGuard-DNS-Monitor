# gui.py
"""
GUI Module
Tkinter-based interface for live logs, statistics, and blocklist management.
"""
import tkinter as tk
from tkinter import ttk
import queue
from stats import compute_stats, create_bar_chart
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def update_logs(tree, log_queue):
    try:
        while True:
            log = log_queue.get_nowait()
            # Insert at index 0 to add new logs to the top
            iid = tree.insert('', 0, values=log[:-1])  # Exclude status from display
            status = log[-1]
            if status == 'safe':
                tree.item(iid, tags=('safe',))
            else:
                tree.item(iid, tags=('malicious',))
    except queue.Empty:
        pass

def update_gui(root, tree, log_queue, all_logs, stats_frame, domain_listbox, ip_listbox, domain_blocklist, ip_blacklist):
    update_logs(tree, log_queue)
    # Update stats every 5 seconds (but for simplicity, update on poll)
    root.after(5000, update_stats, stats_frame, all_logs)
    # Refresh blocklists
    domain_listbox.delete(0, tk.END)
    for domain in domain_blocklist:
        domain_listbox.insert(tk.END, domain)
    ip_listbox.delete(0, tk.END)
    for ip in ip_blacklist:
        ip_listbox.insert(tk.END, ip)
    root.after(100, update_gui, root, tree, log_queue, all_logs, stats_frame, domain_listbox, ip_listbox, domain_blocklist, ip_blacklist)

def update_stats(stats_frame, all_logs):
    # Clear existing widgets
    for widget in stats_frame.winfo_children():
        widget.destroy()
    
    stats_text = compute_stats(all_logs)
    text_widget = tk.Text(stats_frame, wrap='word', height=10)
    text_widget.insert(tk.END, stats_text)
    text_widget.pack(expand=True, fill='x')
    
    # Add bar charts
    if all_logs:
        # Top IPs chart
        ip_fig = create_bar_chart(all_logs, 'ip')
        ip_canvas = FigureCanvasTkAgg(ip_fig, master=stats_frame)
        ip_canvas.draw()
        ip_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # Top Domains chart
        domain_fig = create_bar_chart(all_logs, 'domain')
        domain_canvas = FigureCanvasTkAgg(domain_fig, master=stats_frame)
        domain_canvas.draw()
        domain_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def add_domain(entry, listbox, blocklist):
    domain = entry.get().strip()
    if domain and domain not in blocklist:
        blocklist.append(domain)
        listbox.insert(tk.END, domain)
    entry.delete(0, tk.END)

def remove_domain(listbox, blocklist):
    selected = listbox.curselection()
    if selected:
        domain = listbox.get(selected[0])
        blocklist.remove(domain)
        listbox.delete(selected[0])

def add_ip(entry, listbox, blocklist):
    ip = entry.get().strip()
    if ip and ip not in blocklist:
        blocklist.append(ip)
        listbox.insert(tk.END, ip)
    entry.delete(0, tk.END)

def remove_ip(listbox, blocklist):
    selected = listbox.curselection()
    if selected:
        ip = listbox.get(selected[0])
        blocklist.remove(ip)
        listbox.delete(selected[0])

def create_gui(log_queue, all_logs, domain_blocklist, ip_blacklist):
    root = tk.Tk()
    root.title("DNS Network Activity Monitor")
    root.geometry("1000x800")

    # Notebook for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    # Status bar with live counters
    status_bar = tk.Label(root, text="Queries: 0 | Blocked: 0 | Safe: 0", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status_bar():
        total = len(all_logs)
        blocked = sum(1 for log in all_logs if log[-1] in ['blocked_ip', 'blocked_domain'])
        safe = sum(1 for log in all_logs if log[-1] == 'safe')
        status_bar.config(text=f"Queries: {total} | Blocked: {blocked} | Safe: {safe}")
        root.after(3000, update_status_bar)  # Update every 3 seconds

    update_status_bar()

    # Logs Tab
    logs_frame = ttk.Frame(notebook)
    notebook.add(logs_frame, text='Live Logs')

    tree = ttk.Treeview(logs_frame, columns=('Timestamp', 'Source IP', 'Query Domain', 'Type', 'Details'), show='headings')
    tree.heading('Timestamp', text='Timestamp')
    tree.heading('Source IP', text='Source IP')
    tree.heading('Query Domain', text='Query Domain')
    tree.heading('Type', text='Type')
    tree.heading('Details', text='Details')
    tree.pack(expand=True, fill='both')

        # Pause/Resume functionality
    paused = [False]  # Mutable for nonlocal access

    def toggle_pause():
        paused[0] = not paused[0]
        pause_btn.config(text="Resume Logs" if paused[0] else "Pause Logs")
        status = "PAUSED" if paused[0] else "Running"
        messagebox.showinfo("Logging Status", f"Logging is now {status}")

    pause_btn = ttk.Button(logs_frame, text="Pause Logs", command=toggle_pause)
    pause_btn.pack(pady=5, padx=10)

    # Modify update_logs to respect pause
    # Add at the very top of update_logs function:
    if paused[0]:
        return

    # Color tags
    tree.tag_configure('safe', background='lightgreen')
    tree.tag_configure('malicious', background='lightcoral')

    # Stats Tab
    stats_frame = ttk.Frame(notebook)
    notebook.add(stats_frame, text='Statistics')
    update_stats(stats_frame, all_logs)  # Initial update

    # Blocklists Tab
    block_frame = ttk.Frame(notebook)
    notebook.add(block_frame, text='Blocklists')

    # Domain Blocklist Section
    domain_label = tk.Label(block_frame, text="Domain Blocklist (e.g., example.com or sub.example.com)")
    domain_label.pack()
    domain_entry = tk.Entry(block_frame)
    domain_entry.pack()
    add_domain_btn = tk.Button(block_frame, text="Add Domain", command=lambda: add_domain(domain_entry, domain_listbox, domain_blocklist))
    add_domain_btn.pack()
    domain_listbox = tk.Listbox(block_frame, height=10)
    domain_listbox.pack()
    remove_domain_btn = tk.Button(block_frame, text="Remove Selected Domain", command=lambda: remove_domain(domain_listbox, domain_blocklist))
    remove_domain_btn.pack()

    # IP Blacklist Section
    ip_label = tk.Label(block_frame, text="IP Blacklist (Block all DNS from this IP)")
    ip_label.pack()
    ip_entry = tk.Entry(block_frame)
    ip_entry.pack()
    add_ip_btn = tk.Button(block_frame, text="Add IP", command=lambda: add_ip(ip_entry, ip_listbox, ip_blacklist))
    add_ip_btn.pack()
    ip_listbox = tk.Listbox(block_frame, height=10)
    ip_listbox.pack()
    remove_ip_btn = tk.Button(block_frame, text="Remove Selected IP", command=lambda: remove_ip(ip_listbox, ip_blacklist))
    remove_ip_btn.pack()

    # Start GUI updater
    root.after(100, update_gui, root, tree, log_queue, all_logs, stats_frame, domain_listbox, ip_listbox, domain_blocklist, ip_blacklist)

    root.mainloop()