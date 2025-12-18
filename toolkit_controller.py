#!/usr/bin/env python3
"""
Bug Bounty Toolkit Controller
Manages anonymization settings and provides easy access to toolkit functions
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add core directory to path
TOOLKIT_ROOT = Path(__file__).parent
sys.path.insert(0, str(TOOLKIT_ROOT / "core"))

try:
    from anonymization import generate_anonymity_report, check_anonymity, is_anonymous_mode
except ImportError:
    print("[!] Error: Could not import anonymization module")
    sys.exit(1)

class ToolkitController:
    """Main controller for the bug bounty toolkit"""
    
    def __init__(self):
        self.toolkit_root = TOOLKIT_ROOT
        self.current_status = self._get_current_status()
    
    def _get_current_status(self):
        """Get current anonymization status"""
        env_var = os.getenv('TOOLKIT_ANONYMOUS', '').lower()
        return env_var in ['true', '1', 'yes', 'on', 'enabled']
    
    def enable_anonymous_mode(self):
        """Enable anonymous mode"""
        print("[+] Enabling anonymous mode...")
        
        # Set environment variable for current session
        os.environ['TOOLKIT_ANONYMOUS'] = 'true'
        
        # Add to shell profile for persistence
        self._add_to_shell_profile('export TOOLKIT_ANONYMOUS=true')
        
        print("[+] Anonymous mode ENABLED")
        print("[+] All toolkit operations will now be anonymized")
        print("[+] Restart your shell or run: source ~/.bashrc (or ~/.zshrc)")
        
        # Show immediate status
        self._show_anonymity_status()
    
    def disable_anonymous_mode(self):
        """Disable anonymous mode"""
        print("[+] Disabling anonymous mode...")
        
        # Remove from environment
        os.environ.pop('TOOLKIT_ANONYMOUS', None)
        
        # Remove from shell profile
        self._remove_from_shell_profile('export TOOLKIT_ANONYMOUS=true')
        
        print("[+] Anonymous mode DISABLED")
        print("[+] Toolkit will operate in direct mode")
        print("[+] Restart your shell or run: unset TOOLKIT_ANONYMOUS")
    
    def _add_to_shell_profile(self, line):
        """Add line to shell profile"""
        shell_profiles = ['~/.bashrc', '~/.zshrc', '~/.bash_profile', '~/.profile']
        
        for profile in shell_profiles:
            profile_path = Path(profile).expanduser()
            if profile_path.exists():
                # Check if line already exists
                with open(profile_path, 'r') as f:
                    content = f.read()
                
                if line not in content:
                    with open(profile_path, 'a') as f:
                        f.write(f'\\n# Bug Bounty Toolkit Anonymization\\n{line}\\n')
                    print(f"[+] Added to {profile}")
                break
    
    def _remove_from_shell_profile(self, line):
        """Remove line from shell profiles"""
        shell_profiles = ['~/.bashrc', '~/.zshrc', '~/.bash_profile', '~/.profile']
        
        for profile in shell_profiles:
            profile_path = Path(profile).expanduser()
            if profile_path.exists():
                # Read current content
                with open(profile_path, 'r') as f:
                    lines = f.readlines()
                
                # Filter out the line and related comments
                new_lines = []
                skip_next = False
                for current_line in lines:
                    if '# Bug Bounty Toolkit Anonymization' in current_line:
                        skip_next = True
                        continue
                    if skip_next and line in current_line:
                        skip_next = False
                        continue
                    new_lines.append(current_line)
                
                # Write back
                with open(profile_path, 'w') as f:
                    f.writelines(new_lines)
                print(f"[+] Removed from {profile}")
    
    def _show_anonymity_status(self):
        """Show detailed anonymity status"""
        try:
            print(generate_anonymity_report())
        except Exception as e:
            print(f"[!] Error checking anonymity status: {e}")
    
    def install_dependencies(self):
        """Install required dependencies for anonymization"""
        print("[+] Installing anonymization dependencies...")
        
        dependencies = [
            'PySocks',  # For SOCKS proxy support
            'requests[socks]',  # Requests with SOCKS support
        ]
        
        for dep in dependencies:
            print(f"[+] Installing {dep}...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                             check=True, capture_output=True)
                print(f"[+] {dep} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"[!] Failed to install {dep}: {e}")
        
        # Check for system tools
        system_tools = ['tor', 'proxychains4']
        for tool in system_tools:
            result = subprocess.run(['which', tool], capture_output=True)
            if result.returncode == 0:
                print(f"[+] {tool} is available")
            else:
                print(f"[!] {tool} not found - install with:")
                if tool == 'tor':
                    print("    macOS: brew install tor")
                    print("    Linux: sudo apt install tor")
                elif tool == 'proxychains4':
                    print("    macOS: brew install proxychains-ng")
                    print("    Linux: sudo apt install proxychains4")
    
    def run_tool(self, tool_name, *args):
        """Run a toolkit tool with current anonymization settings"""
        tool_paths = [
            self.toolkit_root / "tools" / "web_applications",
            self.toolkit_root / "tools" / "social_engineering", 
            self.toolkit_root / "exploitation" / "tools",
            self.toolkit_root / "reconnaissance" / "src"
        ]
        
        tool_found = None
        for path in tool_paths:
            potential_tool = path / f"{tool_name}.py"
            if potential_tool.exists():
                tool_found = potential_tool
                break
        
        if not tool_found:
            print(f"[!] Tool '{tool_name}' not found")
            return
        
        # Show anonymization status
        if is_anonymous_mode():
            print(f"[+] Running {tool_name} in ANONYMOUS mode")
        else:
            print(f"[+] Running {tool_name} in DIRECT mode")
        
        # Execute tool
        cmd = [sys.executable, str(tool_found)] + list(args)
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print(f"\\n[!] {tool_name} interrupted by user")
        except Exception as e:
            print(f"[!] Error running {tool_name}: {e}")
    
    def list_tools(self):
        """List available tools"""
        tool_dirs = [
            ("Web Applications", self.toolkit_root / "tools" / "web_applications"),
            ("Social Engineering", self.toolkit_root / "tools" / "social_engineering"),
            ("Exploitation", self.toolkit_root / "exploitation" / "tools"),
            ("Reconnaissance", self.toolkit_root / "reconnaissance" / "src")
        ]
        
        print("\\n🛠️  AVAILABLE TOOLS:")
        print("=" * 50)
        
        for category, path in tool_dirs:
            if path.exists():
                tools = [f.stem for f in path.glob("*.py") if not f.name.startswith('__')]
                if tools:
                    print(f"\\n{category}:")
                    for tool in sorted(tools):
                        print(f"  • {tool}")
    
    def quick_test(self, url=None):
        """Quick anonymity test"""
        test_url = url or "https://httpbin.org/ip"
        
        print(f"[+] Testing anonymization with: {test_url}")
        print(f"[+] Current mode: {'ANONYMOUS' if is_anonymous_mode() else 'DIRECT'}")
        
        try:
            from anonymization import get
            response = get(test_url, timeout=15)
            
            if response.status_code == 200:
                print(f"[+] Response: {response.status_code}")
                try:
                    data = response.json()
                    print(f"[+] Your IP appears as: {data.get('origin', 'unknown')}")
                except:
                    print(f"[+] Response received (non-JSON)")
            else:
                print(f"[!] Response: {response.status_code}")
        
        except Exception as e:
            print(f"[!] Test failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Bug Bounty Toolkit Controller")
    parser.add_argument('--enable-anon', action='store_true', 
                       help='Enable anonymous mode')
    parser.add_argument('--disable-anon', action='store_true',
                       help='Disable anonymous mode')
    parser.add_argument('--status', action='store_true',
                       help='Show anonymization status')
    parser.add_argument('--install-deps', action='store_true',
                       help='Install anonymization dependencies')
    parser.add_argument('--list-tools', action='store_true',
                       help='List available tools')
    parser.add_argument('--run', type=str,
                       help='Run a specific tool')
    parser.add_argument('--test', nargs='?', const='default',
                       help='Quick anonymity test (optional URL)')
    parser.add_argument('tool_args', nargs='*',
                       help='Arguments for the tool')
    
    args = parser.parse_args()
    
    controller = ToolkitController()
    
    if args.enable_anon:
        controller.enable_anonymous_mode()
    elif args.disable_anon:
        controller.disable_anonymous_mode()
    elif args.status:
        controller._show_anonymity_status()
    elif args.install_deps:
        controller.install_dependencies()
    elif args.list_tools:
        controller.list_tools()
    elif args.run:
        controller.run_tool(args.run, *args.tool_args)
    elif args.test:
        test_url = None if args.test == 'default' else args.test
        controller.quick_test(test_url)
    else:
        print("Bug Bounty Toolkit Controller")
        print("=" * 30)
        print(f"Current anonymization: {'ENABLED' if is_anonymous_mode() else 'DISABLED'}")
        print("\\nUsage examples:")
        print("  python3 toolkit_controller.py --enable-anon")
        print("  python3 toolkit_controller.py --status")
        print("  python3 toolkit_controller.py --run subdomain_exposure_hunter target.com")
        print("  python3 toolkit_controller.py --test")
        print("  python3 toolkit_controller.py --list-tools")
        parser.print_help()

if __name__ == "__main__":
    main()