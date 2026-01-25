# gui.py - Full fixed version with all errors resolved
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import queue
import csv
from stats import compute_stats
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import datetime  # Fixed: import datetime for time checks

def create_bar_chart(all_logs, chart_type='ip'):
    """Create bar chart for stats"""
    if chart_type == 'ip':
        counter = Counter(log[1] for log in all_logs)  # source IP
        title = 'Top Active IPs'
        xlabel = 'IPs'
    elif chart_type == 'domain':
        counter = Counter(log[2] for log in all_logs)  # query domain
        title = 'Top Requested Domains'
        xlabel = 'Domains'
    else:
        return None

    top_items = counter.most_common(5)
    if not top_items:
        return None

    labels, values = zip(*top_items)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, values, color='skyblue')
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Count')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()

    return fig

def update_logs(tree, log_queue, paused):
    if paused[0]:
        return
    try:
        while True:
            log = log_queue.get_nowait()
            iid = tree.insert('', 0, values=log[:-1])  # Exclude status
            status = log[-1]
            if status in ['blocked_ip', 'blocked_domain']:
                tree.item(iid, tags=('malicious',))
            elif status == 'safe':
                tree.item(iid, tags=('safe',))
    except queue.Empty:
        pass

def update_gui(root, tree, log_queue, all_logs, stats_frame, domain_listbox, ip_listbox, domain_blocklist, ip_blacklist, paused):
    update_logs(tree, log_queue, paused)
    # Refresh blocklists
    domain_listbox.delete(0, tk.END)
    for domain in domain_blocklist:
        domain_listbox.insert(tk.END, domain)
    ip_listbox.delete(0, tk.END)
    for ip in ip_blacklist:
        ip_listbox.insert(tk.END, ip)
    root.after(100, update_gui, root, tree, log_queue, all_logs, stats_frame, domain_listbox, ip_listbox, domain_blocklist, ip_blacklist, paused)

def update_stats(stats_frame, all_logs):
    for widget in stats_frame.winfo_children():
        widget.destroy()
    stats_text = compute_stats(all_logs)
    text_widget = tk.Text(stats_frame, wrap='word', height=10)
    text_widget.insert(tk.END, stats_text)
    text_widget.config(state='disabled')
    text_widget.pack(expand=True, fill='x')
    # Bar charts
    if all_logs:
        ip_fig = create_bar_chart(all_logs, 'ip')
        if ip_fig:
            ip_canvas = FigureCanvasTkAgg(ip_fig, master=stats_frame)
            ip_canvas.draw()
            ip_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        domain_fig = create_bar_chart(all_logs, 'domain')
        if domain_fig:
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

def export_logs(all_logs):
    if not all_logs:
        messagebox.showinfo("No Data", "No logs to export yet.")
        return
    file = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Export DNS Logs"
    )
    if file:
        with open(file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Source IP', 'Query Domain', 'Type', 'Details', 'Status'])
            writer.writerows(all_logs)
        messagebox.showinfo("Success", f"Exported {len(all_logs)} logs to {file}")

def clear_logs(all_logs, tree):
    if messagebox.askyesno("Confirm", "Clear all logs?"):
        all_logs.clear()
        for item in tree.get_children():
            tree.delete(item)
        messagebox.showinfo("Cleared", "All logs cleared.")

def create_gui(log_queue, all_logs, domain_blocklist, ip_blacklist):

    import subprocess

    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
    except:
        branch = "unknown"

    root.title(f"DNS Network Activity Monitor - v1.0.0 (branch: {branch})")

    root = tk.Tk()
    root.title("DNS Network Activity Monitor")
    root.geometry("1000x800")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

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

    tree.tag_configure('safe', background='lightgreen')
    tree.tag_configure('malicious', background='lightcoral')

    # Pause / Export / Clear
    paused = [False]

    def toggle_pause():
        paused[0] = not paused[0]
        pause_btn.config(text="Resume Logs" if paused[0] else "Pause Logs")

    pause_btn = ttk.Button(logs_frame, text="Pause Logs", command=toggle_pause)
    pause_btn.pack(pady=5, padx=10)

    export_btn = ttk.Button(logs_frame, text="Export Logs to CSV", command=lambda: export_logs(all_logs))
    export_btn.pack(pady=5, padx=10)

    clear_btn = ttk.Button(logs_frame, text="Clear Logs", command=lambda: clear_logs(all_logs, tree))
    clear_btn.pack(pady=5, padx=10)

    # Stats Tab
    stats_frame = ttk.Frame(notebook)
    notebook.add(stats_frame, text='Statistics')

    # Blocklists Tab
    block_frame = ttk.Frame(notebook)
    notebook.add(block_frame, text='Blocklists')

    domain_label = tk.Label(block_frame, text="Domain Blocklist")
    domain_label.pack()
    domain_entry = tk.Entry(block_frame)
    domain_entry.pack()
    add_domain_btn = tk.Button(block_frame, text="Add Domain", command=lambda: add_domain(domain_entry, domain_listbox, domain_blocklist))
    add_domain_btn.pack()
    domain_listbox = tk.Listbox(block_frame, height=10)
    domain_listbox.pack()
    remove_domain_btn = tk.Button(block_frame, text="Remove Selected", command=lambda: remove_domain(domain_listbox, domain_blocklist))
    remove_domain_btn.pack()

    ip_label = tk.Label(block_frame, text="IP Blacklist")
    ip_label.pack()
    ip_entry = tk.Entry(block_frame)
    ip_entry.pack()
    add_ip_btn = tk.Button(block_frame, text="Add IP", command=lambda: add_ip(ip_entry, ip_listbox, ip_blacklist))
    add_ip_btn.pack()
    ip_listbox = tk.Listbox(block_frame, height=10)
    ip_listbox.pack()
    remove_ip_btn = tk.Button(block_frame, text="Remove Selected", command=lambda: remove_ip(ip_listbox, ip_blacklist))
    remove_ip_btn.pack()

    # Status bar
    status_bar = tk.Label(root, text="Queries: 0 | Blocked: 0", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status_bar():
        total = len(all_logs)
        blocked = sum(1 for log in all_logs if log[-1] in ['blocked_ip', 'blocked_domain'])
        status_bar.config(text=f"Queries: {total} | Blocked: {blocked}")
        root.after(3000, update_status_bar)

    update_status_bar()

    # Start updater
    root.after(100, update_gui, root, tree, log_queue, all_logs, stats_frame, domain_listbox, ip_listbox, domain_blocklist, ip_blacklist, paused)

    root.mainloop()