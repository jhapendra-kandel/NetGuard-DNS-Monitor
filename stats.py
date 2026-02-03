from collections import Counter
import datetime

def compute_stats(all_logs):
    """Compute comprehensive statistics from logs"""
    if not all_logs:
        return "No data yet.\n\nConfigure devices to use this PC as DNS server to start monitoring."
    
    total_queries = len(all_logs)
    
    # Time range
    start_time = all_logs[0][0]
    end_time = all_logs[-1][0]
    
    # Success/failure/blocked/cached tracking
    successful = sum(1 for log in all_logs if log[5])  # Index 5 is success
    failed = sum(1 for log in all_logs if not log[5])
    blocked = sum(1 for log in all_logs if log[6])  # Index 6 is blocked
    cached = sum(1 for log in all_logs if log[7])  # Index 7 is cached
    
    # IP analysis
    ip_counter = Counter(log[1] for log in all_logs)
    top_ips = ip_counter.most_common(5)
    unique_ips = len(ip_counter)
    
    # Domain analysis
    domain_counter = Counter(log[2] for log in all_logs)
    top_domains = domain_counter.most_common(5)
    unique_domains = len(domain_counter)
    
    # Query type analysis
    type_counter = Counter(log[3] for log in all_logs)
    
    # Build statistics string
    stats_str = f"📊 OVERVIEW\n"
    stats_str += f"{'─' * 60}\n"
    stats_str += f"Total DNS Queries: {total_queries:,}\n"
    stats_str += f"  ✓ Successful: {successful:,} ({successful/total_queries*100:.1f}%)\n"
    stats_str += f"  ✗ Failed: {failed:,} ({failed/total_queries*100:.1f}%)\n"
    stats_str += f"  🚫 Blocked: {blocked:,} ({blocked/total_queries*100:.1f}%)\n"
    stats_str += f"  💾 Cached: {cached:,} ({cached/total_queries*100:.1f}%)\n"
    stats_str += f"\nTime Range: {start_time} to {end_time}\n"
    stats_str += f"Unique IPs: {unique_ips} | Unique Domains: {unique_domains}\n\n"
    
    stats_str += f"🌐 TOP ACTIVE DEVICES (by query count)\n"
    stats_str += f"{'─' * 60}\n"
    for i, (ip, count) in enumerate(top_ips, 1):
        percentage = (count / total_queries) * 100
        bar = '█' * min(int(percentage / 2), 30)
        stats_str += f"{i}. {ip:15s} │ {count:5d} queries ({percentage:5.1f}%) {bar}\n"
    
    stats_str += f"\n📱 TOP REQUESTED DOMAINS/SERVICES\n"
    stats_str += f"{'─' * 60}\n"
    for i, (domain, count) in enumerate(top_domains, 1):
        percentage = (count / total_queries) * 100
        display_domain = domain[:45] + '...' if len(domain) > 45 else domain
        stats_str += f"{i}. {display_domain:48s} │ {count:4d} ({percentage:5.1f}%)\n"
    
    stats_str += f"\n🔍 QUERY TYPE BREAKDOWN\n"
    stats_str += f"{'─' * 60}\n"
    for qtype, count in type_counter.most_common():
        percentage = (count / total_queries) * 100
        bar = '█' * min(int(percentage / 3), 20)
        stats_str += f"{qtype:10s} │ {count:5d} queries ({percentage:5.1f}%) {bar}\n"
    
    # Performance insights
    cache_hit_rate = (cached / total_queries * 100) if total_queries > 0 else 0
    block_rate = (blocked / total_queries * 100) if total_queries > 0 else 0
    
    stats_str += f"\n💡 PERFORMANCE INSIGHTS\n"
    stats_str += f"{'─' * 60}\n"
    stats_str += f"Cache Efficiency: {cache_hit_rate:.1f}% of queries served from cache\n"
    stats_str += f"Security: {block_rate:.1f}% of queries blocked by filters\n"
    
    if cache_hit_rate > 30:
        stats_str += f"✓ Great cache performance! Reducing network load.\n"
    if block_rate > 10:
        stats_str += f"✓ Blocklist actively protecting your network.\n"
    
    return stats_str