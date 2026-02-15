# NetGuard DNS Monitor - this is the statistics engine file
# it computes all the network statistics and analytics from dns query logs
# basically all the numbers and charts you see in gui come from here

# Author: Jhapendra kandel
# Project: 1st Year Python Programming
# Institution: Softwarica College of IT & E-Commerce (Coventry University)

# counter is very useful for counting how many times something appears in a list
from collections import Counter
# datetime for handling time related stuff like duration calculation
import datetime

VERSION = "2.3.0"

def compute_stats(all_logs):
    """Compute comprehensive statistics from DNS query logs
    
    Args:
        all_logs (list): List of log entries (tuples)
        
    Returns:
        str: Formatted statistics string with detailed analytics
    """
    
    # if there is no data yet we show a helpful message telling user how to set things up
    if not all_logs:
        return """📊 NO DATA YET

Configure devices to use this PC as DNS server to start monitoring.

Setup Instructions:
1. Find your computer's IP address
2. On your device, go to Network settings
3. Set DNS to your computer's IP
4. Start browsing and watch the queries appear!
"""
    
    # counting total queries we have in our log list
    total_queries = len(all_logs)
    
    # getting the first and last timestamp to know the time range of our data
    start_time = all_logs[0][0]
    end_time = all_logs[-1][0]
    
    # calculating how long we have been monitoring
    # we parse the timestamp strings back into datetime objects to do math on them
    try:
        start_dt = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f')
        end_dt = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S.%f')
        duration = end_dt - start_dt
        # removing the microseconds part because it looks ugly in display
        duration_str = str(duration).split('.')[0]
    except:
        duration_str = "Unknown"
    
    # counting successful failed blocked and cached queries from the log entries
    # each log entry is a tuple and we check specific index positions
    successful = sum(1 for log in all_logs if log[5])  # index 5 is success true/false
    failed = sum(1 for log in all_logs if not log[5])
    blocked = sum(1 for log in all_logs if log[6])  # index 6 tells if it was blocked
    cached = sum(1 for log in all_logs if log[7])  # index 7 tells if it came from cache
    
    # calculating percentage for each category so user can see ratio easily
    success_pct = (successful / total_queries * 100) if total_queries > 0 else 0
    failed_pct = (failed / total_queries * 100) if total_queries > 0 else 0
    blocked_pct = (blocked / total_queries * 100) if total_queries > 0 else 0
    cached_pct = (cached / total_queries * 100) if total_queries > 0 else 0
    
    # analyzing which ip addresses (devices) are making most queries
    # counter makes it easy to count occurrences of each ip
    ip_counter = Counter(log[1] for log in all_logs)
    top_ips = ip_counter.most_common(10)  # getting top 10 most active devices
    unique_ips = len(ip_counter)  # how many different devices are using our dns
    
    # analyzing which domains are being requested most
    # this tells us what websites people are visiting most
    domain_counter = Counter(log[2] for log in all_logs)
    top_domains = domain_counter.most_common(10)  # top 10 most requested domains
    unique_domains = len(domain_counter)  # total unique domains people visited
    
    # counting query types like A, AAAA, CNAME etc
    # A is for ipv4 address and AAAA is for ipv6
    type_counter = Counter(log[3] for log in all_logs)
    
    # finding which blocked domains were requested most
    # this helps us know what kind of ads/trackers are most common
    blocked_domains = [log[2] for log in all_logs if log[6]]
    if blocked_domains:
        blocked_domain_counter = Counter(blocked_domains)
        top_blocked = blocked_domain_counter.most_common(5)
    else:
        top_blocked = []
    
    # now we start building the big statistics string that will be displayed in gui
    # we add section by section with nice formatting and emojis
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
    
    # showing top active devices section with bar chart made of block characters
    # the bar length is based on percentage of total queries
    stats_str += "🌐 TOP ACTIVE DEVICES (by query count)\n"
    stats_str += "=" * 60 + "\n"
    
    for i, (ip, count) in enumerate(top_ips, 1):
        percentage = (count / total_queries) * 100
        # making a simple text bar chart, max 30 characters long
        bar_length = min(int(percentage / 2), 30)
        bar = '█' * bar_length
        
        # adding medal emojis for top 3 devices thats a nice touch
        rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        
        stats_str += f"{rank_emoji:3} {ip:15s} │ {count:5,d} queries ({percentage:5.1f}%) {bar}\n"
    
    stats_str += "\n"
    
    # showing top requested domains with service icons
    # we use get_service_icon function to show relevant emoji for each service
    stats_str += "📱 TOP REQUESTED DOMAINS/SERVICES\n"
    stats_str += "=" * 60 + "\n"
    
    for i, (domain, count) in enumerate(top_domains, 1):
        percentage = (count / total_queries) * 100
        
        # if domain name is too long we cut it and add ... at end
        display_domain = domain[:45] + '...' if len(domain) > 45 else domain
        
        # getting the right icon for this domain like google gets search icon etc
        service_icon = get_service_icon(domain)
        
        stats_str += f"{i:2}. {service_icon} {display_domain:48s} │ {count:4,d} ({percentage:5.1f}%)\n"
    
    stats_str += "\n"
    
    # showing blocked domains section only if there are any blocked ones
    if top_blocked:
        stats_str += "🚫 TOP BLOCKED DOMAINS (Security Protection)\n"
        stats_str += "=" * 60 + "\n"
        
        for i, (domain, count) in enumerate(top_blocked, 1):
            percentage = (count / blocked * 100) if blocked > 0 else 0
            display_domain = domain[:45] + '...' if len(domain) > 45 else domain
            
            stats_str += f"{i}. {display_domain:48s} │ {count:4,d} ({percentage:5.1f}%)\n"
        
        stats_str += "\n"
    
    # showing query type breakdown like how many A records vs AAAA vs CNAME etc
    stats_str += "🔍 QUERY TYPE BREAKDOWN\n"
    stats_str += "=" * 60 + "\n"
    
    for qtype, count in type_counter.most_common():
        percentage = (count / total_queries) * 100
        bar_length = min(int(percentage / 3), 20)
        bar = '█' * bar_length
        
        # getting human readable description for each query type
        type_desc = get_query_type_description(qtype)
        
        stats_str += f"{qtype:10s} │ {count:5,d} queries ({percentage:5.1f}%) {bar}\n"
        if type_desc:
            stats_str += f"           │ {type_desc}\n"
    
    stats_str += "\n"
    
    # calculating performance metrics to give user insights about how well things are working
    cache_hit_rate = (cached / total_queries * 100) if total_queries > 0 else 0
    block_rate = (blocked / total_queries * 100) if total_queries > 0 else 0
    success_rate = (successful / total_queries * 100) if total_queries > 0 else 0
    
    stats_str += "💡 PERFORMANCE INSIGHTS\n"
    stats_str += "=" * 60 + "\n"
    stats_str += f"Cache Efficiency: {cache_hit_rate:.1f}% of queries served from cache\n"
    stats_str += f"Security Protection: {block_rate:.1f}% of queries blocked by filters\n"
    stats_str += f"Reliability: {success_rate:.1f}% success rate\n"
    stats_str += "\n"
    
    # giving ratings based on cache performance
    # higher cache hit rate means less load on network which is good
    if cache_hit_rate > 50:
        stats_str += "✅ Excellent cache performance! Reducing network load significantly.\n"
    elif cache_hit_rate > 30:
        stats_str += "✅ Good cache performance! Reducing network load.\n"
    elif cache_hit_rate > 10:
        stats_str += "⚠️  Moderate cache performance. Cache will improve over time.\n"
    else:
        stats_str += "ℹ️  Cache building up. Performance will improve as cache fills.\n"
    
    # giving ratings based on how much blocking is happening
    if block_rate > 10:
        stats_str += "✅ Blocklist actively protecting your network from ads and trackers.\n"
    elif block_rate > 5:
        stats_str += "✅ Blocklist providing moderate protection.\n"
    elif block_rate > 0:
        stats_str += "ℹ️  Some domains being blocked. Consider loading default blocklist.\n"
    
    # giving ratings based on success rate of queries
    # if too many queries failing then there might be network problem
    if success_rate > 95:
        stats_str += "✅ Excellent network reliability!\n"
    elif success_rate > 90:
        stats_str += "✅ Good network reliability.\n"
    elif success_rate > 80:
        stats_str += "⚠️  Some network issues detected. Check your connection.\n"
    else:
        stats_str += "⚠️  High failure rate. Check network and upstream DNS settings.\n"
    
    stats_str += "\n"
    
    # analyzing network behavior like how many devices and what kind of network it is
    stats_str += "🔬 NETWORK BEHAVIOR ANALYSIS\n"
    stats_str += "=" * 60 + "\n"
    
    # categorizing network size based on number of unique devices
    if unique_ips == 1:
        stats_str += "📱 Single device monitoring\n"
    elif unique_ips < 5:
        stats_str += f"🏠 Small network ({unique_ips} devices)\n"
    elif unique_ips < 15:
        stats_str += f"🏢 Medium network ({unique_ips} devices)\n"
    else:
        stats_str += f"🏭 Large network ({unique_ips} devices)\n"
    
    # checking if one device is making too many queries compared to others
    # this could mean something is wrong or one device is very active
    if top_ips:
        top_device_percentage = (top_ips[0][1] / total_queries * 100)
        if top_device_percentage > 80:
            stats_str += f"⚠️  Single device dominates traffic ({top_device_percentage:.0f}%)\n"
        elif top_device_percentage > 50:
            stats_str += f"ℹ️  Primary device: {top_ips[0][0]} ({top_device_percentage:.0f}% of traffic)\n"
    
    # checking domain diversity to understand browsing pattern
    # high repeat rate means same sites being visited again and again which is good for cache
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
    # converting to lowercase so we can match without worrying about case
    domain_lower = domain.lower()
    
    # checking which popular service this domain belongs to and returning matching emoji
    # this makes the stats display look nicer with relevant icons
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
        # for unknown domains we just use globe icon
        return '🌐'


def get_query_type_description(qtype):
    """Get human-readable description of DNS query type
    
    Args:
        qtype (str): Query type code
        
    Returns:
        str: Description or empty string
    """
    # mapping query type codes to simple english descriptions
    # so user can understand what each type means without googling
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
        # first computing the stats string using our main function
        stats = compute_stats(all_logs)
        
        # writing everything to a text file with header and footer
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("NetGuard DNS Monitor - Statistics Report\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(stats)
            f.write("\n\n")
            f.write("=" * 60 + "\n")
            f.write("Report generated by NetGuard DNS Monitor\n")
            f.write("Author: Jhapendra kandel\n")
            f.write("Institution: Softwarica College (Coventry University)\n")
        
        return True
    except Exception as e:
        # if something goes wrong while saving we just print error and return false
        print(f"Error exporting stats: {e}")
        return False
