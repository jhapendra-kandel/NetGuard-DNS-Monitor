"""
NetGuard DNS Monitor - Statistics Engine
Computes comprehensive network statistics and analytics

Author: Jhapendra Kandel
Project: 1st Year Python Programming
Institution: Softwarica College of IT & E-Commerce (Coventry University)
"""

from collections import Counter
import datetime


def compute_stats(all_logs):
    """Compute comprehensive statistics from DNS query logs
    
    Args:
        all_logs (list): List of log entries (tuples)
        
    Returns:
        str: Formatted statistics string with detailed analytics
    """
    
    # Check if we have any data
    if not all_logs:
        return """📊 NO DATA YET

Configure devices to use this PC as DNS server to start monitoring.

Setup Instructions:
1. Find your computer's IP address
2. On your device, go to Network settings
3. Set DNS to your computer's IP
4. Start browsing and watch the queries appear!
"""
    
    # Basic counts
    total_queries = len(all_logs)
    
    # Time range analysis
    start_time = all_logs[0][0]
    end_time = all_logs[-1][0]
    
    # Calculate time duration
    try:
        start_dt = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f')
        end_dt = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S.%f')
        duration = end_dt - start_dt
        duration_str = str(duration).split('.')[0]  # Remove microseconds
    except:
        duration_str = "Unknown"
    
    # Success/failure/blocked/cached tracking
    successful = sum(1 for log in all_logs if log[5])  # Index 5 is success
    failed = sum(1 for log in all_logs if not log[5])
    blocked = sum(1 for log in all_logs if log[6])  # Index 6 is blocked
    cached = sum(1 for log in all_logs if log[7])  # Index 7 is cached
    
    # Calculate percentages
    success_pct = (successful / total_queries * 100) if total_queries > 0 else 0
    failed_pct = (failed / total_queries * 100) if total_queries > 0 else 0
    blocked_pct = (blocked / total_queries * 100) if total_queries > 0 else 0
    cached_pct = (cached / total_queries * 100) if total_queries > 0 else 0
    
    # IP analysis
    ip_counter = Counter(log[1] for log in all_logs)
    top_ips = ip_counter.most_common(10)  # Increased from 5 to 10
    unique_ips = len(ip_counter)
    
    # Domain analysis
    domain_counter = Counter(log[2] for log in all_logs)
    top_domains = domain_counter.most_common(10)  # Increased from 5 to 10
    unique_domains = len(domain_counter)
    
    # Query type analysis
    type_counter = Counter(log[3] for log in all_logs)
    
    # Blocked domains analysis
    blocked_domains = [log[2] for log in all_logs if log[6]]
    if blocked_domains:
        blocked_domain_counter = Counter(blocked_domains)
        top_blocked = blocked_domain_counter.most_common(5)
    else:
        top_blocked = []
    
    # Build comprehensive statistics string
    stats_str = "📊 NETWORK ACTIVITY OVERVIEW\n"
    stats_str += "=" * 60 + "\n"
    stats_str += f"Total DNS Queries: {total_queries:,}\n"
    stats_str += f"  ✓ Successful: {successful:,} ({success_pct:.1f}%)\n"
    stats_str += f"  ✗ Failed: {failed:,} ({failed_pct:.1f}%)\n"
    stats_str += f"  🚫 Blocked: {blocked:,} ({blocked_pct:.1f}%)\n"
    stats_str += f"  💾 Cached: {cached:,} ({cached_pct:.1f}%)\n"
    stats_str += f"\n"
    stats_str += f"Monitoring Period:\n"
    stats_str += f"  Start: {start_time}\n"
    stats_str += f"  End: {end_time}\n"
    stats_str += f"  Duration: {duration_str}\n"
    stats_str += f"\n"
    stats_str += f"Network Diversity:\n"
    stats_str += f"  Unique Devices (IPs): {unique_ips}\n"
    stats_str += f"  Unique Domains: {unique_domains:,}\n"
    stats_str += "\n"
    
    # Top Active Devices
    stats_str += "🌐 TOP ACTIVE DEVICES (by query count)\n"
    stats_str += "=" * 60 + "\n"
    
    for i, (ip, count) in enumerate(top_ips, 1):
        percentage = (count / total_queries) * 100
        bar_length = min(int(percentage / 2), 30)
        bar = '█' * bar_length
        
        # Add device rank emoji
        rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        
        stats_str += f"{rank_emoji:3} {ip:15s} │ {count:5,d} queries ({percentage:5.1f}%) {bar}\n"
    
    stats_str += "\n"
    
    # Top Requested Domains
    stats_str += "📱 TOP REQUESTED DOMAINS/SERVICES\n"
    stats_str += "=" * 60 + "\n"
    
    for i, (domain, count) in enumerate(top_domains, 1):
        percentage = (count / total_queries) * 100
        
        # Truncate long domains
        display_domain = domain[:45] + '...' if len(domain) > 45 else domain
        
        # Add service type indicator
        service_icon = get_service_icon(domain)
        
        stats_str += f"{i:2}. {service_icon} {display_domain:48s} │ {count:4,d} ({percentage:5.1f}%)\n"
    
    stats_str += "\n"
    
    # Top Blocked Domains (if any)
    if top_blocked:
        stats_str += "🚫 TOP BLOCKED DOMAINS (Security Protection)\n"
        stats_str += "=" * 60 + "\n"
        
        for i, (domain, count) in enumerate(top_blocked, 1):
            percentage = (count / blocked * 100) if blocked > 0 else 0
            display_domain = domain[:45] + '...' if len(domain) > 45 else domain
            
            stats_str += f"{i}. {display_domain:48s} │ {count:4,d} ({percentage:5.1f}%)\n"
        
        stats_str += "\n"
    
    # Query Type Breakdown
    stats_str += "🔍 QUERY TYPE BREAKDOWN\n"
    stats_str += "=" * 60 + "\n"
    
    for qtype, count in type_counter.most_common():
        percentage = (count / total_queries) * 100
        bar_length = min(int(percentage / 3), 20)
        bar = '█' * bar_length
        
        # Add description for common query types
        type_desc = get_query_type_description(qtype)
        
        stats_str += f"{qtype:10s} │ {count:5,d} queries ({percentage:5.1f}%) {bar}\n"
        if type_desc:
            stats_str += f"           │ {type_desc}\n"
    
    stats_str += "\n"
    
    # Performance Insights
    cache_hit_rate = (cached / total_queries * 100) if total_queries > 0 else 0
    block_rate = (blocked / total_queries * 100) if total_queries > 0 else 0
    success_rate = (successful / total_queries * 100) if total_queries > 0 else 0
    
    stats_str += "💡 PERFORMANCE INSIGHTS\n"
    stats_str += "=" * 60 + "\n"
    stats_str += f"Cache Efficiency: {cache_hit_rate:.1f}% of queries served from cache\n"
    stats_str += f"Security Protection: {block_rate:.1f}% of queries blocked by filters\n"
    stats_str += f"Reliability: {success_rate:.1f}% success rate\n"
    stats_str += "\n"
    
    # Performance ratings
    if cache_hit_rate > 50:
        stats_str += "✅ Excellent cache performance! Reducing network load significantly.\n"
    elif cache_hit_rate > 30:
        stats_str += "✅ Good cache performance! Reducing network load.\n"
    elif cache_hit_rate > 10:
        stats_str += "⚠️  Moderate cache performance. Cache will improve over time.\n"
    else:
        stats_str += "ℹ️  Cache building up. Performance will improve as cache fills.\n"
    
    if block_rate > 10:
        stats_str += "✅ Blocklist actively protecting your network from ads and trackers.\n"
    elif block_rate > 5:
        stats_str += "✅ Blocklist providing moderate protection.\n"
    elif block_rate > 0:
        stats_str += "ℹ️  Some domains being blocked. Consider loading default blocklist.\n"
    
    if success_rate > 95:
        stats_str += "✅ Excellent network reliability!\n"
    elif success_rate > 90:
        stats_str += "✅ Good network reliability.\n"
    elif success_rate > 80:
        stats_str += "⚠️  Some network issues detected. Check your connection.\n"
    else:
        stats_str += "⚠️  High failure rate. Check network and upstream DNS settings.\n"
    
    stats_str += "\n"
    
    # Network Behavior Analysis
    stats_str += "🔬 NETWORK BEHAVIOR ANALYSIS\n"
    stats_str += "=" * 60 + "\n"
    
    # Check for unusual patterns
    if unique_ips == 1:
        stats_str += "📱 Single device monitoring\n"
    elif unique_ips < 5:
        stats_str += f"🏠 Small network ({unique_ips} devices)\n"
    elif unique_ips < 15:
        stats_str += f"🏢 Medium network ({unique_ips} devices)\n"
    else:
        stats_str += f"🏭 Large network ({unique_ips} devices)\n"
    
    # Query distribution analysis
    if top_ips:
        top_device_percentage = (top_ips[0][1] / total_queries * 100)
        if top_device_percentage > 80:
            stats_str += f"⚠️  Single device dominates traffic ({top_device_percentage:.0f}%)\n"
        elif top_device_percentage > 50:
            stats_str += f"ℹ️  Primary device: {top_ips[0][0]} ({top_device_percentage:.0f}% of traffic)\n"
    
    # Domain diversity
    avg_queries_per_domain = total_queries / unique_domains if unique_domains > 0 else 0
    if avg_queries_per_domain > 10:
        stats_str += "🔄 High domain repeat rate (good for caching)\n"
    elif avg_queries_per_domain > 3:
        stats_str += "📊 Moderate domain diversity\n"
    else:
        stats_str += "🌐 High domain diversity (many unique sites)\n"
    
    return stats_str


