#!/usr/bin/env python3
"""
Anonymous Communication CLI
==========================

Command-line interface for the Anonymous Communication system.
Provides easy access to secure communication channels for security research.

Usage:
    python anonymous_communication_cli.py [action] [options]

Examples:
    # Check system status
    python anonymous_communication_cli.py status

    # Test all communication channels
    python anonymous_communication_cli.py test

    # Send secure email
    python anonymous_communication_cli.py email -r recipient@example.com -s "Subject" -m "Message"

    # Share file anonymously
    python anonymous_communication_cli.py share -f report.pdf -p mypassword -e 48

    # Send emergency alert
    python anonymous_communication_cli.py emergency -m "Critical vulnerability detected"
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add core directory to path
script_dir = Path(__file__).parent
core_dir = script_dir.parent / "core"
sys.path.insert(0, str(core_dir))

try:
    from anonymous_communication import AnonymousCommunication
except ImportError as e:
    print(f"❌ Failed to import anonymous communication module: {e}")
    print("📍 Make sure you're running from the toolkit directory")
    sys.exit(1)


def format_status_output(status: dict) -> str:
    """Format status information for display"""
    output = []
    
    # Header
    output.append("📡 Anonymous Communication System Status")
    output.append("=" * 50)
    
    # Channels section
    output.append("\n🔗 Communication Channels:")
    for ch_id, ch_info in status.get("channels", {}).items():
        enabled_icon = "✅" if ch_info["enabled"] else "❌"
        priority_stars = "★" * ch_info["priority"]
        anonymization_color = {
            "low": "🟡",
            "medium": "🟠", 
            "high": "🔴",
            "paranoid": "🟣"
        }.get(ch_info["anonymization_level"], "⚪")
        
        output.append(f"  {enabled_icon} {ch_info['name']} ({ch_info['type']})")
        output.append(f"     Priority: {priority_stars} | Anonymization: {anonymization_color} {ch_info['anonymization_level']}")
        output.append(f"     Encryption: {'Required' if ch_info['encryption_required'] else 'Optional'}")
    
    # Encryption section
    encryption = status.get("encryption", {})
    output.append(f"\n🔐 Encryption Status:")
    output.append(f"  GPG Available: {'✅ Yes' if encryption.get('gpg_available') else '❌ No'}")
    output.append(f"  Keys Loaded: {encryption.get('keys_loaded', 0)}")
    output.append(f"  Temp Directory: {encryption.get('temp_dir', 'N/A')}")
    
    # Statistics section
    stats = status.get("statistics", {})
    output.append(f"\n📊 Communication Statistics:")
    output.append(f"  Messages Sent: {stats.get('messages_sent', 0)}")
    output.append(f"  Files Shared: {stats.get('files_shared', 0)}")
    output.append(f"  Channels Used: {len(stats.get('channels_used', set()))}")
    output.append(f"  Encryption Failures: {stats.get('encryption_failures', 0)}")
    output.append(f"  Communication Errors: {stats.get('communication_errors', 0)}")
    
    # Session info
    session = status.get("session_info", {})
    output.append(f"\n🌐 Session Information:")
    output.append(f"  Anonymous Session: {'✅ Active' if session.get('anonymous_session') else '❌ Inactive'}")
    output.append(f"  Active Channels: {session.get('active_channels', 0)}")
    
    return "\n".join(output)


def format_test_results(results: dict) -> str:
    """Format test results for display"""
    output = []
    
    output.append("🧪 Communication Channel Test Results")
    output.append("=" * 40)
    
    success_count = 0
    for channel_id, success in results.items():
        status_icon = "✅" if success else "❌"
        status_text = "OPERATIONAL" if success else "FAILED"
        output.append(f"  {status_icon} {channel_id:<20} {status_text}")
        if success:
            success_count += 1
    
    output.append(f"\n📈 Overall Status: {success_count}/{len(results)} channels operational")
    
    if success_count == len(results):
        output.append("🎉 All communication channels are working properly!")
    elif success_count > 0:
        output.append("⚠️  Some channels failed - check configuration")
    else:
        output.append("🚨 No communication channels are working - check system setup")
    
    return "\n".join(output)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Anonymous Communication System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                                    Show system status
  %(prog)s test                                      Test all channels
  %(prog)s email -r user@domain.com -s "Subject" -m "Message"
  %(prog)s share -f report.pdf -p password123       Share file with password
  %(prog)s signal -r +1234567890 -m "Hello"         Send Signal message
  %(prog)s emergency -m "Critical issue detected"   Send emergency alert
        """
    )
    
    # Action argument
    parser.add_argument(
        'action', 
        choices=['status', 'test', 'email', 'share', 'signal', 'emergency'],
        help='Action to perform'
    )
    
    # Communication options
    parser.add_argument('--recipient', '-r', help='Recipient (email/phone)')
    parser.add_argument('--subject', '-s', help='Message subject')
    parser.add_argument('--message', '-m', help='Message content')
    parser.add_argument('--file', '-f', help='File to share')
    parser.add_argument('--password', '-p', help='File sharing password')
    parser.add_argument('--expiry', '-e', type=int, default=24, help='File expiry hours (default: 24)')
    parser.add_argument('--channel', '-c', help='Specific channel to use')
    
    # Output options
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize communication system
    try:
        if not args.quiet:
            print("🔄 Initializing anonymous communication system...")
        
        comm = AnonymousCommunication()
        
        if not args.quiet:
            print("✅ System initialized successfully\n")
            
    except Exception as e:
        print(f"❌ Failed to initialize communication system: {e}")
        return 1
    
    try:
        # Execute requested action
        if args.action == 'status':
            status = comm.get_communication_status()
            
            if args.json:
                print(json.dumps(status, indent=2, default=str))
            else:
                print(format_status_output(status))
                
        elif args.action == 'test':
            if not args.quiet:
                print("🧪 Testing communication channels...")
            
            results = comm.test_communication_channels()
            
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(format_test_results(results))
                
        elif args.action == 'email':
            # Validate required arguments
            if not args.recipient or not args.subject or not args.message:
                print("❌ Email requires --recipient, --subject, and --message")
                return 1
            
            if not args.quiet:
                print(f"📧 Sending secure email to {args.recipient}...")
            
            success = comm.send_secure_email(
                recipient=args.recipient,
                subject=args.subject,
                content=args.message,
                channel_id=args.channel
            )
            
            if success:
                print("✅ Secure email sent successfully")
            else:
                print("❌ Failed to send secure email")
                return 1
                
        elif args.action == 'share':
            # Validate required arguments
            if not args.file:
                print("❌ File sharing requires --file")
                return 1
                
            if not os.path.exists(args.file):
                print(f"❌ File not found: {args.file}")
                return 1
            
            if not args.quiet:
                print(f"📤 Sharing file anonymously: {args.file}")
            
            result = comm.share_file_anonymously(
                file_path=args.file,
                password=args.password,
                expiry_hours=args.expiry
            )
            
            if result:
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    print("✅ File shared successfully")
                    print(f"🔗 Download URL: {result['download_url']}")
                    if result.get('password'):
                        print(f"🔐 Password: {result['password']}")
                    print(f"⏰ Expires: {result['expires_at']}")
                    print(f"📊 Max Downloads: {result['max_downloads']}")
            else:
                print("❌ Failed to share file")
                return 1
                
        elif args.action == 'signal':
            # Validate required arguments
            if not args.recipient or not args.message:
                print("❌ Signal messaging requires --recipient and --message")
                return 1
            
            if not args.quiet:
                print(f"📱 Sending Signal message to {args.recipient}...")
            
            attachments = [args.file] if args.file and os.path.exists(args.file) else None
            success = comm.send_signal_message(
                recipient=args.recipient,
                message=args.message,
                attachments=attachments
            )
            
            if success:
                print("✅ Signal message sent successfully")
            else:
                print("❌ Failed to send Signal message")
                return 1
                
        elif args.action == 'emergency':
            # Validate required arguments
            if not args.message:
                print("❌ Emergency alert requires --message")
                return 1
            
            if not args.quiet:
                print("🚨 Sending emergency alert through all priority channels...")
            
            success = comm.send_emergency_alert(
                message=args.message,
                priority="urgent"
            )
            
            if success:
                print("✅ Emergency alert sent successfully")
            else:
                print("❌ Failed to send emergency alert")
                return 1
                
    except KeyboardInterrupt:
        print("\n⚠️ Operation interrupted by user")
        return 1
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        print(f"❌ Unexpected error: {e}")
        return 1
    finally:
        # Cleanup
        try:
            comm.cleanup()
        except:
            pass
    
    return 0


if __name__ == "__main__":
    sys.exit(main())