import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_system.settings')
django.setup()

from loans.models import Customer, Loan

print(f"Customers: {Customer.objects.count()}")
print(f"Loans: {Loan.objects.count()}")
