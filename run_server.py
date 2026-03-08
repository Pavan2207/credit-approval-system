#!/usr/bin/env python
"""Simple script to run Django backend."""
import os
import sys

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

# Now import Django modules
from django.core.management import call_command

if __name__ == '__main__':
    print("Running migrations...")
    call_command('migrate', verbosity=2)
    
    print("\nStarting development server at http://localhost:8000/")
    call_command('runserver', '8000')

