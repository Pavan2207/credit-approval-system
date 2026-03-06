#!/usr/bin/env python
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_system.settings')
django.setup()

from loans.models import Customer, Loan
from loans.services import CreditScoreService
from datetime import date
from django.db.models import Sum, Q
from decimal import Decimal

print("=" * 50)
print("Debugging Eligibility Check")
print("=" * 50)

# Get customer
customer = Customer.objects.get(customer_id=1)
print(f"\nCustomer: {customer.get_full_name()}")
print(f"Monthly Salary: {customer.monthly_salary}")
print(f"Approved Limit: {customer.approved_limit}")

# Calculate total current EMIs
total_monthly_emis = Loan.objects.filter(
    customer=customer,
    end_date__gte=date.today()
).aggregate(
    total=Sum('monthly_repayment')
)['total'] or Decimal('0')

print(f"\nTotal Monthly EMIs: {total_monthly_emis}")
print(f"50% of Monthly Salary: {customer.monthly_salary * Decimal('0.5')}")

# Check credit score
credit_score = CreditScoreService.calculate_credit_score(customer)
print(f"\nCredit Score: {credit_score}")

# Full eligibility check
print("\n--- Full Eligibility Check ---")
eligibility = CreditScoreService.check_eligibility(customer, 50000, 12, 12)
print(f"Approval: {eligibility['approval']}")
print(f"Message: {eligibility.get('message', 'N/A')}")
print(f"Details: {json.dumps(eligibility, indent=2, default=str)}")

