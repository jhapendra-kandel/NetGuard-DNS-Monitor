import tkinter as tk
from tkinter import ttk
import queue
import threading
from stats import compute_stats

def update_logs(tree, log_queue):
    try:
        while True:
            log = log_queue.get_nowait()
            tree.insert('', 'end', values=log)
    except queue.Empty:
        pass

def update_gui(root, tree, log_queue, all_logs, stats_text):
    update_logs(tree, log_queue)
    # Update stats every 5 seconds
    stats = compute_stats(all_logs)
    stats_text.config(state='normal')
    stats_text.delete(1.0, tk.END)
    stats_text.insert(tk.END, stats)
    stats_text.config(state='disabled')
    root.after(100, update_gui, root, tree, log_queue, all_logs, stats_text)  # Poll every 100ms for logs, stats less often

def create_gui(log_queue, all_logs):
    root = tk.Tk()
    root.title("DNS Network Activity Monitor")
    root.geometry("800x600")

    # Notebook for tabs
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

    # Stats Tab
    stats_frame = ttk.Frame(notebook)
    notebook.add(stats_frame, text='Statistics')

    stats_text = tk.Text(stats_frame, wrap='word', state='disabled')
    stats_text.pack(expand=True, fill='both')

    # Start GUI updater in a thread-like manner via after
    root.after(100, update_gui, root, tree, log_queue, all_logs, stats_text)

    root.mainloop()