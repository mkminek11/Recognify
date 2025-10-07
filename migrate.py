#!/usr/bin/env python3
"""
Migration helper script for UV projects
Usage:
  uv run python migrate.py init        # Initialize migrations (one-time)
  uv run python migrate.py create "message"  # Create new migration
  uv run python migrate.py upgrade     # Apply migrations
  uv run python migrate.py status      # Check status
  uv run python migrate.py stamp head  # Mark as current (emergency)

Migration workflow:
1. Modify your models in models.py (e.g., add/remove fields).
2. Run `uv run python migrate.py create "Description of changes"` to generate a migration script.
3. Run `uv run python migrate.py upgrade` to apply the migration.
"""

import sys
from flask_migrate import init, migrate, upgrade, current, show, stamp
from app.lib import app

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    with app.app_context():
        if command == 'init':
            init()
        elif command == 'create':
            message = sys.argv[2] if len(sys.argv) > 2 else 'Auto migration'
            migrate(message=message)
        elif command == 'upgrade':
            upgrade()
        elif command == 'status':
            print("Current migration version:")
            print(current())
            print("\nAll migrations:")
            show()
        elif command == 'stamp':
            revision = sys.argv[2] if len(sys.argv) > 2 else 'head'
            stamp(revision=revision)
        else:
            print("Unknown command:", command)
            print(__doc__)

if __name__ == '__main__':
    main()