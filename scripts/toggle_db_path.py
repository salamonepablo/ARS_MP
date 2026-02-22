#!/usr/bin/env python
"""
Utility to toggle between Access database paths in .env
- Local: docs/legacy_bd/Accdb/DB_CCEE_Programación 1.1.accdb
- Remote: g:\Material Rodante\1-Servicio Eléctrico\DB\Base de Dato Prog\DB_CCEE_Programación 1.1.accdb
"""

import argparse
import sys
from pathlib import Path

# Paths
LOCAL_DB = r"docs/legacy_bd/Accdb/DB_CCEE_Programación 1.1.accdb"
REMOTE_DB = r"g:\Material Rodante\1-Servicio Eléctrico\DB\Base de Dato Prog\DB_CCEE_Programación 1.1.accdb"
ENV_FILE = Path(".env")

def show_current():
    """Show current database path in .env"""
    if not ENV_FILE.exists():
        print("❌ .env file not found!")
        return
    
    content = ENV_FILE.read_text()
    
    for line in content.split('\n'):
        if line.startswith('LEGACY_ACCESS_DB_PATH='):
            print("📌 Current DB path:")
            print(f"   {line.strip()}")
            break
    else:
        print("⚠️  LEGACY_ACCESS_DB_PATH not found in .env")

def switch_to_local():
    """Switch to local database path"""
    if not ENV_FILE.exists():
        print("❌ .env file not found!")
        return False
    
    content = ENV_FILE.read_text()
    
    # Find and replace LEGACY_ACCESS_DB_PATH
    lines = content.split('\n')
    updated = False
    
    for i, line in enumerate(lines):
        if line.startswith('LEGACY_ACCESS_DB_PATH='):
            lines[i] = f'LEGACY_ACCESS_DB_PATH={LOCAL_DB}'
            updated = True
            break
    
    if updated:
        ENV_FILE.write_text('\n'.join(lines))
        print("✅ Switched to LOCAL database")
        print(f"   Path: {LOCAL_DB}")
        return True
    else:
        print("⚠️  LEGACY_ACCESS_DB_PATH not found in .env")
        return False

def switch_to_remote():
    """Switch to remote database path (G: drive)"""
    if not ENV_FILE.exists():
        print("❌ .env file not found!")
        return False
    
    content = ENV_FILE.read_text()
    
    # Find and replace LEGACY_ACCESS_DB_PATH
    lines = content.split('\n')
    updated = False
    
    for i, line in enumerate(lines):
        if line.startswith('LEGACY_ACCESS_DB_PATH='):
            lines[i] = f'LEGACY_ACCESS_DB_PATH="{REMOTE_DB}"'
            updated = True
            break
    
    if updated:
        ENV_FILE.write_text('\n'.join(lines))
        print("✅ Switched to REMOTE database (G:)")
        print(f"   Path: {REMOTE_DB}")
        return True
    else:
        print("⚠️  LEGACY_ACCESS_DB_PATH not found in .env")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Toggle between local and remote Access database paths"
    )
    parser.add_argument(
        'action',
        choices=['show', 'local', 'remote'],
        help="Action to perform"
    )
    
    args = parser.parse_args()
    
    if args.action == 'show':
        show_current()
    elif args.action == 'local':
        success = switch_to_local()
        sys.exit(0 if success else 1)
    elif args.action == 'remote':
        success = switch_to_remote()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
