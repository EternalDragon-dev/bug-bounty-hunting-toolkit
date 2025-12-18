#!/usr/bin/env python3
"""
Advanced Database Exposure Hunter - Data Exposure Discovery Tool
Discovers exposed databases (MongoDB, Redis, Elasticsearch, etc.) and tests for sensitive data
"""

import socket
import threading
import time
import json
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import re
import base64

class DatabaseHunter:
    def __init__(self, target, port_range="1-65535", threads=50):
        self.target = target
        self.threads = threads
        self.exposed_databases = []
        self.sensitive_data = []
        
        # Parse port range
        if "-" in port_range:
            start, end = map(int, port_range.split("-"))
            self.ports = list(range(start, end + 1))
        else:
            self.ports = [int(port_range)]
        
        # Database signatures and default ports
        self.database_signatures = {
            'mongodb': {
                'ports': [27017, 27018, 27019, 28017],
                'banner_regex': [b'MongoDB', b'ismaster'],
                'test_method': self._test_mongodb
            },
            'redis': {
                'ports': [6379, 6380],
                'banner_regex': [b'redis_version', b'+PONG'],
                'test_method': self._test_redis
            },
            'elasticsearch': {
                'ports': [9200, 9201, 9300],
                'banner_regex': [b'elasticsearch', b'"cluster_name"'],
                'test_method': self._test_elasticsearch
            },
            'memcached': {
                'ports': [11211, 11212],
                'banner_regex': [b'STAT version', b'END'],
                'test_method': self._test_memcached
            },
            'cassandra': {
                'ports': [9042, 9160, 7000],
                'banner_regex': [b'Cassandra', b'cql_version'],
                'test_method': self._test_cassandra
            },
            'couchdb': {
                'ports': [5984, 5985, 6984],
                'banner_regex': [b'couchdb', b'"version"'],
                'test_method': self._test_couchdb
            },
            'mysql': {
                'ports': [3306, 3307],
                'banner_regex': [b'mysql_native_password', b'\\x00\\x00\\x00'],
                'test_method': self._test_mysql
            },
            'postgresql': {
                'ports': [5432, 5433],
                'banner_regex': [b'PostgreSQL', b'FATAL'],
                'test_method': self._test_postgresql
            },
            'influxdb': {
                'ports': [8086, 8088],
                'banner_regex': [b'InfluxDB', b'"version"'],
                'test_method': self._test_influxdb
            },
            'rethinkdb': {
                'ports': [28015, 8080],
                'banner_regex': [b'RethinkDB', b'SUCCESS'],
                'test_method': self._test_rethinkdb
            }
        }
        
        # Sensitive data patterns
        self.sensitive_patterns = {
            'Credentials': [r'password', r'passwd', r'pwd', r'secret', r'token', r'key', r'auth'],
            'Personal Info': [r'email', r'phone', r'address', r'ssn', r'social', r'name', r'user'],
            'Financial': [r'card', r'payment', r'billing', r'transaction', r'account', r'balance'],
            'API Keys': [r'api_key', r'access_key', r'secret_key', r'jwt', r'bearer'],
            'Database Configs': [r'connection', r'database', r'host', r'port', r'username']
        }

    def scan_port(self, port):
        """Scan a single port for database services"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((self.target, port))
            
            if result == 0:
                # Port is open, try to identify service
                try:
                    # Send basic probe
                    sock.send(b'\r\n')
                    banner = sock.recv(1024)
                    
                    # Check against database signatures
                    for db_type, signature in self.database_signatures.items():
                        if port in signature['ports']:
                            for regex in signature['banner_regex']:
                                if regex in banner:
                                    sock.close()
                                    return {'port': port, 'type': db_type, 'banner': banner.decode('utf-8', errors='ignore')}
                    
                    # Generic service detected
                    if banner:
                        sock.close()
                        return {'port': port, 'type': 'unknown', 'banner': banner.decode('utf-8', errors='ignore')}
                        
                except Exception:
                    pass
                    
            sock.close()
            
        except Exception:
            pass
            
        return None

    def _test_mongodb(self, host, port):
        """Test MongoDB for data exposure"""
        results = {
            'accessible': False,
            'authentication': False,
            'databases': [],
            'collections': [],
            'sample_data': [],
            'sensitive_data': [],
            'business_impact': {'severity': 'Low', 'findings': []}
        }
        
        try:
            # Try to connect without authentication
            import pymongo
            client = pymongo.MongoClient(host, port, serverSelectionTimeoutMS=5000)
            
            # Test connection
            client.admin.command('ismaster')
            results['accessible'] = True
            
            # List databases
            databases = client.list_database_names()
            results['databases'] = databases
            
            # Check each database
            for db_name in databases[:5]:  # Limit to first 5 databases
                if db_name in ['admin', 'local', 'config']:
                    continue
                    
                db = client[db_name]
                collections = db.list_collection_names()
                results['collections'].extend([f"{db_name}.{col}" for col in collections[:10]])
                
                # Sample data from collections
                for collection_name in collections[:3]:
                    try:
                        collection = db[collection_name]
                        sample = list(collection.find().limit(5))
                        
                        if sample:
                            results['sample_data'].extend([
                                {'database': db_name, 'collection': collection_name, 'data': str(doc)[:500]}
                                for doc in sample
                            ])
                            
                            # Check for sensitive data
                            for doc in sample:
                                for category, patterns in self.sensitive_patterns.items():
                                    for pattern in patterns:
                                        if re.search(pattern, str(doc), re.IGNORECASE):
                                            results['sensitive_data'].append({
                                                'category': category,
                                                'pattern': pattern,
                                                'location': f"{db_name}.{collection_name}",
                                                'sample': str(doc)[:200]
                                            })
                    except Exception:
                        pass
                        
            client.close()
            
        except ImportError:
            # Fallback to HTTP API if available
            try:
                response = requests.get(f"http://{host}:28017/", timeout=5)
                if response.status_code == 200 and 'MongoDB' in response.text:
                    results['accessible'] = True
                    results['business_impact']['findings'].append("HTTP interface exposed")
            except Exception:
                pass
                
        except Exception as e:
            results['error'] = str(e)
            
        # Assess business impact
        if results['accessible']:
            results['business_impact']['severity'] = 'High'
            results['business_impact']['findings'].append("Database accessible without authentication")
            
            if results['sensitive_data']:
                results['business_impact']['severity'] = 'Critical'
                results['business_impact']['findings'].append(f"Sensitive data exposed: {len(results['sensitive_data'])} instances")
                
        return results

    def _test_redis(self, host, port):
        """Test Redis for data exposure"""
        results = {
            'accessible': False,
            'authentication': False,
            'keys': [],
            'sample_data': [],
            'sensitive_data': [],
            'business_impact': {'severity': 'Low', 'findings': []}
        }
        
        try:
            import redis
            client = redis.Redis(host=host, port=port, socket_timeout=5, decode_responses=True)
            
            # Test connection
            client.ping()
            results['accessible'] = True
            
            # Get key information
            info = client.info()
            results['info'] = {
                'version': info.get('redis_version'),
                'keys': info.get('db0', {}).get('keys', 0) if 'db0' in info else 0
            }
            
            # Sample keys
            keys = client.keys('*')[:50]  # Limit to first 50 keys
            results['keys'] = keys
            
            # Sample data
            for key in keys[:10]:
                try:
                    key_type = client.type(key)
                    if key_type == 'string':
                        value = client.get(key)
                    elif key_type == 'hash':
                        value = client.hgetall(key)
                    elif key_type == 'list':
                        value = client.lrange(key, 0, 4)
                    elif key_type == 'set':
                        value = list(client.smembers(key))[:5]
                    else:
                        value = f"Type: {key_type}"
                        
                    results['sample_data'].append({
                        'key': key,
                        'type': key_type,
                        'value': str(value)[:500]
                    })
                    
                    # Check for sensitive data
                    for category, patterns in self.sensitive_patterns.items():
                        for pattern in patterns:
                            if re.search(pattern, f"{key} {value}", re.IGNORECASE):
                                results['sensitive_data'].append({
                                    'category': category,
                                    'pattern': pattern,
                                    'key': key,
                                    'sample': str(value)[:200]
                                })
                                
                except Exception:
                    pass
                    
        except ImportError:
            # Fallback to raw socket
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((host, port))
                
                # Send PING command
                sock.send(b'*1\r\n$4\r\nPING\r\n')
                response = sock.recv(1024)
                
                if b'+PONG' in response:
                    results['accessible'] = True
                    
                sock.close()
                
            except Exception:
                pass
                
        except Exception as e:
            results['error'] = str(e)
            
        # Assess business impact
        if results['accessible']:
            results['business_impact']['severity'] = 'High'
            results['business_impact']['findings'].append("Redis accessible without authentication")
            
            if results['sensitive_data']:
                results['business_impact']['severity'] = 'Critical'
                results['business_impact']['findings'].append(f"Sensitive data exposed: {len(results['sensitive_data'])} instances")
                
        return results

    def _test_elasticsearch(self, host, port):
        """Test Elasticsearch for data exposure"""
        results = {
            'accessible': False,
            'version': None,
            'indices': [],
            'sample_data': [],
            'sensitive_data': [],
            'business_impact': {'severity': 'Low', 'findings': []}
        }
        
        try:
            # Test basic connection
            response = requests.get(f"http://{host}:{port}/", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                results['accessible'] = True
                results['version'] = data.get('version', {}).get('number')
                results['cluster_name'] = data.get('cluster_name')
                
                # Get indices
                indices_response = requests.get(f"http://{host}:{port}/_cat/indices?format=json", timeout=5)
                if indices_response.status_code == 200:
                    indices = indices_response.json()
                    results['indices'] = [idx.get('index') for idx in indices]
                    
                    # Sample data from indices
                    for index in results['indices'][:5]:
                        try:
                            search_response = requests.get(
                                f"http://{host}:{port}/{index}/_search?size=5", 
                                timeout=5
                            )
                            
                            if search_response.status_code == 200:
                                search_data = search_response.json()
                                hits = search_data.get('hits', {}).get('hits', [])
                                
                                for hit in hits:
                                    source = hit.get('_source', {})
                                    results['sample_data'].append({
                                        'index': index,
                                        'type': hit.get('_type'),
                                        'data': str(source)[:500]
                                    })
                                    
                                    # Check for sensitive data
                                    for category, patterns in self.sensitive_patterns.items():
                                        for pattern in patterns:
                                            if re.search(pattern, str(source), re.IGNORECASE):
                                                results['sensitive_data'].append({
                                                    'category': category,
                                                    'pattern': pattern,
                                                    'index': index,
                                                    'sample': str(source)[:200]
                                                })
                                                
                        except Exception:
                            pass
                            
        except Exception as e:
            results['error'] = str(e)
            
        # Assess business impact
        if results['accessible']:
            results['business_impact']['severity'] = 'Medium'
            results['business_impact']['findings'].append("Elasticsearch accessible without authentication")
            
            if results['sensitive_data']:
                results['business_impact']['severity'] = 'Critical'
                results['business_impact']['findings'].append(f"Sensitive data exposed: {len(results['sensitive_data'])} instances")
                
        return results

    def _test_memcached(self, host, port):
        """Test Memcached for data exposure"""
        results = {
            'accessible': False,
            'version': None,
            'stats': {},
            'keys': [],
            'business_impact': {'severity': 'Low', 'findings': []}
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            
            # Get version
            sock.send(b'version\r\n')
            version_response = sock.recv(1024).decode('utf-8', errors='ignore')
            
            if 'VERSION' in version_response:
                results['accessible'] = True
                results['version'] = version_response.strip()
                
                # Get stats
                sock.send(b'stats\r\n')
                stats_response = sock.recv(4096).decode('utf-8', errors='ignore')
                
                stats = {}
                for line in stats_response.split('\n'):
                    if line.startswith('STAT'):
                        parts = line.split(' ', 2)
                        if len(parts) >= 3:
                            stats[parts[1]] = parts[2]
                            
                results['stats'] = stats
                
            sock.close()
            
        except Exception as e:
            results['error'] = str(e)
            
        # Assess business impact
        if results['accessible']:
            results['business_impact']['severity'] = 'Medium'
            results['business_impact']['findings'].append("Memcached accessible without authentication")
            
        return results

    def _test_cassandra(self, host, port):
        """Test Cassandra for data exposure"""
        results = {
            'accessible': False,
            'version': None,
            'keyspaces': [],
            'business_impact': {'severity': 'Low', 'findings': []}
        }
        
        try:
            # Try CQL native protocol
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            
            # Send basic CQL handshake
            sock.send(b'\x04\x00\x00\x00\x01\x00\x00\x00\x00')
            response = sock.recv(1024)
            
            if response:
                results['accessible'] = True
                results['business_impact']['severity'] = 'Medium'
                results['business_impact']['findings'].append("Cassandra port accessible")
                
            sock.close()
            
        except Exception as e:
            results['error'] = str(e)
            
        return results

    def _test_couchdb(self, host, port):
        """Test CouchDB for data exposure"""
        results = {
            'accessible': False,
            'version': None,
            'databases': [],
            'sample_data': [],
            'sensitive_data': [],
            'business_impact': {'severity': 'Low', 'findings': []}
        }
        
        try:
            # Test basic connection
            response = requests.get(f"http://{host}:{port}/", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'couchdb' in data:
                    results['accessible'] = True
                    results['version'] = data.get('version')
                    
                    # Get databases
                    db_response = requests.get(f"http://{host}:{port}/_all_dbs", timeout=5)
                    if db_response.status_code == 200:
                        results['databases'] = db_response.json()
                        
                        # Sample data from databases
                        for database in results['databases'][:5]:
                            if database.startswith('_'):
                                continue
                                
                            try:
                                docs_response = requests.get(
                                    f"http://{host}:{port}/{database}/_all_docs?limit=5&include_docs=true",
                                    timeout=5
                                )
                                
                                if docs_response.status_code == 200:
                                    docs_data = docs_response.json()
                                    rows = docs_data.get('rows', [])
                                    
                                    for row in rows:
                                        doc = row.get('doc', {})
                                        results['sample_data'].append({
                                            'database': database,
                                            'id': doc.get('_id'),
                                            'data': str(doc)[:500]
                                        })
                                        
                                        # Check for sensitive data
                                        for category, patterns in self.sensitive_patterns.items():
                                            for pattern in patterns:
                                                if re.search(pattern, str(doc), re.IGNORECASE):
                                                    results['sensitive_data'].append({
                                                        'category': category,
                                                        'pattern': pattern,
                                                        'database': database,
                                                        'sample': str(doc)[:200]
                                                    })
                                                    
                            except Exception:
                                pass
                                
        except Exception as e:
            results['error'] = str(e)
            
        # Assess business impact
        if results['accessible']:
            results['business_impact']['severity'] = 'Medium'
            results['business_impact']['findings'].append("CouchDB accessible without authentication")
            
            if results['sensitive_data']:
                results['business_impact']['severity'] = 'Critical'
                results['business_impact']['findings'].append(f"Sensitive data exposed: {len(results['sensitive_data'])} instances")
                
        return results

    def _test_mysql(self, host, port):
        """Test MySQL for data exposure"""
        results = {
            'accessible': False,
            'version': None,
            'business_impact': {'severity': 'Low', 'findings': []}
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            
            # Read initial handshake packet
            response = sock.recv(1024)
            
            if len(response) > 5:
                # Parse MySQL handshake packet
                if response[4] == 10:  # Protocol version 10
                    results['accessible'] = True
                    # Extract version string
                    version_end = response.find(b'\x00', 5)
                    if version_end > 5:
                        results['version'] = response[5:version_end].decode('utf-8', errors='ignore')
                        
            sock.close()
            
        except Exception as e:
            results['error'] = str(e)
            
        # Assess business impact
        if results['accessible']:
            results['business_impact']['severity'] = 'Medium'
            results['business_impact']['findings'].append("MySQL port accessible")
            
        return results

    def _test_postgresql(self, host, port):
        """Test PostgreSQL for data exposure"""
        results = {
            'accessible': False,
            'version': None,
            'business_impact': {'severity': 'Low', 'findings': []}
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            
            # Send startup message
            startup_msg = b'\x00\x00\x00\x08\x04\xd2\x16\x2f'
            sock.send(startup_msg)
            
            response = sock.recv(1024)
            
            if b'FATAL' in response or b'postgres' in response.lower():
                results['accessible'] = True
                
            sock.close()
            
        except Exception as e:
            results['error'] = str(e)
            
        # Assess business impact
        if results['accessible']:
            results['business_impact']['severity'] = 'Medium'
            results['business_impact']['findings'].append("PostgreSQL port accessible")
            
        return results

    def _test_influxdb(self, host, port):
        """Test InfluxDB for data exposure"""
        results = {
            'accessible': False,
            'version': None,
            'databases': [],
            'business_impact': {'severity': 'Low', 'findings': []}
        }
        
        try:
            # Test HTTP API
            response = requests.get(f"http://{host}:{port}/ping", timeout=5)
            
            if response.status_code == 204 and 'X-Influxdb-Version' in response.headers:
                results['accessible'] = True
                results['version'] = response.headers.get('X-Influxdb-Version')
                
                # Try to get databases
                db_response = requests.get(f"http://{host}:{port}/query?q=SHOW+DATABASES", timeout=5)
                if db_response.status_code == 200:
                    data = db_response.json()
                    if 'results' in data and data['results']:
                        series = data['results'][0].get('series', [])
                        if series and 'values' in series[0]:
                            results['databases'] = [db[0] for db in series[0]['values']]
                            
        except Exception as e:
            results['error'] = str(e)
            
        # Assess business impact
        if results['accessible']:
            results['business_impact']['severity'] = 'Medium'
            results['business_impact']['findings'].append("InfluxDB accessible without authentication")
            
        return results

    def _test_rethinkdb(self, host, port):
        """Test RethinkDB for data exposure"""
        results = {
            'accessible': False,
            'version': None,
            'business_impact': {'severity': 'Low', 'findings': []}
        }
        
        try:
            # Test RethinkDB protocol
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            
            # Send RethinkDB handshake
            handshake = b'\xc3\xbd\xc2\x34' + b'\x00' * 4  # Version + auth length
            sock.send(handshake)
            
            response = sock.recv(1024)
            if b'SUCCESS' in response:
                results['accessible'] = True
                
            sock.close()
            
        except Exception as e:
            results['error'] = str(e)
            
        # Also test web interface
        try:
            web_response = requests.get(f"http://{host}:8080/", timeout=5)
            if web_response.status_code == 200 and 'RethinkDB' in web_response.text:
                results['web_interface'] = True
                if not results['accessible']:
                    results['accessible'] = True
                    
        except Exception:
            pass
            
        # Assess business impact
        if results['accessible']:
            results['business_impact']['severity'] = 'Medium'
            results['business_impact']['findings'].append("RethinkDB accessible")
            
        return results

    def hunt_databases(self):
        """Main database hunting function"""
        print(f"[+] Starting database hunt on {self.target}")
        print(f"[+] Scanning {len(self.ports)} ports with {self.threads} threads")
        
        open_ports = []
        
        # First pass: port scanning
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_port = {
                executor.submit(self.scan_port, port): port 
                for port in self.ports
            }
            
            for future in as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    result = future.result()
                    if result:
                        print(f"[!] Found service on port {result['port']}: {result['type']}")
                        open_ports.append(result)
                except Exception as e:
                    pass
        
        print(f"\n[+] Found {len(open_ports)} database services, testing for exposure...")
        
        # Second pass: database-specific testing
        for service in open_ports:
            if service['type'] in self.database_signatures:
                test_method = self.database_signatures[service['type']]['test_method']
                
                try:
                    print(f"[+] Testing {service['type']} on port {service['port']}")
                    results = test_method(self.target, service['port'])
                    
                    if results.get('accessible'):
                        service.update(results)
                        service['business_impact'] = results['business_impact']
                        self.exposed_databases.append(service)
                        
                        print(f"[!] {service['type']} EXPOSED on port {service['port']}")
                        print(f"    Severity: {results['business_impact']['severity']}")
                        
                except Exception as e:
                    print(f"[!] Error testing {service['type']}: {e}")
                    
        return self.exposed_databases

    def generate_report(self):
        """Generate comprehensive database exposure report"""
        report = {
            'target': self.target,
            'scan_time': datetime.now().isoformat(),
            'summary': {
                'total_databases_found': len(self.exposed_databases),
                'critical_exposures': len([db for db in self.exposed_databases 
                                         if db.get('business_impact', {}).get('severity') == 'Critical']),
                'high_exposures': len([db for db in self.exposed_databases 
                                     if db.get('business_impact', {}).get('severity') == 'High']),
                'medium_exposures': len([db for db in self.exposed_databases 
                                       if db.get('business_impact', {}).get('severity') == 'Medium'])
            },
            'exposed_databases': self.exposed_databases
        }
        
        # Calculate overall severity
        severities = [db.get('business_impact', {}).get('severity', 'Low') for db in self.exposed_databases]
        
        if 'Critical' in severities:
            report['overall_severity'] = 'Critical'
        elif 'High' in severities:
            report['overall_severity'] = 'High'
        elif 'Medium' in severities:
            report['overall_severity'] = 'Medium'
        else:
            report['overall_severity'] = 'Low'
            
        return report

    def save_report(self, filename=None):
        """Save detailed report"""
        if not filename:
            filename = f"database_hunt_{self.target.replace('.', '_')}_{int(time.time())}.json"
            
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n[+] Report saved to {filename}")
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced Database Exposure Hunter')
    parser.add_argument('target', help='Target IP or domain to scan')
    parser.add_argument('-p', '--ports', default='1-65535', 
                       help='Port range to scan (default: 1-65535)')
    parser.add_argument('-t', '--threads', type=int, default=50, 
                       help='Number of threads (default: 50)')
    parser.add_argument('-o', '--output', help='Output file for report')
    
    args = parser.parse_args()
    
    hunter = DatabaseHunter(args.target, args.ports, args.threads)
    databases = hunter.hunt_databases()
    
    print(f"\n{'='*60}")
    print("DATABASE EXPOSURE HUNTING RESULTS")
    print(f"{'='*60}")
    
    if not databases:
        print("[-] No exposed databases found")
        return
        
    for db in databases:
        print(f"\n[!] {db['type'].upper()} - Port {db['port']}")
        print(f"    Version: {db.get('version', 'Unknown')}")
        print(f"    Severity: {db.get('business_impact', {}).get('severity', 'Unknown')}")
        
        # Show specific findings
        findings = db.get('business_impact', {}).get('findings', [])
        for finding in findings:
            print(f"    - {finding}")
            
        # Show sensitive data summary
        sensitive_data = db.get('sensitive_data', [])
        if sensitive_data:
            categories = {}
            for item in sensitive_data:
                cat = item['category']
                categories[cat] = categories.get(cat, 0) + 1
                
            print(f"    Sensitive Data Categories:")
            for category, count in categories.items():
                print(f"      - {category}: {count} instances")
    
    # Save report
    report = hunter.save_report(args.output)
    print(f"\n[+] Overall Severity: {report['overall_severity']}")
    print(f"[+] Total Exposed Databases: {report['summary']['total_databases_found']}")

if __name__ == '__main__':
    main()