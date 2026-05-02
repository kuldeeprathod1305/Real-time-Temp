#!/usr/bin/env python3
"""
🔮 Temperature Prediction System - Automated Setup Script
This script automates the installation and setup process.

Usage:
    python setup.py
"""

import os
import sys
import shutil
from pathlib import Path

class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")

def check_files_exist():
    """Check if required files are in current directory"""
    print_header("Step 1: Checking Required Files")
    
    required_files = {
        'temperature_predictor.py': 'Prediction engine module',
        'app_updated.py': 'Updated Flask application',
        'requirements.txt': 'Updated Python dependencies',
        '__init___updated.py': 'Updated utils package'
    }
    
    missing = []
    for filename, description in required_files.items():
        if os.path.exists(filename):
            print_success(f"Found: {filename} ({description})")
        else:
            print_error(f"Missing: {filename} ({description})")
            missing.append(filename)
    
    if missing:
        print_error(f"\nMissing {len(missing)} file(s)!")
        print_info("Make sure all files are in the current directory:")
        for f in missing:
            print(f"  - {f}")
        return False
    
    print_success("All required files found!")
    return True

def check_project_structure():
    """Check if project structure is correct"""
    print_header("Step 2: Checking Project Structure")
    
    required_dirs = {
        'utils': 'Utils package directory',
        'templates': 'Templates directory',
    }
    
    for dirname, description in required_dirs.items():
        if os.path.isdir(dirname):
            print_success(f"Found: {dirname}/ ({description})")
        else:
            print_error(f"Missing: {dirname}/ ({description})")
            return False
    
    # Check utils files
    utils_files = ['alert_monitor.py', 'email_config.py', '__init__.py']
    for filename in utils_files:
        path = os.path.join('utils', filename)
        if os.path.exists(path):
            print_success(f"Found: utils/{filename}")
        else:
            print_warning(f"Missing: utils/{filename} (might need manual check)")
    
    print_success("Project structure looks good!")
    return True

def backup_files():
    """Backup existing files before overwriting"""
    print_header("Step 3: Backing Up Existing Files")
    
    files_to_backup = [
        ('app.py', 'app.py.bak'),
        ('requirements.txt', 'requirements.txt.bak'),
        ('utils/__init__.py', 'utils/__init__.py.bak')
    ]
    
    for original, backup in files_to_backup:
        if os.path.exists(original):
            try:
                shutil.copy(original, backup)
                print_success(f"Backed up: {original} → {backup}")
            except Exception as e:
                print_error(f"Failed to backup {original}: {e}")
                return False
        else:
            print_info(f"Skipped: {original} (not found)")
    
    return True

def install_dependencies():
    """Install required Python packages"""
    print_header("Step 4: Installing Dependencies")
    
    packages = [
        ('scikit-learn', '1.3.2'),
        ('numpy', '1.24.3'),
    ]
    
    import subprocess
    
    for package, version in packages:
        print_info(f"Installing {package}=={version}...")
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', f'{package}=={version}'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print_success(f"Installed: {package}=={version}")
        except subprocess.CalledProcessError:
            print_error(f"Failed to install {package}")
            return False
    
    return True

def copy_prediction_module():
    """Copy temperature_predictor.py to utils/"""
    print_header("Step 5: Installing Prediction Module")
    
    src = 'temperature_predictor.py'
    dst = os.path.join('utils', 'temperature_predictor.py')
    
    try:
        shutil.copy(src, dst)
        print_success(f"Copied: {src} → {dst}")
        return True
    except Exception as e:
        print_error(f"Failed to copy {src}: {e}")
        return False

def update_app():
    """Replace app.py with app_updated.py"""
    print_header("Step 6: Updating Flask Application")
    
    src = 'app_updated.py'
    dst = 'app.py'
    
    try:
        shutil.copy(src, dst)
        print_success(f"Updated: {src} → {dst}")
        return True
    except Exception as e:
        print_error(f"Failed to update app.py: {e}")
        return False

def update_utils_init():
    """Update utils/__init__.py"""
    print_header("Step 7: Updating Utils Package")
    
    src = '__init___updated.py'
    dst = os.path.join('utils', '__init__.py')
    
    try:
        shutil.copy(src, dst)
        print_success(f"Updated: {src} → {dst}")
        return True
    except Exception as e:
        print_error(f"Failed to update utils/__init__.py: {e}")
        return False

