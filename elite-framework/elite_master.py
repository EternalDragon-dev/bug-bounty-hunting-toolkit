#!/usr/bin/env python3
"""
Elite Bug Bounty Master Orchestrator
Combines reconnaissance, exploitation, stealth, and professional reporting
"""

import asyncio
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import secrets
import traceback

# Import our elite modules
sys.path.append(str(Path(__file__).parent / 'core'))

from elite_recon_engine import EliteReconEngine, TargetIntel
from elite_exploitation_engine import EliteExploitationEngine, VulnerabilityProfile
from stealth_coordinator import EliteStealthController

# Professional reporting
from jinja2 import Template
import base64

class EliteBugBountyMaster:
    """Master orchestrator for elite bug bounty operations"""
    
    def __init__(self, target: str, config: Optional[Dict] = None):
        self.target = target
        self.config = config or {}
        self.operation_id = secrets.token_hex(8)
        self.start_time = datetime.now()
        
        # Initialize core engines
        self.recon_engine = EliteReconEngine()
        self.exploitation_engine = EliteExploitationEngine()
        self.stealth_controller = EliteStealthController()
        
        # Results storage
        self.intelligence = {}
        self.vulnerabilities = []
        self.evidence = []
        self.operation_log = []
        
        print(f"🎯 Elite Bug Bounty Master initialized")
        print(f"🔮 Operation ID: {self.operation_id}")
        print(f"🎪 Target: {self.target}")
        print(f"⏰ Started: {self.start_time}")
    
    async def execute_full_engagement(self, 
                                    reconnaissance: bool = True,
                                    exploitation: bool = True,
                                    stealth_mode: bool = True,
                                    generate_report: bool = True) -> Dict[str, Any]:
        """Execute full elite engagement"""
        
        results = {
            'operation_id': self.operation_id,
            'target': self.target,
            'start_time': self.start_time,
            'phases_completed': [],
            'intelligence': {},
            'vulnerabilities': [],
            'risk_score': 0.0,
            'confidence': 0.0,
            'evidence_count': 0,
            'report_path': None
        }
        
        try:
            # Phase 1: Elite Reconnaissance
            if reconnaissance:
                print(f"\n🔍 Phase 1: Elite Reconnaissance")
                print("=" * 50)
                
                intel = await self.recon_engine.comprehensive_reconnaissance(self.target)
                self.intelligence = self._convert_intel_to_dict(intel)
                results['intelligence'] = self.intelligence
                results['phases_completed'].append('reconnaissance')
                
                self._log_operation('reconnaissance_completed', {
                    'subdomains_found': len(intel.subdomains),
                    'technologies_detected': len(intel.technologies),
                    'risk_score': intel.risk_score
                })
                
                print(f"✅ Reconnaissance complete")
                print(f"📊 Risk Score: {intel.risk_score:.2f}")
                print(f"🌐 Subdomains: {len(intel.subdomains)}")
                print(f"🔧 Technologies: {len(intel.technologies)}")
            
            # Phase 2: Stealth Configuration
            if stealth_mode:
                print(f"\n🥷 Phase 2: Stealth Initialization")
                print("=" * 50)
                
                stealth_profiles = await self.stealth_controller.initialize_stealth_operation(
                    [self.target], 'full_engagement'
                )
                
                print(f"✅ Stealth profiles initialized")
                print(f"🕶️ Active sessions: {len(stealth_profiles)}")
                
                results['phases_completed'].append('stealth_initialization')
            
            # Phase 3: Elite Exploitation
            if exploitation:
                print(f"\n🚀 Phase 3: Elite Exploitation")
                print("=" * 50)
                
                target_url = f"https://{self.target}"
                vulnerabilities = await self.exploitation_engine.comprehensive_exploitation(
                    target_url, self.intelligence
                )
                
                self.vulnerabilities = [self._convert_vuln_to_dict(v) for v in vulnerabilities]
                results['vulnerabilities'] = self.vulnerabilities
                results['phases_completed'].append('exploitation')
                
                # Calculate overall risk
                if vulnerabilities:
                    risk_scores = []
                    for vuln in vulnerabilities:
                        if vuln.risk_level == 'high':
                            risk_scores.append(8.0)
                        elif vuln.risk_level == 'medium':
                            risk_scores.append(5.0)
                        elif vuln.risk_level == 'low':
                            risk_scores.append(2.0)
                        else:
                            risk_scores.append(1.0)
                    
                    results['risk_score'] = max(risk_scores) if risk_scores else 0.0
                    results['confidence'] = min(len(vulnerabilities) * 0.2, 1.0)
                
                self._log_operation('exploitation_completed', {
                    'vulnerabilities_found': len(vulnerabilities),
                    'high_risk_count': len([v for v in vulnerabilities if v.risk_level == 'high']),
                    'medium_risk_count': len([v for v in vulnerabilities if v.risk_level == 'medium'])
                })
                
                print(f"✅ Exploitation complete")
                print(f"🎯 Vulnerabilities found: {len(vulnerabilities)}")
                
                # Display vulnerability summary
                vuln_summary = {}
                for vuln in vulnerabilities:
                    vuln_type = vuln.vuln_type
                    if vuln_type not in vuln_summary:
                        vuln_summary[vuln_type] = {'count': 0, 'risk_levels': []}
                    vuln_summary[vuln_type]['count'] += 1
                    vuln_summary[vuln_type]['risk_levels'].append(vuln.risk_level)
                
                for vuln_type, info in vuln_summary.items():
                    risk_dist = {level: info['risk_levels'].count(level) for level in ['high', 'medium', 'low']}
                    print(f"  📋 {vuln_type}: {info['count']} (H:{risk_dist['high']}, M:{risk_dist['medium']}, L:{risk_dist['low']})")
            
            # Phase 4: Evidence Collection & Professional Reporting
            if generate_report:
                print(f"\n📊 Phase 4: Professional Reporting")
                print("=" * 50)
                
                report_path = await self._generate_professional_report(results)
                results['report_path'] = report_path
                results['phases_completed'].append('reporting')
                
                self._log_operation('reporting_completed', {
                    'report_path': report_path,
                    'total_findings': len(self.vulnerabilities)
                })
                
                print(f"✅ Professional report generated")
                print(f"📄 Report saved to: {report_path}")
            
            # Final summary
            results['end_time'] = datetime.now()
            results['total_duration'] = (results['end_time'] - self.start_time).total_seconds()
            results['evidence_count'] = len(self.evidence)
            
            return results
            
        except Exception as e:
            error_info = {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }
            
            self._log_operation('operation_error', error_info)
            results['error'] = error_info
            
            print(f"❌ Operation failed: {e}")
            return results
        
        finally:
            # Cleanup resources
            try:
                await self.recon_engine.cleanup()
                await self.exploitation_engine.cleanup()
                print(f"🧹 Resources cleaned up")
            except:
                pass
    
    def _convert_intel_to_dict(self, intel: TargetIntel) -> Dict[str, Any]:
        """Convert TargetIntel to dictionary"""
        return {
            'domain': intel.domain,
            'ip_addresses': list(intel.ip_addresses),
            'subdomains': list(intel.subdomains),
            'technologies': intel.technologies,
            'certificates': intel.certificates,
            'dns_records': intel.dns_records,
            'social_presence': intel.social_presence,
            'employees': intel.employees,
            'cloud_assets': intel.cloud_assets,
            'vulnerabilities': intel.vulnerabilities,
            'defense_mechanisms': intel.defense_mechanisms,
            'risk_score': intel.risk_score,
            'confidence': intel.confidence,
            'timestamp': intel.timestamp.isoformat()
        }
    
    def _convert_vuln_to_dict(self, vuln: VulnerabilityProfile) -> Dict[str, Any]:
        """Convert VulnerabilityProfile to dictionary"""
        return {
            'vuln_type': vuln.vuln_type,
            'target_url': vuln.target_url,
            'parameters': vuln.parameters,
            'payloads': [self._convert_payload_to_dict(p) for p in vuln.payloads],
            'success_indicators': vuln.success_indicators,
            'bypass_methods': vuln.bypass_methods,
            'risk_level': vuln.risk_level,
            'exploitation_difficulty': vuln.exploitation_difficulty,
            'remediation': vuln.remediation
        }
    
    def _convert_payload_to_dict(self, payload) -> Dict[str, Any]:
        """Convert ExploitPayload to dictionary"""
        return {
            'payload_type': payload.payload_type,
            'content': payload.content,
            'encoding': payload.encoding,
            'bypass_technique': payload.bypass_technique,
            'confidence': payload.confidence,
            'context': payload.context,
            'timestamp': payload.timestamp.isoformat()
        }
    
    def _log_operation(self, event_type: str, data: Dict[str, Any]):
        """Log operation event"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation_id': self.operation_id,
            'event_type': event_type,
            'data': data
        }
        self.operation_log.append(log_entry)
    
    async def _generate_professional_report(self, results: Dict[str, Any]) -> str:
        """Generate professional HackerOne-style report"""
        
        # Create reports directory
        reports_dir = Path(__file__).parent.parent / 'reports' / 'elite_reports'
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"elite_security_assessment_{self.target}_{timestamp}.html"
        report_path = reports_dir / report_filename
        
        # Professional HTML report template
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Security Assessment - {{ target }}</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --success-color: #059669;
            --warning-color: #d97706;
            --danger-color: #dc2626;
            --dark-bg: #1f2937;
            --light-bg: #f9fafb;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #374151;
            background-color: #ffffff;
        }
        
        .header {
            background: linear-gradient(135deg, var(--primary-color), #1d4ed8);
            color: white;
            padding: 2rem 0;
            text-align: center;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }
        
        .elite-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-size: 0.875rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        .report-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .report-subtitle {
            font-size: 1.25rem;
            opacity: 0.9;
        }
        
        .summary-section {
            background: var(--light-bg);
            padding: 2rem 0;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        
        .summary-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--primary-color);
        }
        
        .card-title {
            font-size: 0.875rem;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        
        .card-value {
            font-size: 2rem;
            font-weight: 700;
            color: #111827;
        }
        
        .content-section {
            padding: 2rem 0;
        }
        
        .section-title {
            font-size: 1.875rem;
            font-weight: 700;
            color: #111827;
            margin-bottom: 1rem;
            border-bottom: 3px solid var(--primary-color);
            padding-bottom: 0.5rem;
        }
        
        .vuln-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .vuln-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .vuln-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #111827;
        }
        
        .risk-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 50px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .risk-high {
            background-color: #fef2f2;
            color: var(--danger-color);
            border: 1px solid #fecaca;
        }
        
        .risk-medium {
            background-color: #fffbeb;
            color: var(--warning-color);
            border: 1px solid #fed7aa;
        }
        
        .risk-low {
            background-color: #f0f9ff;
            color: var(--primary-color);
            border: 1px solid #bae6fd;
        }
        
        .vuln-details {
            margin-top: 1rem;
        }
        
        .detail-section {
            margin-bottom: 1rem;
        }
        
        .detail-title {
            font-weight: 600;
            color: #374151;
            margin-bottom: 0.5rem;
        }
        
        .detail-content {
            color: #6b7280;
            background: #f9fafb;
            padding: 0.75rem;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.875rem;
        }
        
        .remediation-box {
            background: #f0f9ff;
            border: 1px solid #bae6fd;
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
        }
        
        .remediation-title {
            font-weight: 600;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }
        
        .footer {
            background: var(--dark-bg);
            color: white;
            text-align: center;
            padding: 2rem 0;
            margin-top: 3rem;
        }
        
        .timestamp {
            color: #9ca3af;
            font-size: 0.875rem;
        }
        
        .no-vulnerabilities {
            text-align: center;
            padding: 3rem 2rem;
            background: var(--light-bg);
            border-radius: 12px;
            margin: 2rem 0;
        }
        
        .no-vuln-icon {
            font-size: 4rem;
            color: var(--success-color);
            margin-bottom: 1rem;
        }
        
        .intelligence-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        
        .intel-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1.5rem;
        }
        
        .intel-title {
            font-weight: 600;
            color: #111827;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
        }
        
        .intel-icon {
            margin-right: 0.5rem;
        }
        
        .intel-list {
            list-style: none;
        }
        
        .intel-list li {
            padding: 0.25rem 0;
            color: #6b7280;
            border-bottom: 1px solid #f3f4f6;
        }
        
        .intel-list li:last-child {
            border-bottom: none;
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="elite-badge">🎯 Elite Security Assessment</div>
            <h1 class="report-title">Security Assessment Report</h1>
            <p class="report-subtitle">Target: {{ target }}</p>
        </div>
    </header>

    <section class="summary-section">
        <div class="container">
            <h2 class="section-title">Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="card-title">Overall Risk Score</div>
                    <div class="card-value" style="color: {% if risk_score >= 7.0 %}var(--danger-color){% elif risk_score >= 4.0 %}var(--warning-color){% else %}var(--success-color){% endif %}">
                        {{ "%.1f"|format(risk_score) }}/10.0
                    </div>
                </div>
                <div class="summary-card">
                    <div class="card-title">Vulnerabilities Found</div>
                    <div class="card-value">{{ vulnerabilities|length }}</div>
                </div>
                <div class="summary-card">
                    <div class="card-title">Confidence Level</div>
                    <div class="card-value">{{ "%.0f"|format(confidence * 100) }}%</div>
                </div>
                <div class="summary-card">
                    <div class="card-title">Assessment Duration</div>
                    <div class="card-value">{{ "%.0f"|format(total_duration/60) }}m</div>
                </div>
            </div>
        </div>
    </section>

    <section class="content-section">
        <div class="container">
            <h2 class="section-title">🔍 Intelligence Gathering Results</h2>
            
            <div class="intelligence-grid">
                {% if intelligence.subdomains %}
                <div class="intel-card">
                    <div class="intel-title">
                        <span class="intel-icon">🌐</span>
                        Subdomains ({{ intelligence.subdomains|length }})
                    </div>
                    <ul class="intel-list">
                        {% for subdomain in intelligence.subdomains[:10] %}
                        <li>{{ subdomain }}</li>
                        {% endfor %}
                        {% if intelligence.subdomains|length > 10 %}
                        <li><em>... and {{ intelligence.subdomains|length - 10 }} more</em></li>
                        {% endif %}
                    </ul>
                </div>
                {% endif %}
                
                {% if intelligence.technologies %}
                <div class="intel-card">
                    <div class="intel-title">
                        <span class="intel-icon">🔧</span>
                        Technologies Detected
                    </div>
                    <ul class="intel-list">
                        {% for tech, confidence in intelligence.technologies.items() %}
                        <li>{{ tech }} ({{ "%.1f"|format(confidence) }})</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}
                
                {% if intelligence.defense_mechanisms %}
                <div class="intel-card">
                    <div class="intel-title">
                        <span class="intel-icon">🛡️</span>
                        Defense Mechanisms
                    </div>
                    <ul class="intel-list">
                        {% for defense in intelligence.defense_mechanisms %}
                        <li>{{ defense }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}
                
                {% if intelligence.ip_addresses %}
                <div class="intel-card">
                    <div class="intel-title">
                        <span class="intel-icon">🌍</span>
                        IP Addresses
                    </div>
                    <ul class="intel-list">
                        {% for ip in intelligence.ip_addresses %}
                        <li>{{ ip }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}
            </div>
        </div>
    </section>

    <section class="content-section">
        <div class="container">
            <h2 class="section-title">🚨 Vulnerability Assessment Results</h2>
            
            {% if vulnerabilities %}
                {% for vuln in vulnerabilities %}
                <div class="vuln-card">
                    <div class="vuln-header">
                        <div>
                            <div class="vuln-title">{{ vuln.vuln_type.replace('_', ' ').title() }}</div>
                            <span class="risk-badge risk-{{ vuln.risk_level }}">{{ vuln.risk_level }} Risk</span>
                        </div>
                    </div>
                    
                    <div class="vuln-details">
                        <div class="detail-section">
                            <div class="detail-title">Target URL</div>
                            <div class="detail-content">{{ vuln.target_url }}</div>
                        </div>
                        
                        {% if vuln.parameters %}
                        <div class="detail-section">
                            <div class="detail-title">Affected Parameters</div>
                            <div class="detail-content">{{ vuln.parameters|join(', ') }}</div>
                        </div>
                        {% endif %}
                        
                        {% if vuln.success_indicators %}
                        <div class="detail-section">
                            <div class="detail-title">Success Indicators</div>
                            <div class="detail-content">{{ vuln.success_indicators|join(', ') }}</div>
                        </div>
                        {% endif %}
                        
                        {% if vuln.bypass_methods %}
                        <div class="detail-section">
                            <div class="detail-title">Bypass Methods Used</div>
                            <div class="detail-content">{{ vuln.bypass_methods|join(', ') }}</div>
                        </div>
                        {% endif %}
                        
                        <div class="detail-section">
                            <div class="detail-title">Exploitation Difficulty</div>
                            <div class="detail-content">{{ vuln.exploitation_difficulty.title() }}</div>
                        </div>
                        
                        <div class="remediation-box">
                            <div class="remediation-title">🔧 Remediation</div>
                            <div>{{ vuln.remediation }}</div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-vulnerabilities">
                    <div class="no-vuln-icon">🛡️</div>
                    <h3>No Critical Vulnerabilities Found</h3>
                    <p>The target appears to have strong security measures in place. Continue monitoring and consider deeper analysis of discovered technologies.</p>
                </div>
            {% endif %}
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <p><strong>Elite Security Assessment</strong> - Professional Bug Bounty Testing Framework</p>
            <p class="timestamp">Generated on {{ timestamp }} | Operation ID: {{ operation_id }}</p>
        </div>
    </footer>
</body>
</html>
        """
        
        # Render the template
        template = Template(html_template)
        html_content = template.render(
            target=self.target,
            operation_id=self.operation_id,
            timestamp=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            risk_score=results.get('risk_score', 0.0),
            confidence=results.get('confidence', 0.0),
            total_duration=results.get('total_duration', 0),
            vulnerabilities=results.get('vulnerabilities', []),
            intelligence=results.get('intelligence', {})
        )
        
        # Write the report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)

