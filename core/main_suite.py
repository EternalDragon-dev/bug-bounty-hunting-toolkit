#!/usr/bin/env python3

"""
🎯 Ultimate Bug Bounty Suite - Master CLI Interface
Unified reconnaissance, exploitation, and reporting framework

Usage:
    ./suite.py recon --target example.com --comprehensive
    ./suite.py exploit --target example.com --auto
    ./suite.py report --format hackerone --severity critical
    ./suite.py workflow --target example.com --full-chain
"""

import argparse
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add reconnaissance module to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'reconnaissance'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'exploitation'))
sys.path.insert(0, str(Path(__file__).parent))

from workflow_engine import WorkflowEngine
from target_manager import TargetManager
from evidence_collector import EvidenceCollector

class UltimateBugBountySuite:
    """Master orchestrator for the Ultimate Bug Bounty Suite"""
    
    def __init__(self):
        self.suite_root = Path(__file__).parent.parent
        self.target_manager = TargetManager(self.suite_root)
        self.workflow_engine = WorkflowEngine(self.suite_root)
        self.evidence_collector = EvidenceCollector(self.suite_root)
        
        # Print banner
        self.print_banner()
    
    def print_banner(self):
        """Print the suite banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║  🎯 ULTIMATE BUG BOUNTY SUITE v2.0                          ║
║                                                              ║
║  🔍 Advanced Reconnaissance → 💥 Active Exploitation        ║
║  🎯 Impact Validation → 📊 Professional Reporting           ║
║                                                              ║
║  From Information Gathering to $50,000+ Payouts             ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def reconnaissance_mode(self, args):
        """Execute reconnaissance workflow"""
        print(f"🔍 Starting reconnaissance on {args.target}")
        
        # Import and run recon scanner
        try:
            from scanner import WebReconScanner
            scanner = WebReconScanner()
            
            # Determine scan type
            if args.comprehensive:
                scan_type = "comprehensive"
            elif args.quick:
                scan_type = "quick"
            elif args.osint:
                scan_type = "osint"
            elif args.modern_web:
                scan_type = "modern_web"
            else:
                scan_type = "standard"
            
            # Execute reconnaissance
            results = scanner.scan(args.target, scan_type)
            
            # Store results
            self.target_manager.store_recon_results(args.target, results, scan_type)
            
            print(f"✅ Reconnaissance completed. Results stored in results/reconnaissance/{args.target}/")
            
            if args.auto_exploit:
                print("🚀 Auto-exploitation enabled. Starting exploitation phase...")
                args.target = args.target  # Pass target to exploitation
                self.exploitation_mode(args)
                
        except ImportError as e:
            print(f"❌ Error importing reconnaissance modules: {e}")
            print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
    
    def exploitation_mode(self, args):
        """Execute exploitation workflow"""
        print(f"💥 Starting exploitation on {args.target}")
        
        # Load reconnaissance results if available
        recon_data = self.target_manager.load_recon_results(args.target)
        
        if recon_data:
            print("📊 Using reconnaissance data to guide exploitation")
            targets = self.workflow_engine.identify_exploitation_targets(recon_data)
        else:
            print("⚠️  No reconnaissance data found. Running basic exploitation...")
            targets = [{"url": f"https://{args.target}", "type": "web"}]
        
        # Execute exploitation workflow
        vulnerabilities = self.workflow_engine.execute_exploitation(targets, args)
        
        # Validate and collect evidence
        validated_vulns = self.evidence_collector.validate_vulnerabilities(vulnerabilities)
        
        # Store results
        self.target_manager.store_exploitation_results(args.target, validated_vulns)
        
        print(f"✅ Exploitation completed. Found {len(validated_vulns)} validated vulnerabilities")
        
        if args.auto_report:
            print("📊 Auto-reporting enabled. Generating reports...")
            args.format = "hackerone"
            self.reporting_mode(args)
    
    def reporting_mode(self, args):
        """Generate professional reports"""
        print(f"📊 Generating {args.format} reports for {args.target}")
        
        # Load vulnerability data
        vuln_data = self.target_manager.load_exploitation_results(args.target)
        
        if not vuln_data:
            print("❌ No vulnerability data found. Run exploitation first.")
            return
        
        # Filter by severity if specified
        if args.severity:
            vuln_data = [v for v in vuln_data if v.get('severity', '').lower() == args.severity.lower()]
        
        # Generate reports
        reports = self.workflow_engine.generate_reports(vuln_data, args.format, args.target)
        
        print(f"✅ Generated {len(reports)} reports in results/reports/{args.target}/")
        
        # Display summary
        self.display_report_summary(reports)
    
    def workflow_mode(self, args):
        """Execute full workflow: recon → exploit → report"""
        print(f"🚀 Starting full workflow on {args.target}")
        
        # Phase 1: Reconnaissance
        print("\n" + "="*60)
        print("📡 PHASE 1: ADVANCED RECONNAISSANCE")
        print("="*60)
        args.comprehensive = True
        args.auto_exploit = True
        self.reconnaissance_mode(args)
        
        # Phase 2: Exploitation (triggered automatically)
        print("\n" + "="*60)
        print("💥 PHASE 2: VULNERABILITY EXPLOITATION")
        print("="*60)
        # Already executed via auto_exploit
        
        # Phase 3: Professional Reporting
        print("\n" + "="*60)
        print("📊 PHASE 3: PROFESSIONAL REPORTING")
        print("="*60)
        args.format = "hackerone"
        args.auto_report = True
        self.reporting_mode(args)
        
        print("\n🎯 FULL WORKFLOW COMPLETED!")
        print(f"📁 All results available in results/{args.target}/")
    
    def display_report_summary(self, reports):
        """Display summary of generated reports"""
        print("\n📋 REPORT SUMMARY:")
        print("-" * 50)
        
        total_critical = sum(1 for r in reports if r.get('severity') == 'Critical')
        total_high = sum(1 for r in reports if r.get('severity') == 'High')
        total_medium = sum(1 for r in reports if r.get('severity') == 'Medium')
        
        print(f"🔴 Critical: {total_critical}")
        print(f"🟠 High: {total_high}")
        print(f"🟡 Medium: {total_medium}")
        print(f"📊 Total Reports: {len(reports)}")
        
        if total_critical > 0:
            print(f"\n💰 Estimated Value: ${total_critical * 10000 + total_high * 3000 + total_medium * 1000:,}")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Ultimate Bug Bounty Suite - Reconnaissance, Exploitation & Reporting",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='Operation modes')
    
    # Reconnaissance mode
    recon_parser = subparsers.add_parser('recon', help='Advanced reconnaissance')
    recon_parser.add_argument('--target', required=True, help='Target domain or URL')
    recon_parser.add_argument('--comprehensive', action='store_true', help='Comprehensive scan')
    recon_parser.add_argument('--quick', action='store_true', help='Quick scan')
    recon_parser.add_argument('--osint', action='store_true', help='OSINT-focused scan')
    recon_parser.add_argument('--modern-web', action='store_true', help='Modern web technologies scan')
    recon_parser.add_argument('--auto-exploit', action='store_true', help='Automatically start exploitation')
    
    # Exploitation mode
    exploit_parser = subparsers.add_parser('exploit', help='Vulnerability exploitation')
    exploit_parser.add_argument('--target', required=True, help='Target domain or URL')
    exploit_parser.add_argument('--auto', action='store_true', help='Automatic exploitation based on recon')
    exploit_parser.add_argument('--sqli', action='store_true', help='Focus on SQL injection')
    exploit_parser.add_argument('--xss', action='store_true', help='Focus on XSS')
    exploit_parser.add_argument('--idor', action='store_true', help='Focus on IDOR')
    exploit_parser.add_argument('--auth-bypass', action='store_true', help='Focus on authentication bypass')
    exploit_parser.add_argument('--auto-report', action='store_true', help='Automatically generate reports')
    
    # Reporting mode
    report_parser = subparsers.add_parser('report', help='Generate professional reports')
    report_parser.add_argument('--target', required=True, help='Target domain')
    report_parser.add_argument('--format', choices=['hackerone', 'bugcrowd', 'technical'], 
                              default='hackerone', help='Report format')
    report_parser.add_argument('--severity', choices=['critical', 'high', 'medium', 'low'], 
                              help='Filter by severity')
    
    # Full workflow mode
    workflow_parser = subparsers.add_parser('workflow', help='Full recon → exploit → report workflow')
    workflow_parser.add_argument('--target', required=True, help='Target domain or URL')
    workflow_parser.add_argument('--full-chain', action='store_true', help='Complete attack chain')
    
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        sys.exit(1)
    
    # Initialize suite
    suite = UltimateBugBountySuite()
    
    # Route to appropriate mode
    if args.mode == 'recon':
        suite.reconnaissance_mode(args)
    elif args.mode == 'exploit':
        suite.exploitation_mode(args)
    elif args.mode == 'report':
        suite.reporting_mode(args)
    elif args.mode == 'workflow':
        suite.workflow_mode(args)

if __name__ == "__main__":
    main()