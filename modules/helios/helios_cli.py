#!/usr/bin/env python3
"""Helios Protocol CLI - Management Interface"""

import sys
import json
import argparse
from datetime import datetime
from tabulate import tabulate

sys.path.insert(0, '/opt/tps19/modules')
sys.path.insert(0, '/workspace/modules')

from helios.helios_protocol import helios_protocol, HeliosPhase, DecisionStatus

class HeliosCLI:
    """Command Line Interface for Helios Protocol"""
    
    def __init__(self):
        self.helios = helios_protocol
    
    def status(self, args):
        """Display Helios Protocol status"""
        status = self.helios.get_status()
        
        print("\n🛡️  HELIOS PROTOCOL STATUS")
        print("="*60)
        
        # Deployment Status
        can_deploy = status.get('can_deploy', False)
        deploy_status = "✅ ALLOWED" if can_deploy else "🚫 BLOCKED"
        print(f"Deployment Status: {deploy_status}")
        if not can_deploy:
            print(f"Reason: {status.get('deploy_status_message', 'Unknown')}")
        
        print(f"\nTotal Deployments: {status.get('total_deployments', 0)}")
        print(f"Rolled Back: {status.get('rolled_back_deployments', 0)}")
        print(f"Recent Rollbacks (7d): {status.get('recent_rollbacks_7d', 0)}")
        print(f"Current Stable Version: {status.get('current_stable_version', 'None')}")
        
        # Open Postmortems
        open_pms = status.get('open_postmortems', {})
        if open_pms:
            print("\n📋 Open Postmortems by Severity:")
            for severity, count in sorted(open_pms.items()):
                print(f"   Severity {severity}: {count}")
        else:
            print("\n✅ No open postmortems")
        
        print(f"\nMonitoring Active: {'Yes' if status.get('monitoring_active') else 'No'}")
        print("="*60)
    
    def list_postmortems(self, args):
        """List all postmortems"""
        import sqlite3
        
        conn = sqlite3.connect(self.helios.db_path)
        cursor = conn.cursor()
        
        if args.open_only:
            cursor.execute("""SELECT postmortem_id, deployment_id, severity, title, status, created_at
                FROM postmortems WHERE status = 'open' ORDER BY severity, created_at DESC""")
        else:
            cursor.execute("""SELECT postmortem_id, deployment_id, severity, title, status, created_at
                FROM postmortems ORDER BY created_at DESC LIMIT 20""")
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            print("No postmortems found")
            return
        
        headers = ["ID", "Deployment", "Severity", "Title", "Status", "Created"]
        table_data = []
        
        for row in results:
            pm_id, deploy_id, severity, title, status, created = row
            # Truncate long fields
            pm_id_short = pm_id[:20] + "..." if len(pm_id) > 20 else pm_id
            title_short = title[:40] + "..." if len(title) > 40 else title
            
            table_data.append([
                pm_id_short,
                deploy_id[:15] + "..." if len(deploy_id) > 15 else deploy_id,
                f"SEV-{severity}",
                title_short,
                status.upper(),
                created[:19]  # Remove microseconds
            ])
        
        print("\n📋 POSTMORTEMS")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def view_postmortem(self, args):
        """View detailed postmortem information"""
        import sqlite3
        
        conn = sqlite3.connect(self.helios.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""SELECT * FROM postmortems WHERE postmortem_id = ?""", (args.id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            print(f"Postmortem {args.id} not found")
            return
        
        # Parse result
        _, pm_id, deploy_id, severity, title, desc, root_cause, actions, status, assigned, created, completed = result
        
        print(f"\n📋 POSTMORTEM: {pm_id}")
        print("="*60)
        print(f"Deployment: {deploy_id}")
        print(f"Severity: {severity}")
        print(f"Status: {status.upper()}")
        print(f"Created: {created}")
        if completed:
            print(f"Completed: {completed}")
        if assigned:
            print(f"Assigned To: {assigned}")
        
        print(f"\nTitle: {title}")
        print(f"\nDescription:\n{desc}")
        
        if root_cause:
            print(f"\nRoot Cause:\n{root_cause}")
        
        if actions:
            print("\nCorrective Actions:")
            try:
                action_list = json.loads(actions)
                for i, action in enumerate(action_list, 1):
                    print(f"  {i}. {action}")
            except:
                print(f"  {actions}")
        
        print("="*60)
    
    def complete_postmortem(self, args):
        """Complete a postmortem"""
        # Read corrective actions from file or stdin
        if args.actions_file:
            with open(args.actions_file, 'r') as f:
                actions = [line.strip() for line in f if line.strip()]
        else:
            print("Enter corrective actions (one per line, empty line to finish):")
            actions = []
            while True:
                action = input("> ").strip()
                if not action:
                    break
                actions.append(action)
        
        if not actions:
            print("Error: At least one corrective action is required")
            return
        
        # Complete the postmortem
        success = self.helios.complete_postmortem(args.id, args.root_cause, actions)
        
        if success:
            print(f"✅ Postmortem {args.id} completed successfully")
            
            # Check deployment status
            can_deploy, message = self.helios.can_deploy()
            if can_deploy:
                print("✅ All Severity-1 postmortems resolved - deployments are now allowed")
            else:
                print(f"⚠️  {message}")
        else:
            print(f"❌ Failed to complete postmortem {args.id}")
    
    def list_rollbacks(self, args):
        """List rollback history"""
        import sqlite3
        
        conn = sqlite3.connect(self.helios.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""SELECT rollback_id, deployment_id, trigger_phase, from_version, 
            to_version, success, created_at FROM rollback_history 
            ORDER BY created_at DESC LIMIT 10""")
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            print("No rollbacks found")
            return
        
        headers = ["Rollback ID", "Deployment", "Trigger", "From Ver", "To Ver", "Success", "Time"]
        table_data = []
        
        for row in results:
            rb_id, deploy_id, phase, from_v, to_v, success, created = row
            table_data.append([
                rb_id[:20] + "..." if len(rb_id) > 20 else rb_id,
                deploy_id[:15] + "..." if len(deploy_id) > 15 else deploy_id,
                phase,
                from_v[:10],
                to_v[:10],
                "✅" if success else "❌",
                created[:19]
            ])
        
        print("\n🔄 ROLLBACK HISTORY")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def mark_stable(self, args):
        """Mark a version as stable"""
        success = self.helios.mark_version_stable(args.version, args.deployment_id)
        
        if success:
            print(f"✅ Version {args.version} marked as stable")
        else:
            print(f"❌ Failed to mark version {args.version} as stable")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Helios Protocol Management CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show Helios Protocol status')
    
    # Postmortem commands
    pm_parser = subparsers.add_parser('postmortems', help='Postmortem management')
    pm_subparsers = pm_parser.add_subparsers(dest='pm_command')
    
    # List postmortems
    pm_list = pm_subparsers.add_parser('list', help='List postmortems')
    pm_list.add_argument('--open-only', action='store_true', help='Show only open postmortems')
    
    # View postmortem
    pm_view = pm_subparsers.add_parser('view', help='View postmortem details')
    pm_view.add_argument('id', help='Postmortem ID')
    
    # Complete postmortem
    pm_complete = pm_subparsers.add_parser('complete', help='Complete a postmortem')
    pm_complete.add_argument('id', help='Postmortem ID')
    pm_complete.add_argument('root_cause', help='Root cause description')
    pm_complete.add_argument('--actions-file', help='File containing corrective actions')
    
    # Rollback history
    rollback_parser = subparsers.add_parser('rollbacks', help='Show rollback history')
    
    # Mark stable version
    stable_parser = subparsers.add_parser('mark-stable', help='Mark version as stable')
    stable_parser.add_argument('version', help='Version ID to mark as stable')
    stable_parser.add_argument('--deployment-id', help='Associated deployment ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = HeliosCLI()
    
    if args.command == 'status':
        cli.status(args)
    elif args.command == 'postmortems':
        if args.pm_command == 'list':
            cli.list_postmortems(args)
        elif args.pm_command == 'view':
            cli.view_postmortem(args)
        elif args.pm_command == 'complete':
            cli.complete_postmortem(args)
        else:
            pm_parser.print_help()
    elif args.command == 'rollbacks':
        cli.list_rollbacks(args)
    elif args.command == 'mark-stable':
        cli.mark_stable(args)

if __name__ == "__main__":
    main()