async def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Elite Bug Bounty Master - Advanced Security Assessment Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 elite_master.py example.com
  python3 elite_master.py example.com --no-exploitation
  python3 elite_master.py example.com --stealth-mode --full-engagement
  python3 elite_master.py example.com --reconnaissance-only
        """
    )
    
    parser.add_argument('target', help='Target domain to assess')
    parser.add_argument('--no-reconnaissance', action='store_true', 
                       help='Skip reconnaissance phase')
    parser.add_argument('--no-exploitation', action='store_true', 
                       help='Skip exploitation phase')
    parser.add_argument('--no-stealth', action='store_true', 
                       help='Disable stealth mode')
    parser.add_argument('--no-report', action='store_true', 
                       help='Skip report generation')
    parser.add_argument('--reconnaissance-only', action='store_true',
                       help='Only perform reconnaissance')
    parser.add_argument('--exploitation-only', action='store_true',
                       help='Only perform exploitation')
    parser.add_argument('--stealth-mode', action='store_true',
                       help='Enable maximum stealth (default: True)')
    parser.add_argument('--full-engagement', action='store_true',
                       help='Perform full engagement (all phases)')
    
    args = parser.parse_args()
    
    # Configure phases based on arguments
    if args.reconnaissance_only:
        reconnaissance = True
        exploitation = False
        stealth_mode = not args.no_stealth
        generate_report = not args.no_report
    elif args.exploitation_only:
        reconnaissance = False
        exploitation = True
        stealth_mode = not args.no_stealth
        generate_report = not args.no_report
    else:
        reconnaissance = not args.no_reconnaissance
        exploitation = not args.no_exploitation
        stealth_mode = not args.no_stealth or args.stealth_mode
        generate_report = not args.no_report
    
    print("🎯" + "="*70 + "🎯")
    print("🚀 ELITE BUG BOUNTY MASTER FRAMEWORK 🚀")
    print("🎯" + "="*70 + "🎯")
    print()
    print(f"🎪 Target: {args.target}")
    print(f"🔍 Reconnaissance: {'✅' if reconnaissance else '❌'}")
    print(f"🚀 Exploitation: {'✅' if exploitation else '❌'}")
    print(f"🥷 Stealth Mode: {'✅' if stealth_mode else '❌'}")
    print(f"📊 Generate Report: {'✅' if generate_report else '❌'}")
    print()
    
    # Initialize master controller
    master = EliteBugBountyMaster(args.target)
    
    try:
        # Execute engagement
        results = await master.execute_full_engagement(
            reconnaissance=reconnaissance,
            exploitation=exploitation,
            stealth_mode=stealth_mode,
            generate_report=generate_report
        )
        
        # Display final results
        print(f"\n" + "🎯" + "="*70 + "🎯")
        print("🏆 ELITE ENGAGEMENT COMPLETE 🏆")
        print("🎯" + "="*70 + "🎯")
        
        if 'error' in results:
            print(f"❌ Operation completed with errors:")
            print(f"   Error: {results['error']['error']}")
            return 1
        
        print(f"🎯 Operation ID: {results['operation_id']}")
        print(f"⏱️ Duration: {results.get('total_duration', 0):.1f} seconds")
        print(f"✅ Phases Completed: {', '.join(results['phases_completed'])}")
        print(f"📊 Overall Risk Score: {results.get('risk_score', 0.0):.1f}/10.0")
        print(f"🎯 Vulnerabilities Found: {len(results.get('vulnerabilities', []))}")
        print(f"🔍 Confidence Level: {results.get('confidence', 0.0):.1%}")
        
        if results.get('report_path'):
            print(f"📄 Professional Report: {results['report_path']}")
        
        if results.get('vulnerabilities'):
            print(f"\n🚨 Vulnerability Summary:")
            vuln_types = {}
            for vuln in results['vulnerabilities']:
                vtype = vuln['vuln_type']
                risk = vuln['risk_level']
                if vtype not in vuln_types:
                    vuln_types[vtype] = {'high': 0, 'medium': 0, 'low': 0}
                vuln_types[vtype][risk] += 1
            
            for vtype, counts in vuln_types.items():
                total = sum(counts.values())
                print(f"   📋 {vtype.replace('_', ' ').title()}: {total} "
                      f"(🔴{counts['high']} 🟡{counts['medium']} 🟢{counts['low']})")
        
        print(f"\n🎪 Elite Bug Bounty Master - Mission Accomplished! 🎪")
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)