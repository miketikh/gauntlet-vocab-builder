"""
Apply migrations to Supabase - Output SQL for manual execution.

This script reads migration files and outputs the SQL for manual execution
in the Supabase Dashboard.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")


def read_migration_file(file_path: Path) -> str:
    """Read a migration file."""
    with open(file_path, 'r') as f:
        return f.read()




def main():
    """Main execution."""
    migrations_dir = Path(__file__).parent / "supabase" / "migrations"

    if not migrations_dir.exists():
        print(f"Error: Migrations directory not found: {migrations_dir}")
        return False

    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("No migration files found!")
        return False

    print("=" * 60)
    print("SUPABASE MIGRATIONS - MANUAL EXECUTION REQUIRED")
    print("=" * 60)
    print(f"\nFound {len(migration_files)} migration file(s)\n")

    print("INSTRUCTIONS:")
    print("1. Go to: https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Navigate to: SQL Editor > New Query")
    print("4. Copy and paste each migration SQL below")
    print("5. Click 'Run' to execute")
    print("6. Repeat for all migrations in order")
    print()

    for i, file_path in enumerate(migration_files, 1):
        print(f"\n{'#'*60}")
        print(f"# MIGRATION {i}/{len(migration_files)}")
        print(f"# File: {file_path.name}")
        print(f"{'#'*60}\n")

        sql = read_migration_file(file_path)
        print(sql)
        print()

    print("=" * 60)
    print("After executing all migrations, run:")
    print("  python3 test_db_connection.py")
    print("to verify the setup.")
    print("=" * 60)

    return True


if __name__ == "__main__":
    main()
