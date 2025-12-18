#!/usr/bin/env python3

"""
🎯 Target Manager - Centralized target and results management
Handles storage, retrieval, and organization of scan results and evidence
"""

import json
import os
from datetime import datetime
from pathlib import Path
import logging

class TargetManager:
    """Centralized target and results management system"""
    
    def __init__(self, suite_root):
        self.suite_root = Path(suite_root)
        self.results_dir = self.suite_root / "results"
        
        # Ensure results directories exist
        self.ensure_directories()
        
        # Setup logging
        self.setup_logging()
    
    def ensure_directories(self):
        """Create necessary directory structure"""
        directories = [
            self.results_dir / "reconnaissance",
            self.results_dir / "vulnerabilities", 
            self.results_dir / "reports",
            self.results_dir / "evidence"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def setup_logging(self):
        """Setup logging for target manager"""
        log_file = self.suite_root / "logs" / "target_manager.log"
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def store_recon_results(self, target, results, scan_type):
        """Store reconnaissance results"""
        target_dir = self.results_dir / "reconnaissance" / target
        target_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Store main results
        results_file = target_dir / f"{scan_type}_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Create/update latest symlink
        latest_link = target_dir / "latest.json"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(results_file.name)
        
        # Store metadata
        metadata = {
            "target": target,
            "scan_type": scan_type,
            "timestamp": timestamp,
            "results_file": str(results_file),
            "total_findings": len(results) if isinstance(results, list) else 1
        }
        
        metadata_file = target_dir / f"metadata_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Stored recon results for {target}: {scan_type}")
        return results_file
    
    def load_recon_results(self, target):
        """Load latest reconnaissance results"""
        target_dir = self.results_dir / "reconnaissance" / target
        latest_file = target_dir / "latest.json"
        
        if not latest_file.exists():
            self.logger.warning(f"No recon results found for {target}")
            return None
        
        try:
            with open(latest_file, 'r') as f:
                results = json.load(f)
            
            self.logger.info(f"Loaded recon results for {target}")
            return results
        
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.error(f"Error loading recon results for {target}: {e}")
            return None
    
    def store_exploitation_results(self, target, vulnerabilities):
        """Store exploitation results"""
        target_dir = self.results_dir / "vulnerabilities" / target
        target_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Store vulnerabilities
        vulns_file = target_dir / f"vulnerabilities_{timestamp}.json"
        with open(vulns_file, 'w') as f:
            json.dump(vulnerabilities, f, indent=2, default=str)
        
        # Create/update latest symlink
        latest_link = target_dir / "latest_vulns.json"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(vulns_file.name)
        
        # Store summary
        summary = {
            "target": target,
            "timestamp": timestamp,
            "total_vulnerabilities": len(vulnerabilities),
            "by_severity": self.count_by_severity(vulnerabilities),
            "by_type": self.count_by_type(vulnerabilities),
            "high_impact": [v for v in vulnerabilities if v.get('severity') in ['Critical', 'High']]
        }
        
        summary_file = target_dir / f"summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"Stored {len(vulnerabilities)} vulnerabilities for {target}")
        return vulns_file
    
    def load_exploitation_results(self, target):
        """Load latest exploitation results"""
        target_dir = self.results_dir / "vulnerabilities" / target
        latest_file = target_dir / "latest_vulns.json"
        
        if not latest_file.exists():
            self.logger.warning(f"No vulnerability results found for {target}")
            return None
        
        try:
            with open(latest_file, 'r') as f:
                results = json.load(f)
            
            self.logger.info(f"Loaded {len(results)} vulnerabilities for {target}")
            return results
        
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.error(f"Error loading vulnerability results for {target}: {e}")
            return None
    
    def store_reports(self, target, reports, report_format):
        """Store generated reports"""
        target_dir = self.results_dir / "reports" / target
        target_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Store individual reports
        report_files = []
        for i, report in enumerate(reports):
            report_file = target_dir / f"{report_format}_report_{i+1}_{timestamp}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            report_files.append(report_file)
        
        # Store report package
        package = {
            "target": target,
            "format": report_format,
            "timestamp": timestamp,
            "total_reports": len(reports),
            "report_files": [str(f) for f in report_files],
            "reports": reports
        }
        
        package_file = target_dir / f"{report_format}_package_{timestamp}.json"
        with open(package_file, 'w') as f:
            json.dump(package, f, indent=2, default=str)
        
        self.logger.info(f"Stored {len(reports)} {report_format} reports for {target}")
        return package_file
    
    def count_by_severity(self, vulnerabilities):
        """Count vulnerabilities by severity"""
        counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'Info')
            if severity in counts:
                counts[severity] += 1
        
        return counts
    
    def count_by_type(self, vulnerabilities):
        """Count vulnerabilities by type"""
        counts = {}
        
        for vuln in vulnerabilities:
            vuln_type = vuln.get('type', 'Unknown')
            counts[vuln_type] = counts.get(vuln_type, 0) + 1
        
        return counts
    
    def get_target_summary(self, target):
        """Get comprehensive summary for a target"""
        summary = {
            "target": target,
            "reconnaissance": None,
            "vulnerabilities": None,
            "reports": None,
            "last_updated": None
        }
        
        # Load recon data
        recon_data = self.load_recon_results(target)
        if recon_data:
            summary["reconnaissance"] = {
                "available": True,
                "findings": len(recon_data) if isinstance(recon_data, list) else 1
            }
        
        # Load vulnerability data
        vuln_data = self.load_exploitation_results(target)
        if vuln_data:
            summary["vulnerabilities"] = {
                "total": len(vuln_data),
                "by_severity": self.count_by_severity(vuln_data),
                "by_type": self.count_by_type(vuln_data)
            }
        
        # Check for reports
        reports_dir = self.results_dir / "reports" / target
        if reports_dir.exists():
            report_files = list(reports_dir.glob("*_package_*.json"))
            summary["reports"] = {
                "total_packages": len(report_files),
                "latest": max(report_files, key=os.path.getctime).name if report_files else None
            }
        
        return summary
    
    def list_targets(self):
        """List all targets with basic info"""
        targets = []
        
        # Check reconnaissance directory
        recon_dir = self.results_dir / "reconnaissance"
        if recon_dir.exists():
            for target_dir in recon_dir.iterdir():
                if target_dir.is_dir():
                    summary = self.get_target_summary(target_dir.name)
                    targets.append(summary)
        
        return targets
    
    def cleanup_old_results(self, target, days_old=30):
        """Clean up old results for a target"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cleaned_files = 0
        
        target_dirs = [
            self.results_dir / "reconnaissance" / target,
            self.results_dir / "vulnerabilities" / target,
            self.results_dir / "reports" / target
        ]
        
        for target_dir in target_dirs:
            if target_dir.exists():
                for file_path in target_dir.glob("*"):
                    if file_path.is_file() and not file_path.is_symlink():
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time < cutoff_date:
                            file_path.unlink()
                            cleaned_files += 1
        
        self.logger.info(f"Cleaned up {cleaned_files} old files for {target}")
        return cleaned_files