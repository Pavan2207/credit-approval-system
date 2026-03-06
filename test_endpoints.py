#!/usr/bin/env python
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_system.settings')
django.setup()

from loans.models import Customer, Loan
from loans.services import CreditScoreService, LoanService

print("=" * 50)
print("Testing Credit Approval System")
print("=" * 50)

# Test 1: Check customer exists
print("\n1. Checking customer 1...")
try:
    customer = Customer.objects.get(customer_id=1)
    print(f"   Customer: {customer.get_full_name()}")
    print(f"   Approved Limit: {customer.approved_limit}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Check loans exist
print("\n2. Checking loans for customer 1...")
loans = Loan.objects.filter(customer_id=1)
print(f"   Total loans: {loans.count()}")
for loan in loans[:3]:
    print(f"   - Loan {loan.loan_id}: {loan.loan_amount}, Interest: {loan.interest_rate}%")

# Test 3: Credit Score
print("\n3. Calculating credit score...")
try:
    credit_score = CreditScoreService.calculate_credit_score(customer)
    print(f"   Credit Score: {credit_score}")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: Check Eligibility
print("\n4. Checking eligibility...")
try:
    eligibility = CreditScoreService.check_eligibility(customer, 50000, 12, 12)
    print(f"   Approval: {eligibility['approval']}")
    print(f"   Credit Score: {eligibility['credit_score']}")
    print(f"   Interest Rate: {eligibility['interest_rate']}")
    print(f"   Corrected Rate: {eligibility['corrected_interest_rate']}")
    print(f"   Monthly Installment: {eligibility['monthly_installment']}")
except Exception as e:
    print(f"   Error: {e}")

# Test 5: Check loan with low interest rate
print("\n5. Checking eligibility with low interest rate (8%)...")
try:
    eligibility = CreditScoreService.check_eligibility(customer, 50000, 8, 12)
    print(f"   Approval: {eligibility['approval']}")
    print(f"   Interest Rate: {eligibility['interest_rate']}")
    print(f"   Corrected Rate: {eligibility['corrected_interest_rate']}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 50)
print("All tests completed!")
print("=" * 50)

