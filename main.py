#!/usr/bin/env python3
"""
DIAGNOSTIC_MEDICAL - Point d'entree principal
Usage: uv run python main.py [command]

Commands:
    api      - Lance l'API FastAPI (port 8000)
    frontend - Lance l'interface Streamlit (port 8501)
    mcp      - Lance le serveur MCP
    studio   - Lance LangGraph Studio
    test     - Lance les tests
"""

import sys
import os
import subprocess
from dotenv import load_dotenv
load_dotenv()  # Loads .env file
# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


def run_api():
    """Lance l'API FastAPI."""
    print("Lancement API FastAPI sur http://localhost:8000")
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "backend.app.api:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])


def run_frontend():
    """Lance l'interface Streamlit."""
    print("Lancement Frontend Streamlit sur http://localhost:8501")
    subprocess.run([
        sys.executable, "-m", "streamlit",
        "run", "frontend/app.py"
    ])


def run_mcp():
    """Lance le serveur MCP."""
    print("Lancement Serveur MCP")
    subprocess.run([sys.executable, "mcp_server/server.py"])


def run_studio():
    """Lance LangGraph Studio."""
    print("Lancement LangGraph Studio")
    subprocess.run([sys.executable, "-m", "langgraph", "dev"])


def run_tests():
    """Lance les tests."""
    print("Lancement des tests")
    subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])


def show_help():
    print(__doc__)
    print("\nExemples:")
    print("  uv run python main.py api")
    print("  uv run python main.py frontend")
    print("  uv run python main.py mcp")
    print("  uv run python main.py studio")
    print("  uv run python main.py test")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    command = sys.argv[1].lower()
    commands = {
        "api": run_api,
        "frontend": run_frontend,
        "mcp": run_mcp,
        "studio": run_studio,
        "test": run_tests,
        "help": show_help,
        "-h": show_help,
        "--help": show_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Commande inconnue: {command}")
        show_help()
        sys.exit(1)