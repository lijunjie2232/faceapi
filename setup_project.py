#!/usr/bin/env python3
"""
Setup script for the Face Recognition System
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    print(f"Running: {command}")
    result = subprocess.run(
        command, 
        shell=True, 
        cwd=cwd,
        capture_output=True, 
        text=True
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True


def setup_project():
    """Setup the face recognition system project"""
    project_root = Path(__file__).parent
    print(f"Setting up project in: {project_root}")
    
    # Initialize uv project
    print("\nInitializing uv project...")
    if not run_command("uv init", cwd=project_root):
        print("Failed to initialize uv project")
        return False
    
    # Install dependencies
    print("\nInstalling dependencies...")
    if not run_command("uv pip install -r requirements.txt", cwd=project_root):
        print("Failed to install dependencies")
        return False
    
    # Create necessary directories if they don't exist
    dirs_to_create = [
        project_root / "logs",
        project_root / "uploads",
        project_root / "volumes" / "milvus",
        project_root / "volumes" / "etcd",
        project_root / "volumes" / "minio"
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Ensured directory exists: {dir_path}")
    
    print("\nProject setup completed successfully!")
    print("\nTo start the services, run:")
    print("  docker-compose up -d")
    print("\nTo run the backend locally, navigate to the backend directory and run:")
    print("  uvicorn app.main:app --reload")
    
    return True


if __name__ == "__main__":
    if not setup_project():
        sys.exit(1)