def update_requirements():
    """Replace requirements.txt"""
    print_header("Step 8: Updating Requirements")
    
    try:
        # Already copied in step 4, but verify
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                content = f.read()
                if 'scikit-learn' in content and 'numpy' in content:
                    print_success("requirements.txt is up to date")
                    return True
        
        print_error("requirements.txt not properly updated")
        return False
    except Exception as e:
        print_error(f"Failed to verify requirements.txt: {e}")
        return False

def verify_installation():
    """Verify the installation"""
    print_header("Step 9: Verifying Installation")
    
    # Check if prediction module can be imported
    try:
        sys.path.insert(0, os.getcwd())
        from utils.temperature_predictor import TemperaturePredictor
        print_success("Can import TemperaturePredictor")
    except ImportError as e:
        print_error(f"Cannot import TemperaturePredictor: {e}")
        return False
    
    # Check if scikit-learn is installed
    try:
        import sklearn
        print_success(f"scikit-learn {sklearn.__version__} is installed")
    except ImportError:
        print_error("scikit-learn not installed")
        return False
    
    # Check if numpy is installed
    try:
        import numpy
        print_success(f"numpy {numpy.__version__} is installed")
    except ImportError:
        print_error("numpy not installed")
        return False
    
    print_success("Installation verified!")
    return True

def print_next_steps():
    """Print instructions for next steps"""
    print_header("✨ Setup Complete!")
    
    print(f"{Colors.BOLD}Your temperature prediction system is ready!{Colors.ENDC}\n")
    
    print("Next steps:\n")
    
    print(f"{Colors.BOLD}1. Start Flask Server:{Colors.ENDC}")
    print("   python -X utf8 app.py\n")
    
    print(f"{Colors.BOLD}2. Test the API:{Colors.ENDC}")
    print("   curl http://127.0.0.1:5000/api/predict")
    print("   curl http://127.0.0.1:5000/api/predict/24h-forecast\n")
    
    print(f"{Colors.BOLD}3. Verify endpoints (wait 10+ minutes for data):{Colors.ENDC}")
    print("   GET /api/predict?minutes_ahead=30")
    print("   GET /api/predict/multiple")
    print("   GET /api/predict/24h-forecast")
    print("   GET /api/predict/moving-average")
    print("   GET /api/predict/anomalies\n")
    
    print(f"{Colors.BOLD}4. Read Documentation:{Colors.ENDC}")
    print("   - 00_START_HERE.md")
    print("   - API_QUICK_REFERENCE.md")
    print("   - PREDICTION_IMPLEMENTATION_GUIDE.md\n")
    
    print(f"{Colors.BOLD}Backup files created:{Colors.ENDC}")
    print("   - app.py.bak")
    print("   - requirements.txt.bak")
    print("   - utils/__init__.py.bak\n")
    
    print(f"{Colors.GREEN}{Colors.BOLD}🔮 Happy Predicting!{Colors.ENDC}\n")

def main():
    """Main setup flow"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     🔮 TEMPERATURE PREDICTION SYSTEM - SETUP WIZARD             ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    steps = [
        ("Checking Required Files", check_files_exist),
        ("Checking Project Structure", check_project_structure),
        ("Backing Up Existing Files", backup_files),
        ("Installing Dependencies", install_dependencies),
        ("Installing Prediction Module", copy_prediction_module),
        ("Updating Flask Application", update_app),
        ("Updating Utils Package", update_utils_init),
        ("Updating Requirements", update_requirements),
        ("Verifying Installation", verify_installation),
    ]
    
    failed_step = None
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_step = step_name
                break
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            failed_step = step_name
            break
    
    if failed_step:
        print_header("⚠️  Setup Failed")
        print_error(f"Setup failed at: {failed_step}")
        print_info("Check the errors above and try again")
        print_info("You can restore from backups if needed:")
        print("  cp app.py.bak app.py")
        print("  cp requirements.txt.bak requirements.txt")
        print("  cp utils/__init__.py.bak utils/__init__.py\n")
        return False
    
    print_next_steps()
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
