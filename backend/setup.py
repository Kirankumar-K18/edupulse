#!/usr/bin/env python3
"""
setup.py — One-time setup script for Smart Lecturer Review System.
Run this ONCE after cloning the project:
    python setup.py
"""

import os
import sys
import subprocess
import getpass

print("""
╔══════════════════════════════════════════════════════════╗
║     Smart Lecturer Review System — Setup Wizard          ║
╚══════════════════════════════════════════════════════════╝
""")

# ── Step 1: Check Python version ─────────────────────────────────────
if sys.version_info < (3, 9):
    print("✗ Python 3.9+ required.")
    sys.exit(1)
print("✓ Python", sys.version.split()[0])

# ── Step 2: Install requirements ─────────────────────────────────────
print("\n[1/6] Installing Python dependencies...")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
    capture_output=True, text=True
)
if result.returncode != 0:
    print("✗ pip install failed:\n", result.stderr)
    sys.exit(1)
print("✓ Dependencies installed")

# ── Step 3: Create .env ──────────────────────────────────────────────
print("\n[2/6] Environment configuration")
if os.path.exists(".env"):
    print("  .env already exists — skipping.")
else:
    import secrets
    secret_key = secrets.token_urlsafe(50)

    db_name     = input("  MySQL database name [smart_lecturer_db]: ").strip() or "smart_lecturer_db"
    db_user     = input("  MySQL username [root]: ").strip() or "root"
    db_password = getpass.getpass("  MySQL password: ")
    db_host     = input("  MySQL host [localhost]: ").strip() or "localhost"
    db_port     = input("  MySQL port [3306]: ").strip() or "3306"
    email_domain = input("  College email domain [college.edu]: ").strip() or "college.edu"

    with open(".env", "w") as f:
        f.write(f"""DJANGO_SECRET_KEY={secret_key}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST={db_host}
DB_PORT={db_port}
COLLEGE_EMAIL_DOMAIN={email_domain}
""")
    print("✓ .env created")
    db_password_saved = db_password
    db_name_saved = db_name
    db_user_saved = db_user
    db_host_saved = db_host
    db_port_saved = db_port

# ── Step 4: Load .env into os.environ ────────────────────────────────
print("\n[3/6] Loading environment...")
with open(".env") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()
print("✓ Environment loaded")

# ── Step 5: Create MySQL database ────────────────────────────────────
print("\n[4/6] Creating MySQL database...")
try:
    import MySQLdb
    db_name = os.environ.get("DB_NAME", "smart_lecturer_db")
    conn = MySQLdb.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        passwd=os.environ.get("DB_PASSWORD", ""),
        port=int(os.environ.get("DB_PORT", 3306)),
    )
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
        f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✓ Database '{db_name}' ready")
except Exception as e:
    print(f"✗ MySQL error: {e}")
    print("  Make sure MySQL is running and credentials are correct in .env")
    sys.exit(1)

# ── Step 6: Django migrations ─────────────────────────────────────────
print("\n[5/6] Running Django migrations...")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smart_lecturer.settings")

result = subprocess.run(
    [sys.executable, "manage.py", "migrate", "--run-syncdb"],
    capture_output=True, text=True
)
if result.returncode != 0:
    print("✗ migrate failed:\n", result.stderr)
    sys.exit(1)
print("✓ Migrations applied")
print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)

# ── Step 7: Collect static ───────────────────────────────────────────
print("\n[6/6] Collecting static files...")
result = subprocess.run(
    [sys.executable, "manage.py", "collectstatic", "--noinput", "-v", "0"],
    capture_output=True, text=True
)
print("✓ Static files collected" if result.returncode == 0 else "  (skipped)")

# ── Step 8: Create admin ─────────────────────────────────────────────
print("\n══════════════════════════════════════════════════")
print("Setup complete! Now create the admin account:\n")
print("  python manage.py create_admin\n")
print("Then start the server:")
print("  python manage.py runserver\n")
print("Open: http://127.0.0.1:8000/")
print("══════════════════════════════════════════════════")
