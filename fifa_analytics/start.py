#!/usr/bin/env python3
"""
FIFA Analytics Platform — One-click Startup
Mahindra University · SE Project 2026
"""

import subprocess
import sys
import os
import time

BASE = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(BASE, "backend")
DB = os.path.join(BACKEND, "fifa.db")

print("=" * 55)
print("   ⚽  FIFA World Cup Analytics Platform")
print("   Mahindra University · SE Project 2026")
print("=" * 55)

# 1. Install dependencies
print("\n[1/3] Installing dependencies...")
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
    "fastapi", "uvicorn[standard]", "aiofiles"], check=True)
print("      ✅ Dependencies ready")

# 2. Seed database
if not os.path.exists(DB):
    print("\n[2/3] Creating & seeding database...")
    subprocess.run([sys.executable, os.path.join(BACKEND, "seed_db.py")], check=True)
else:
    print("\n[2/3] Database already exists ✅")

# 3. Start API server
print("\n[3/3] Starting FastAPI server...")
print("\n" + "─" * 55)
print("  🌐  API:      http://localhost:8000")
print("  📖  API Docs: http://localhost:8000/docs")
print("  🖥️  Frontend: open frontend/dashboard.html")
print("─" * 55)
print("  Press Ctrl+C to stop\n")

os.chdir(BACKEND)
subprocess.run([
    sys.executable, "-m", "uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--reload",
])
