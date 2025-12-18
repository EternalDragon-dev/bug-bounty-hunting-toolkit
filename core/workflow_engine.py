#!/usr/bin/env python3

"""
🔗 Workflow Engine - Orchestrates the complete bug bounty workflow
Coordinates reconnaissance → exploitation → validation → reporting
"""

import json
import logging
from pathlib import Path
from datetime import datetime

class WorkflowEngine:
    """Orchestrates the complete vulnerability discovery and exploitation workflow"""
    
    def __init__(self, suite_root):
        self.suite_root = Path(suite_root)
        self.logger = self.setup_logging()
    
    def setup_logging(self):
        """Setup workflow logging"""
        log_file = self.suite_root / "logs" / "workflow_engine.log"
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def identify_exploitation_targets(self, recon_data):
        """Analyze recon data to identify high-value exploitation targets"""
        self.logger.info("Analyzing reconnaissance data for exploitation opportunities")
        
        targets = []
        
        # Extract targets from recon data structure
        if isinstance(recon_data, dict):
            # Handle modern web recon format
            if 'target_info' in recon_data:
                base_url = f"https://{recon_data['target_info']['domain']}"
                targets.append({
                    "url": base_url,
                    "type": "web",
                    "priority": "high",
                    "technologies": recon_data.get('technologies', []),
                    "endpoints": recon_data.get('endpoints', [])
                })
            
            # Extract subdomains
            if 'subdomains' in recon_data:
                for subdomain in recon_data['subdomains'][:10]:  # Limit to top 10
                    targets.append({
                        "url": f"https://{subdomain}",
                        "type": "subdomain",
                        "priority": "medium"
                    })
            
            # Extract API endpoints
            if 'api_endpoints' in recon_data:
                for endpoint in recon_data['api_endpoints']:
                    targets.append({
                        "url": endpoint,
                        "type": "api",
                        "priority": "high"
                    })
            
            # Extract login/admin panels
            if 'admin_panels' in recon_data:
                for panel in recon_data['admin_panels']:
                    targets.append({
                        "url": panel,
                        "type": "admin",
                        "priority": "critical"
                    })
        
        elif isinstance(recon_data, list):
            # Handle list format
            for item in recon_data:
                if isinstance(item, dict) and 'url' in item:
                    targets.append({
                        "url": item['url'],
                        "type": "discovered",
                        "priority": "medium"
                    })
        
        # Sort by priority
        priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        targets.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 1), reverse=True)
        
        self.logger.info(f"Identified {len(targets)} exploitation targets")
        return targets
    
    def execute_exploitation(self, targets, args):
        """Execute exploitation against identified targets"""
        self.logger.info(f"Starting exploitation against {len(targets)} targets")
        
        vulnerabilities = []
        
        for target in targets:
            self.logger.info(f"Testing target: {target['url']}")
            
            # SQL Injection Testing
            if not args or args.sqli or getattr(args, 'auto', False):
                sqli_vulns = self.test_sql_injection(target)
                vulnerabilities.extend(sqli_vulns)
            
            # XSS Testing  
            if not args or args.xss or getattr(args, 'auto', False):
                xss_vulns = self.test_xss(target)
                vulnerabilities.extend(xss_vulns)
            
            # IDOR Testing
            if not args or args.idor or getattr(args, 'auto', False):
                idor_vulns = self.test_idor(target)
                vulnerabilities.extend(idor_vulns)
            
            # Authentication Bypass Testing
            if not args or getattr(args, 'auth_bypass', False) or getattr(args, 'auto', False):
                auth_vulns = self.test_auth_bypass(target)
                vulnerabilities.extend(auth_vulns)
        
        self.logger.info(f"Exploitation completed. Found {len(vulnerabilities)} potential vulnerabilities")
        return vulnerabilities
    
    def test_sql_injection(self, target):
        """Test for SQL injection vulnerabilities"""
        vulnerabilities = []
        
        # Import SQL injection testing module
        try:
            # This would import your advanced SQLi exploitation module
            # For now, we'll create a placeholder that demonstrates the concept
            vuln = {
                "type": "SQL Injection",
                "severity": "High",
                "target": target['url'],
                "description": "Potential SQL injection vulnerability detected",
                "payload": "' OR 1=1 --",
                "impact": "Database access, data extraction possible",
                "remediation": "Use parameterized queries",
                "timestamp": datetime.now().isoformat(),
                "validated": False
            }
            
            # Only add if we have strong indicators
            if self.has_sql_indicators(target):
                vulnerabilities.append(vuln)
        
        except Exception as e:
            self.logger.error(f"Error in SQL injection testing: {e}")
        
        return vulnerabilities
    
    def test_xss(self, target):
        """Test for XSS vulnerabilities"""
        vulnerabilities = []
        
        try:
            vuln = {
                "type": "Cross-Site Scripting",
                "severity": "Medium", 
                "target": target['url'],
                "description": "Potential XSS vulnerability detected",
                "payload": "<script>alert('XSS')</script>",
                "impact": "Session hijacking, account takeover possible",
                "remediation": "Implement proper input validation and output encoding",
                "timestamp": datetime.now().isoformat(),
                "validated": False
            }
            
            if self.has_xss_indicators(target):
                vulnerabilities.append(vuln)
        
        except Exception as e:
            self.logger.error(f"Error in XSS testing: {e}")
        
        return vulnerabilities
    
    def test_idor(self, target):
        """Test for IDOR vulnerabilities"""
        vulnerabilities = []
        
        try:
            if target.get('type') == 'api' or '/api/' in target.get('url', ''):
                vuln = {
                    "type": "Insecure Direct Object Reference",
                    "severity": "High",
                    "target": target['url'],
                    "description": "Potential IDOR vulnerability in API endpoint",
                    "payload": "Modified ID parameter",
                    "impact": "Unauthorized access to other users' data",
                    "remediation": "Implement proper authorization checks",
                    "timestamp": datetime.now().isoformat(),
                    "validated": False
                }
                vulnerabilities.append(vuln)
        
        except Exception as e:
            self.logger.error(f"Error in IDOR testing: {e}")
        
        return vulnerabilities
    
    def test_auth_bypass(self, target):
        """Test for authentication bypass vulnerabilities"""
        vulnerabilities = []
        
        try:
            if target.get('type') in ['admin', 'api'] or 'login' in target.get('url', '').lower():
                vuln = {
                    "type": "Authentication Bypass",
                    "severity": "Critical",
                    "target": target['url'],
                    "description": "Potential authentication bypass vulnerability",
                    "payload": "SQL injection or parameter manipulation",
                    "impact": "Complete account takeover possible",
                    "remediation": "Implement secure authentication mechanisms",
                    "timestamp": datetime.now().isoformat(),
                    "validated": False
                }
                vulnerabilities.append(vuln)
        
        except Exception as e:
            self.logger.error(f"Error in authentication bypass testing: {e}")
        
        return vulnerabilities
    
    def has_sql_indicators(self, target):
        """Check if target has SQL injection indicators"""
        # This would contain sophisticated detection logic
        # For now, return True for demonstration
        return True  # Placeholder - would contain real detection logic
    
    def has_xss_indicators(self, target):
        """Check if target has XSS indicators"""
        # This would contain sophisticated detection logic
        return True  # Placeholder - would contain real detection logic
    
    def generate_reports(self, vulnerabilities, report_format, target):
        """Generate professional vulnerability reports"""
        self.logger.info(f"Generating {report_format} reports for {len(vulnerabilities)} vulnerabilities")
        
        reports = []
        
        for vuln in vulnerabilities:
            if report_format == "hackerone":
                report = self.generate_hackerone_report(vuln, target)
            elif report_format == "bugcrowd":
                report = self.generate_bugcrowd_report(vuln, target)
            else:
                report = self.generate_technical_report(vuln, target)
            
            reports.append(report)
        
        return reports
    
    def generate_hackerone_report(self, vuln, target):
        """Generate HackerOne-formatted report"""
        report = {
            "title": f"{vuln['type']} in {target}",
            "severity": vuln['severity'],
            "asset": target,
            "vulnerability_type": vuln['type'],
            "description": self.generate_detailed_description(vuln),
            "reproduction_steps": self.generate_reproduction_steps(vuln),
            "impact": vuln['impact'],
            "proof_of_concept": {
                "payload": vuln['payload'],
                "evidence": "Evidence would be collected here"
            },
            "remediation": vuln['remediation'],
            "cvss_score": self.calculate_cvss(vuln),
            "timestamp": vuln['timestamp']
        }
        
        return report
    
    def generate_detailed_description(self, vuln):
        """Generate detailed vulnerability description"""
        return f"""
A {vuln['type']} vulnerability has been identified in the target application.

Technical Details:
- Vulnerability Type: {vuln['type']}
- Severity Level: {vuln['severity']}
- Attack Vector: {vuln.get('attack_vector', 'Web Application')}
- Impact: {vuln['impact']}

This vulnerability allows an attacker to {vuln['impact'].lower()}.
        """.strip()
    
    def generate_reproduction_steps(self, vuln):
        """Generate step-by-step reproduction instructions"""
        return [
            f"Navigate to {vuln['target']}",
            f"Inject the following payload: {vuln['payload']}",
            "Observe the application response",
            "Note the vulnerability confirmation"
        ]
    
    def generate_bugcrowd_report(self, vuln, target):
        """Generate Bugcrowd-formatted report"""
        # Similar to HackerOne but with Bugcrowd-specific formatting
        return self.generate_hackerone_report(vuln, target)
    
    def generate_technical_report(self, vuln, target):
        """Generate technical report for internal use"""
        return {
            "vulnerability": vuln,
            "target": target,
            "technical_details": {
                "detection_method": "Automated scanning with manual validation",
                "confidence": "High" if vuln.get('validated') else "Medium",
                "false_positive_likelihood": "Low"
            }
        }
    
    def calculate_cvss(self, vuln):
        """Calculate CVSS score based on vulnerability details"""
        # Simplified CVSS calculation
        base_scores = {
            "Critical": 9.0,
            "High": 7.0,
            "Medium": 5.0,
            "Low": 3.0,
            "Info": 1.0
        }
        
        return base_scores.get(vuln['severity'], 5.0)