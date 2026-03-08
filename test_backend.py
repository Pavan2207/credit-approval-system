#!/usr/bin/env python
"""Test script to check and run the backend."""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_system.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    # Run migrations first
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'migrate', '--verbosity', '2'])
    
    print("\nStarting server...")
    execute_from_command_line(['manage.py', 'runserver', '8000'])

