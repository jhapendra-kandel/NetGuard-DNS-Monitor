#!/usr/bin/env python3
"""
NetGuard DNS Monitor - Setup Script
Automates the installation and configuration process
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print setup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🛡️  NetGuard DNS Monitor - Setup Script  🛡️          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have Python {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")

def check_venv_exists():
    """Check if virtual environment exists"""
    venv_path = os.path.join(os.getcwd(), 'venv')
    return os.path.exists(venv_path)

def create_virtual_environment():
    """Create virtual environment"""
    print("\n📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def get_pip_command():
    """Get the appropriate pip command based on OS and venv"""
    if platform.system() == "Windows":
        return os.path.join('venv', 'Scripts', 'pip.exe')
    else:
        return os.path.join('venv', 'bin', 'pip')

def get_python_command():
    """Get the appropriate python command based on OS and venv"""
    if platform.system() == "Windows":
        return os.path.join('venv', 'Scripts', 'python.exe')
    else:
        return os.path.join('venv', 'bin', 'python')

def install_dependencies():
    """Install required dependencies"""
    print("\n📥 Installing dependencies...")
    pip_cmd = get_pip_command()
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found!")
        return False
    
    try:
        # Upgrade pip first
        print("  Upgrading pip...")
        subprocess.run([pip_cmd, 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        # Install requirements
        print("  Installing packages from requirements.txt...")
        subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_admin_privileges():
    """Check if script is run with admin privileges"""
    print("\n🔐 Checking administrator privileges...")
    
    if platform.system() == "Windows":
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if is_admin:
                print("✅ Running with administrator privileges")
            else:
                print("⚠️  Not running as administrator")
                print("   Note: You'll need admin rights to run the DNS server")
            return is_admin
        except:
            return False
    else:
        # Unix-like systems
        is_root = os.geteuid() == 0
        if is_root:
            print("✅ Running with root privileges")
        else:
            print("⚠️  Not running as root")
            print("   Note: You'll need to use 'sudo' to run the DNS server")
        return is_root

def print_next_steps():
    """Print next steps after setup"""
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    print("\n📝 Next Steps:")
    print("\n1. Activate virtual environment:")
    
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. Run NetGuard DNS Monitor:")
    if platform.system() == "Windows":
        print("   python main.py")
        print("   (Run Command Prompt as Administrator)")
    else:
        print("   sudo python3 main.py")
    
    print("\n3. Configure device DNS:")
    print("   - Find your computer's IP address")
    print("   - Set device DNS to your computer's IP")
    print("   - Set secondary DNS to 8.8.8.8")
    
    print("\n📚 Documentation:")
    print("   - Quick Start: QUICK_SETUP.md")
    print("   - Full Manual: USAGE.md")
    print("   - Installation: INSTALLATION.md")
    
    print("\n🔗 GitHub: https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor")
    print("="*60 + "\n")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Check/create virtual environment
    if check_venv_exists():
        print("\n📦 Virtual environment already exists")
        response = input("   Do you want to recreate it? (y/N): ").strip().lower()
        if response == 'y':
            print("   Removing old virtual environment...")
            import shutil
            shutil.rmtree('venv')
            if not create_virtual_environment():
                sys.exit(1)
    else:
        if not create_virtual_environment():
            sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Installation completed with errors")
        print("   Please check the error messages above")
        sys.exit(1)
    
    # Check admin privileges
    check_admin_privileges()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)