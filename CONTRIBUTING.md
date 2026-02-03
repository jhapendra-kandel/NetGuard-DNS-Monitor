# 🤝 Contributing to NetGuard DNS Monitor

Thank you for your interest in contributing to NetGuard DNS Monitor! This document provides guidelines and instructions for contributing to this project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for everyone, regardless of:
- Experience level
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Body size
- Race or ethnicity
- Age
- Religion
- Nationality

### Our Standards

**Positive Behavior:**
✅ Using welcoming and inclusive language  
✅ Being respectful of differing viewpoints  
✅ Gracefully accepting constructive criticism  
✅ Focusing on what's best for the community  
✅ Showing empathy towards others  

**Unacceptable Behavior:**
❌ Harassment or discriminatory language  
❌ Trolling or insulting comments  
❌ Public or private harassment  
❌ Publishing others' private information  
❌ Unprofessional conduct  

---

## 🚀 How Can I Contribute?

### Reporting Bugs

Found a bug? Help us fix it!

**Before submitting:**
1. Check [existing issues](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/issues)
2. Verify it's actually a bug
3. Gather relevant information

**Bug Report Template:**

```markdown
**Bug Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: [e.g., Windows 11]
- Python Version: [e.g., 3.11.0]
- NetGuard Version: [e.g., 2.0]

**Screenshots:**
If applicable

**Additional Context:**
Any other relevant information
```

### Suggesting Features

Have an idea? We'd love to hear it!

**Feature Request Template:**

```markdown
**Feature Description:**
Clear description of the feature

**Problem it Solves:**
What problem does this address?

**Proposed Solution:**
How should it work?

**Alternatives Considered:**
Other solutions you've thought about

**Additional Context:**
Mock-ups, examples, etc.
```

### Improving Documentation

Documentation improvements are always welcome!

**Areas to Contribute:**
- README improvements
- Code comments
- API documentation
- Usage examples
- Tutorial videos
- Translations

### Code Contributions

#### Good First Issues

Look for issues labeled:
- `good first issue` - Perfect for beginners
- `help wanted` - We need assistance
- `documentation` - Docs improvements
- `enhancement` - New features

#### Areas Needing Help

1. **Testing**
   - Unit tests
   - Integration tests
   - Performance tests

2. **Features**
   - HTTPS DNS (DoH) support
   - Advanced filtering
   - Database storage
   - API endpoints

3. **Performance**
   - Optimization
   - Memory management
   - Cache improvements

4. **UI/UX**
   - Design improvements
   - Dark mode
   - Accessibility

---

## 💻 Development Setup

### Prerequisites

- Python 3.8+
- Git
- Code editor (VS Code recommended)

### Fork and Clone

1. **Fork the repository**
   - Visit [NetGuard DNS Monitor](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor)
   - Click "Fork" button

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/NetGuard-DNS-Monitor.git
   cd NetGuard-DNS-Monitor
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor.git
   ```

### Development Environment

1. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development tools
   ```

3. **Install development tools**
   ```bash
   pip install pytest pytest-cov black flake8 mypy pylint
   ```

### Project Structure

```
NetGuard-DNS-Monitor/
├── main.py              # Entry point
├── dns_server.py        # Core DNS logic
├── gui.py               # User interface
├── stats.py             # Statistics
├── tests/               # Test files
│   ├── test_dns_server.py
│   ├── test_cache.py
│   └── test_blocklist.py
├── docs/                # Documentation
└── examples/            # Example configs
```

---

## 📝 Coding Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

#### Code Formatting

```python
# Use 4 spaces for indentation
def example_function():
    if condition:
        do_something()

# Maximum line length: 100 characters
long_variable_name = some_function_call(
    parameter1, parameter2, parameter3
)

# Imports organized
import os
import sys

from collections import Counter
from threading import Lock

import dnslib
import matplotlib
```

#### Naming Conventions

```python
# Classes: PascalCase
class DNSCache:
    pass

# Functions and variables: snake_case
def get_cache_stats():
    cache_hit_count = 0

# Constants: UPPER_SNAKE_CASE
MAX_CACHE_SIZE = 10000
UPSTREAM_DNS = '8.8.8.8'

# Private members: leading underscore
class Example:
    def __init__(self):
        self._private_var = 0
    
    def _private_method(self):
        pass
```

#### Documentation

```python
def compute_stats(all_logs):
    """Compute comprehensive statistics from logs.
    
    Args:
        all_logs (list): List of log entries (tuples)
        
    Returns:
        str: Formatted statistics string
        
    Example:
        >>> logs = [(time, ip, domain, type, details, success, blocked, cached)]
        >>> stats = compute_stats(logs)
        >>> print(stats)
    """
    # Implementation
```

#### Type Hints (Recommended)

```python
from typing import List, Tuple, Optional

def get_top_domains(logs: List[Tuple], count: int = 10) -> List[Tuple[str, int]]:
    """Get top N most queried domains."""
    # Implementation
```

### Code Quality Tools

#### Black (Auto-formatting)

```bash
# Format all Python files
black .

# Check without modifying
black --check .
```

#### Flake8 (Linting)

```bash
# Check code style
flake8 .

# Configuration in .flake8 file
[flake8]
max-line-length = 100
exclude = venv/,.git/
```

#### MyPy (Type Checking)

```bash
# Check type hints
mypy dns_server.py

# Configuration in mypy.ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
```

#### Pylint (Code Analysis)

```bash
# Full analysis
pylint dns_server.py

# Score should be > 8.0
```

---

## 📝 Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, missing semi-colons, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

**Good Commits:**

