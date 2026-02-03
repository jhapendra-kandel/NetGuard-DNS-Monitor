# Changelog

All notable changes to NetGuard DNS Monitor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-02-03

### 🎉 Major Release - Complete Rewrite

This version represents a complete rewrite of the DNS Monitor with significant improvements across all aspects.

### ✨ Added

#### Core Features
- **DNS Caching System** - TTL-based intelligent caching
  - Automatic cache expiration
  - Hit/miss tracking
  - Performance metrics
  - Cache statistics view

- **Anomaly Detection** - Real-time threat detection
  - Excessive query monitoring (>100/min)
  - Suspicious domain detection
  - Pattern-based analysis
  - Severity classification (HIGH/MEDIUM/LOW)

- **Advanced Blocklist Management**
  - Wildcard subdomain blocking
  - Allowlist override system
  - Default ad/tracker lists
  - Persistent storage

- **Enhanced GUI**
  - Four-tab interface (Logs, Statistics, Blocklists, Alerts)
  - Real-time log filtering
  - Color-coded status indicators
  - Auto-refreshing statistics

#### Analytics Features
- **Statistics Dashboard**
  - Query type distribution (pie chart)
  - Top 10 active devices (bar chart)
  - Top 10 requested domains (bar chart)
  - Performance insights
  - Cache efficiency metrics

- **Data Export**
  - CSV export functionality
  - Timestamp-based filenames
  - Complete log data

#### User Interface
- **Menu System**
  - File menu (Export, Clear, Exit)
  - View menu (Pause/Resume)
  - Cache menu (Clear, Statistics)
  - Help menu (About)

- **Advanced Filtering**
  - Text search (domain/IP)
  - Query type filtering (A, AAAA, CNAME, MX, TXT)
  - Real-time filter updates

- **Status Bar**
  - Total queries counter
  - Blocked queries counter
  - Cached queries counter
  - Running/Paused status

### 🔧 Changed

- **Complete Architecture Redesign**
  - Separated concerns (main, dns_server, gui, stats)
  - Thread-safe data structures
  - Improved error handling
  - Better resource management

- **DNS Server Improvements**
  - Multi-threaded request handling
  - Timeout and retry logic
  - Proper socket management
  - Graceful shutdown

- **Performance Optimizations**
  - Efficient caching algorithm
  - Batch GUI updates (500ms)
  - Memory-conscious log retention
  - Set-based blocklist lookups

### 🐛 Fixed

- **Critical Bug Fixes**
  - UnboundLocalError in DNS handler (v1.1.0 issue)
  - Statistics not auto-refreshing
  - Blocklist persistence issues
  - Chart rendering problems
  - Memory leaks from unlimited log growth

- **UI/UX Fixes**
  - Scrollable statistics view
  - Proper color coding in logs
  - Clear filter functionality
  - Status bar accuracy

### 🔒 Security

- **Enhanced Security Features**
  - Domain validation
  - IP address validation
  - Input sanitization
  - Secure default configurations
  - Anomaly detection system

### 📚 Documentation

- **Comprehensive Documentation**
  - Detailed README.md
  - INSTALLATION.md guide
  - USAGE.md manual
  - CONTRIBUTING.md guidelines
  - API documentation
  - Code comments

### 🎓 Educational Value

- Demonstrates network programming concepts
- Shows multithreading implementation
- Illustrates DNS protocol handling
- Examples of GUI development
- Security best practices

---

## [1.1.0] - 2026-01-26

### ✨ Added
- Import domain lists from files
- IP validation for blacklist
- Clear logs function
- Enhanced UI with emojis and colors
- Scrollable statistics view
- Status distribution chart

### 🔧 Changed
- Statistics auto-refresh when tab selected
- All charts display correctly
- Improved error handling throughout
- Save blocklists on exit

### 🐛 Fixed
- Blocklists now fully functional with persistence
- Statistics calculation errors
- Chart rendering issues

---

## [1.0.0] - 2026-01-25

### 🎉 Initial Release

### ✨ Added
- Real-time DNS query monitoring
- Domain & IP blocking
- Persistent blocklists
- Color-coded logs
- Auto-refreshing statistics
- Visual charts (3 types)
- CSV export
- Pause/Resume logging
- Comprehensive metrics

### Core Components
- DNS proxy server on port 53
- Tkinter GUI interface
- Statistics computation
- Matplotlib visualizations

### Security Features
- Domain blacklisting
- IP blacklisting
- Threat detection
- Alert logging

### Documentation
- README.md with quick start
- Installation instructions
- Usage guide
- Troubleshooting section

---

## [Unreleased]

### 🚧 Planned Features

#### Version 2.1.0 (Q2 2026)
- [ ] HTTPS DNS (DoH) support
- [ ] Machine learning-based anomaly detection
- [ ] Custom alerting rules
- [ ] RESTful API for external integration
- [ ] Database storage option (SQLite)
- [ ] Configuration file support (YAML/JSON)

#### Version 3.0.0 (Q4 2026)
- [ ] Web-based dashboard
- [ ] Multi-user support
- [ ] Cloud sync capabilities
- [ ] Mobile app companion
- [ ] Docker container
- [ ] Kubernetes support

#### Future Enhancements
- [ ] IPv6 full support
- [ ] DNSSEC validation
- [ ] Geographic IP blocking
- [ ] Bandwidth monitoring
- [ ] Automated reports (PDF/email)
- [ ] Integration with threat intelligence feeds
- [ ] Dark mode UI
- [ ] Accessibility improvements
- [ ] Internationalization (i18n)
- [ ] Plugin system

---

## Version History Summary

| Version | Release Date | Key Highlight |
|---------|--------------|---------------|
| 2.0.0 | 2026-02-03 | Complete rewrite with caching & anomaly detection |
| 1.1.0 | 2026-01-26 | Fixed blocklists, improved statistics |
| 1.0.0 | 2026-01-25 | Initial public release |

---

## Migration Guide

### Upgrading from v1.x to v2.0

**Breaking Changes:**
- Configuration file format changed
- API endpoints restructured (if using programmatically)
- Log format updated

**Migration Steps:**

1. **Backup your data**
   ```bash
   # Export current logs
   # Backup blocklists
   ```

2. **Install new version**
   ```bash
   git pull origin main
   pip install -r requirements.txt
   ```

3. **Migrate blocklists**
   - Old blocklists automatically imported on first run
   - Verify in Blocklist Manager tab

4. **Verify functionality**
   - Test DNS resolution
   - Check statistics
   - Confirm alerts working

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Reporting bugs
- Suggesting features
- Submitting pull requests
- Development setup

---

## Support

- **Issues:** [GitHub Issues](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/issues)
- **Discussions:** [GitHub Discussions](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/discussions)
- **Email:** jhapendrakandel@example.com

---

<div align="center">

**Stay Updated!** Watch this repository for new releases.

[Back to README](README.md) | [View Releases](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/releases)

</div>
