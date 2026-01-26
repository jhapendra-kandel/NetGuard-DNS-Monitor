# stats.py
from collections import Counter
import datetime

def compute_stats(all_logs):
    if not all_logs:
        return "No data yet. Start querying DNS!"
    
    total_queries = len(all_logs)
    blocked = sum(1 for log in all_logs if log[-1] in ['blocked_ip', 'blocked_domain'])
    safe = sum(1 for log in all_logs if log[-1] == 'safe')
    failed = sum(1 for log in all_logs if log[-1] == 'failed')
    
    # Top domains
    domain_counter = Counter(log[2] for log in all_logs)
    top_domains = domain_counter.most_common(5)
    
    # Top IPs
    ip_counter = Counter(log[1] for log in all_logs)
    top_ips = ip_counter.most_common(5)
    
    # Query types
    type_counter = Counter(log[3] for log in all_logs)
    
    stats_text = f"""
=== DNS Query Statistics ===

Total Queries: {total_queries}
Safe Queries: {safe}
Blocked Queries: {blocked}
Failed Queries: {failed}

Top 5 Domains:
"""
    for domain, count in top_domains:
        stats_text += f"  {domain}: {count}\n"
    
    stats_text += "\nTop 5 Source IPs:\n"
    for ip, count in top_ips:
        stats_text += f"  {ip}: {count}\n"
    
    stats_text += "\nQuery Types:\n"
    for qtype, count in type_counter.items():
        stats_text += f"  {qtype}: {count}\n"
    
    return stats_text