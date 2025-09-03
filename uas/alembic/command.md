# ===============================
# ALEMBIC CHEAT SHEET
# ===============================

# --- Initialize Alembic ---
alembic init alembic          # Create Alembic environment (alembic.ini + versions/)

# --- Create Migrations ---
alembic revision -m "msg"             # Create empty migration file
alembic revision --autogenerate -m "msg"  # Auto-generate migration from models

# --- Upgrade / Apply Migrations ---
alembic upgrade head        # Upgrade to latest migration
alembic upgrade <revision>  # Upgrade to specific revision
alembic upgrade +1          # Upgrade one step

# --- Downgrade / Revert Migrations ---
alembic downgrade -1        # Revert last migration
alembic downgrade <revision> # Revert to specific revision
alembic downgrade base      # Revert all migrations (empty DB)

# --- Database Revision Info ---
alembic current             # Show current database revision
alembic history --verbose    # Show all migration history
alembic heads               # Show latest head(s) in migration folder

# --- Stamp / Sync Revisions ---
alembic stamp <revision>    # Set database revision without running migrations
alembic stamp head          # Mark DB as up-to-date with latest head

# --- Merging & Branching ---
alembic merge <rev1> <rev2> -m "merge message"  # Merge multiple heads

# --- Generate SQL Only ---
alembic revision --autogenerate --sql -m "msg"  # Generate SQL script without applying

# --- Show Revision ---
alembic show <revision>     # Show migration script content

# --- Troubleshooting ---
# 1. Multiple heads -> use merge
# 2. Broken DB revision -> use stamp
# 3. Dropped column in model -> run autogenerate migration

# --- Notes ---
# - Always run migrations in a virtual environment where SQLAlchemy is installed.
# - Use --autogenerate carefully; always review generated migration scripts.
# - For Postgres: cascading drops require careful handling of dependent objects.
