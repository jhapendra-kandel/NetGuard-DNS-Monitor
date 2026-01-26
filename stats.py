"""
Statistics Module
Computes and formats DNS query statistics for display.
Enhanced version with comprehensive network monitoring metrics.
"""
from collections import Counter
import datetime

def compute_stats(all_logs):
    """
    Compute comprehensive DNS statistics from log entries.
    
    Log format: (timestamp, src_ip, query_name, query_type, details, status)
    Status values: 'safe', 'blocked_ip', 'blocked_domain', 'failed'
    """
    if not all_logs:
        return "No data yet. Start monitoring DNS queries!"
    
    total_queries = len(all_logs)
    start_time = all_logs[0][0] if all_logs else 'N/A'
    end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # -----------------------------
    # Enhanced Status Categorization
    # -----------------------------
    safe_queries = sum(1 for log in all_logs if log[5] == 'safe')
    blocked_domain = sum(1 for log in all_logs if log[5] == 'blocked_domain')
    blocked_ip = sum(1 for log in all_logs if log[5] == 'blocked_ip')
    failed_queries = sum(1 for log in all_logs if log[5] == 'failed')
    cached_queries = sum(1 for log in all_logs if 'cached' in log[4].lower())
    
    total_blocked = blocked_domain + blocked_ip
    
    # Calculate percentages (safety check)
    if total_queries > 0:
        safe_pct = (safe_queries / total_queries) * 100
        blocked_pct = (total_blocked / total_queries) * 100
        failed_pct = (failed_queries / total_queries) * 100
        cached_pct = (cached_queries / total_queries) * 100
    else:
        safe_pct = blocked_pct = failed_pct = cached_pct = 0.0
    
    # -----------------------------
    # Network Activity Counters
    # -----------------------------
    ip_counter = Counter(log[1] for log in all_logs)      # log[1] = source IP
    top_ips = ip_counter.most_common(10)
    
    domain_counter = Counter(log[2] for log in all_logs)  # log[2] = domain
    top_domains = domain_counter.most_common(10)
    
    type_counter = Counter(log[3] for log in all_logs)    # log[3] = query type
    
    # -----------------------------
    # Blocked Domains & IPs Analysis
    # -----------------------------
    blocked_domains_list = [log[2] for log in all_logs if log[5] == 'blocked_domain']
    blocked_ips_list = [log[1] for log in all_logs if log[5] == 'blocked_ip']
    
    blocked_domain_counter = Counter(blocked_domains_list)
    blocked_ip_counter = Counter(blocked_ips_list)
    
    top_blocked_domains = blocked_domain_counter.most_common(5)
    top_blocked_ips = blocked_ip_counter.most_common(5)
    
    # -----------------------------
    # Time-based Analysis
    # -----------------------------
    try:
        if len(all_logs) > 1:
            first_time = datetime.datetime.strptime(all_logs[0][0], '%Y-%m-%d %H:%M:%S')
            last_time = datetime.datetime.strptime(all_logs[-1][0], '%Y-%m-%d %H:%M:%S')
            duration = (last_time - first_time).total_seconds()
            if duration > 0:
                qps = total_queries / duration  # Queries per second
            else:
                qps = 0
        else:
            qps = 0
    except:
        qps = 0
    
    # -----------------------------
    # Unique counts
    # -----------------------------
    unique_ips = len(ip_counter)
    unique_domains = len(domain_counter)
    
    # -----------------------------
    # Build Comprehensive Stats String
    # -----------------------------
    stats_str = "=" * 50 + "\n"
    stats_str += "DNS NETWORK ACTIVITY MONITOR - STATISTICS\n"
    stats_str += "=" * 50 + "\n\n"
    
    stats_str += f"📊 OVERVIEW\n"
    stats_str += f"{'─' * 50}\n"
    stats_str += f"Total DNS Queries: {total_queries:,}\n"
    stats_str += f"Monitoring Period: {start_time} to {end_time}\n"
    stats_str += f"Average Query Rate: {qps:.2f} queries/second\n"
    stats_str += f"Unique Source IPs: {unique_ips}\n"
    stats_str += f"Unique Domains Queried: {unique_domains}\n\n"
    
    stats_str += f"🔐 SECURITY STATUS\n"
    stats_str += f"{'─' * 50}\n"
    stats_str += f"✅ Safe Queries: {safe_queries:,} ({safe_pct:.1f}%)\n"
    stats_str += f"🚫 Blocked Queries: {total_blocked:,} ({blocked_pct:.1f}%)\n"
    stats_str += f"   ├─ Blocked Domains: {blocked_domain:,}\n"
    stats_str += f"   └─ Blocked IPs: {blocked_ip:,}\n"
    stats_str += f"❌ Failed Queries: {failed_queries:,} ({failed_pct:.1f}%)\n"
    
    if cached_queries > 0:
        stats_str += f"⚡ Cached Responses: {cached_queries:,} ({cached_pct:.1f}%)\n"
    stats_str += "\n"
    
    stats_str += f"🌐 TOP ACTIVE IPs (Network Usage)\n"
    stats_str += f"{'─' * 50}\n"
    if top_ips:
        for idx, (ip, count) in enumerate(top_ips, 1):
            pct = (count / total_queries) * 100
            stats_str += f"{idx:2}. {ip:15} → {count:4} queries ({pct:.1f}%)\n"
    else:
        stats_str += "No IP data available\n"
    stats_str += "\n"
    
    stats_str += f"🔍 TOP REQUESTED DOMAINS/APPLICATIONS\n"
    stats_str += f"{'─' * 50}\n"
    if top_domains:
        for idx, (domain, count) in enumerate(top_domains, 1):
            pct = (count / total_queries) * 100
            # Truncate long domains for display
            display_domain = domain[:45] + "..." if len(domain) > 45 else domain
            stats_str += f"{idx:2}. {display_domain:48} → {count:4} ({pct:.1f}%)\n"
    else:
        stats_str += "No domain data available\n"
    stats_str += "\n"
    
    if top_blocked_domains:
        stats_str += f"⚠️  TOP BLOCKED DOMAINS (Security Threats)\n"
        stats_str += f"{'─' * 50}\n"
        for idx, (domain, count) in enumerate(top_blocked_domains, 1):
            display_domain = domain[:45] + "..." if len(domain) > 45 else domain
            stats_str += f"{idx}. {display_domain} → {count} attempts\n"
        stats_str += "\n"
    
    if top_blocked_ips:
        stats_str += f"🛡️  TOP BLOCKED IPs (Blacklisted Sources)\n"
        stats_str += f"{'─' * 50}\n"
        for idx, (ip, count) in enumerate(top_blocked_ips, 1):
            stats_str += f"{idx}. {ip} → {count} blocked attempts\n"
        stats_str += "\n"
    
    stats_str += f"📋 QUERY TYPE DISTRIBUTION\n"
    stats_str += f"{'─' * 50}\n"
    if type_counter:
        # Sort by count descending
        sorted_types = sorted(type_counter.items(), key=lambda x: x[1], reverse=True)
        for qtype, count in sorted_types:
            pct = (count / total_queries) * 100
            stats_str += f"{qtype:10} → {count:5} queries ({pct:.1f}%)\n"
    else:
        stats_str += "No query type data available\n"
    
    stats_str += "\n" + "=" * 50 + "\n"
    
    return stats_str