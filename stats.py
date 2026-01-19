"""
Statistics Module
Computes and formats DNS query statistics for display.
"""
from collections import Counter
import datetime

def compute_stats(all_logs):
    if not all_logs:
        return "No data yet."

    total_queries = len(all_logs)
    start_time = all_logs[0][0] if all_logs else 'N/A'
    end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # -----------------------------
    # Success / Blocked / Failed
    # -----------------------------
    successful = sum(
        1 for log in all_logs
        if 'OK' in log[4] or 'cached' in log[4].lower()
    )
    blocked = sum(
        1 for log in all_logs
        if 'Blocked' in log[4]
    )
    failed = total_queries - successful - blocked

    # Avoid division by zero (safety)
    if total_queries > 0:
        success_pct = successful / total_queries * 100
        blocked_pct = blocked / total_queries * 100
        failed_pct = failed / total_queries * 100
    else:
        success_pct = blocked_pct = failed_pct = 0.0

    # -----------------------------
    # Counters
    # -----------------------------
    ip_counter = Counter(log[1] for log in all_logs)      # log[1] = source IP
    top_ips = ip_counter.most_common(5)

    domain_counter = Counter(log[2] for log in all_logs)  # log[2] = domain
    top_domains = domain_counter.most_common(5)

    type_counter = Counter(log[3] for log in all_logs)    # log[3] = query type

    # -----------------------------
    # Build stats string
    # -----------------------------
    stats_str = f"Total DNS Queries: {total_queries}\n"
    stats_str += f"Time Range: {start_time} to {end_time}\n\n"

    stats_str += f"Success: {successful} ({success_pct:.1f}%)\n"
    stats_str += f"Blocked: {blocked} ({blocked_pct:.1f}%)\n"
    stats_str += f"Failed/Other: {failed} ({failed_pct:.1f}%)\n\n"

    stats_str += "Top Active IPs (Most Network Use):\n"
    for ip, count in top_ips:
        stats_str += f"- {ip}: {count} queries\n"

    stats_str += "\nTop Requested Domains/Apps:\n"
    for domain, count in top_domains:
        stats_str += f"- {domain}: {count} requests\n"

    stats_str += "\nQuery Type Distribution:\n"
    for qtype, count in type_counter.items():
        stats_str += f"- {qtype}: {count}\n"

    return stats_str
