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
print("Testing Multiple Customers")
print("=" * 50)

# Test different customers
for customer_id in [1, 10, 50, 100, 150]:
    print(f"\n--- Customer {customer_id} ---")
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        
        # Get total current EMIs
        total_monthly_emis = Loan.objects.filter(
            customer=customer,
            end_date__gte=date.today()
        ).aggregate(total=Sum('monthly_repayment'))['total'] or Decimal('0')
        
        print(f"Name: {customer.get_full_name()}")
        print(f"Salary: {customer.monthly_salary}")
        print(f"Approved Limit: {customer.approved_limit}")
        print(f"Current EMIs: {total_monthly_emis}")
        print(f"EMI Limit (50%): {customer.monthly_salary * Decimal('0.5')}")
        
        # Calculate credit score
        credit_score = CreditScoreService.calculate_credit_score(customer)
        print(f"Credit Score: {credit_score}")
        
        # Check eligibility
        eligibility = CreditScoreService.check_eligibility(customer, 50000, 12, 12)
        print(f"Eligibility: {eligibility['approval']} - {eligibility.get('message', 'OK')}")
        
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 50)

