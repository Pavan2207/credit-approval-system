#!/usr/bin/env python
"""Simple script to run Django backend server in background."""
import os
import sys
import subprocess
import time

# Add project directory to Python path
project_dir = r"c:\Users\pavan\Downloads\Backend Internship Assignment"
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'credit_system.settings'
os.environ['PYTHONPATH'] = project_dir

# Setup Django
import django
django.setup()

from django.core.management import call_command

if __name__ == '__main__':
    # Run migrations only once
    print("=" * 50)
    print("Running migrations...")
    print("=" * 50)
    call_command('migrate', verbosity=1)
    
    print("\n" + "=" * 50)
    print("Starting development server at http://localhost:8000/")
    print("Press CTRL+C to stop the server")
    print("=" * 50 + "\n")
    
    # Start the server
    call_command('runserver', '8000', '--noreload')