def get_service_icon(domain):
    """Get icon for common services
    
    Args:
        domain (str): Domain name
        
    Returns:
        str: Service icon/emoji
    """
    domain_lower = domain.lower()
    
    # Common services
    if 'google' in domain_lower:
        return '🔍'
    elif 'facebook' in domain_lower or 'fb' in domain_lower:
        return '📘'
    elif 'youtube' in domain_lower:
        return '📹'
    elif 'twitter' in domain_lower:
        return '🐦'
    elif 'instagram' in domain_lower:
        return '📷'
    elif 'amazon' in domain_lower:
        return '🛒'
    elif 'netflix' in domain_lower:
        return '🎬'
    elif 'spotify' in domain_lower:
        return '🎵'
    elif 'microsoft' in domain_lower or 'office' in domain_lower:
        return '💼'
    elif 'apple' in domain_lower or 'icloud' in domain_lower:
        return '🍎'
    elif 'github' in domain_lower:
        return '💻'
    elif 'cloudflare' in domain_lower:
        return '☁️'
    elif any(ad in domain_lower for ad in ['ad', 'ads', 'advertising', 'doubleclick']):
        return '🚫'
    else:
        return '🌐'


def get_query_type_description(qtype):
    """Get human-readable description of DNS query type
    
    Args:
        qtype (str): Query type code
        
    Returns:
        str: Description or empty string
    """
    descriptions = {
        'A': 'IPv4 address',
        'AAAA': 'IPv6 address',
        'CNAME': 'Canonical name (alias)',
        'MX': 'Mail exchange server',
        'TXT': 'Text record',
        'NS': 'Name server',
        'PTR': 'Pointer (reverse DNS)',
        'SOA': 'Start of authority',
        'SRV': 'Service locator',
        'CAA': 'Certificate authority authorization'
    }
    
    return descriptions.get(qtype, '')


def export_stats_to_file(all_logs, filename='dns_stats_report.txt'):
    """Export statistics to a text file
    
    Args:
        all_logs (list): Log entries
        filename (str): Output filename
        
    Returns:
        bool: Success status
    """
    try:
        stats = compute_stats(all_logs)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("NetGuard DNS Monitor - Statistics Report\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(stats)
            f.write("\n\n")
            f.write("=" * 60 + "\n")
            f.write("Report generated by NetGuard DNS Monitor\n")
            f.write("Author: Jhapendra Kandel\n")
            f.write("Institution: Softwarica College (Coventry University)\n")
        
        return True
    except Exception as e:
        print(f"Error exporting stats: {e}")
        return False