```
feat(cache): Add TTL-based expiration

Implement automatic cache expiration based on DNS TTL values.
Cache entries now automatically expire after their TTL, improving
accuracy of DNS responses.

Closes #123
```

```
fix(gui): Prevent crash when no logs exist

Add check for empty logs before computing statistics.
Previously would crash with IndexError.

Fixes #456
```

```
docs(readme): Update installation instructions

Add detailed steps for macOS installation including
Homebrew setup and Python installation.
```

**Bad Commits:**

```
❌ Fixed stuff
❌ Updated code
❌ Changes
❌ WIP
```

### Commit Best Practices

1. **One logical change per commit**
   - Don't mix bug fixes with features
   - Keep related changes together

2. **Write clear messages**
   - First line: concise summary (50 chars)
   - Body: detailed explanation (72 chars per line)
   - Reference issues/PRs

3. **Commit frequently**
   - Small, focused commits
   - Easier to review
   - Easier to revert

---

## 🔄 Pull Request Process

### Before Submitting

1. **Update from upstream**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests**
   ```bash
   pytest tests/
   ```

3. **Check code quality**
   ```bash
   black --check .
   flake8 .
   pylint dns_server.py
   ```

4. **Update documentation**
   - README if needed
   - Code comments
   - CHANGELOG

### Creating Pull Request

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open PR on GitHub**
   - Click "New Pull Request"
   - Select your branch
   - Fill out template

**PR Template:**

```markdown
## Description
Clear description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tested locally
- [ ] Added unit tests
- [ ] Tested on multiple platforms

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added where needed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests pass

## Screenshots
If applicable

## Related Issues
Closes #123
```

### Review Process

1. **Automated checks**
   - CI/CD runs tests
   - Code quality checks
   - Must pass before merge

2. **Code review**
   - Maintainer reviews code
   - May request changes
   - Discussion and iteration

3. **Approval and merge**
   - Approved by maintainer
   - Squash and merge
   - PR closed, branch deleted

### After Merge

1. **Update local repository**
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Delete feature branch**
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_dns_server.py

# Run with verbose output
pytest -v
```

### Writing Tests

**Test Structure:**

```python
# tests/test_dns_server.py
import pytest
from dns_server import DNSCache

class TestDNSCache:
    """Test DNS caching functionality."""
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        cache = DNSCache()
        cache.set('example.com', 'A', b'response', ttl=300)
        
        result = cache.get('example.com', 'A')
        assert result == b'response'
    
    def test_cache_expiration(self):
        """Test that cache entries expire after TTL."""
        cache = DNSCache()
        cache.set('example.com', 'A', b'response', ttl=0)
        
        import time
        time.sleep(1)
        
        result = cache.get('example.com', 'A')
        assert result is None
```

**Test Coverage Goals:**

- Unit tests: >80% coverage
- Integration tests for critical paths
- Edge cases and error conditions

---

## 📚 Documentation

### Code Comments

```python
# Good comments explain WHY, not WHAT

# Bad
x = x + 1  # Increment x

# Good
x = x + 1  # Offset by 1 to account for zero-indexing

# Complex logic needs explanation
# Cache key combines domain and type because:
# - Same domain can have multiple record types (A, AAAA, etc.)
# - Each type needs separate caching
# - Prevents type confusion in lookups
cache_key = (domain, qtype)
```

### README Updates

When adding features:

1. Update feature list
2. Add usage examples
3. Update screenshots if UI changed
4. Add to CHANGELOG

### API Documentation

Document all public functions:

```python
def handle_dns_request(data, addr, sock, **kwargs):
    """Handle individual DNS request with all features.
    
    This function processes incoming DNS queries by:
    1. Parsing the DNS request
    2. Checking cache for existing response
    3. Applying blocklist filters
    4. Forwarding to upstream if needed
    5. Logging the transaction
    
    Args:
        data (bytes): Raw DNS query packet
        addr (tuple): Client address (ip, port)
        sock (socket): UDP socket for sending response
        **kwargs: Additional components (cache, blocklist, etc.)
        
    Returns:
        None: Response sent directly via socket
        
    Raises:
        DNSError: If query parsing fails
        SocketError: If network communication fails
        
    Example:
        >>> handle_dns_request(query_data, ('192.168.1.100', 12345), 
        ...                   server_socket, cache=cache, blocklist=blocklist)
    """
```

---

## 🎯 Development Workflow

### Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes
# ... code ...

# 3. Test locally
pytest
black .
flake8 .

# 4. Commit
git add .
git commit -m "feat(component): description"

# 5. Push and create PR
git push origin feature/new-feature
```

### Bug Fixes

```bash
# 1. Create bugfix branch
git checkout -b fix/bug-description

# 2. Fix the bug
# ... code ...

# 3. Add test for the bug
# tests/test_*.py

# 4. Verify fix
pytest tests/test_specific_bug.py

# 5. Commit and push
git commit -m "fix(component): description"
git push origin fix/bug-description
```

---

## 🏆 Recognition

Contributors are recognized in:

- README.md contributors section
- Release notes
- GitHub contributors page

Top contributors may receive:
- Maintainer status
- Special recognition
- Recommendation letters (for students)

---

## 📧 Contact

**Questions?**
- Open a [Discussion](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/discussions)
- Email: jhapendrakandel@example.com
- Discord: [Join our server](#) (if available)

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

<div align="center">

**Thank you for contributing to NetGuard DNS Monitor!** 🙏

[Back to README](README.md) | [View Issues](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/issues) | [Create PR](https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor/pulls)

</div>
