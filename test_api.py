#!/usr/bin/env python
"""
Test script for Credit Approval System API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_register():
    """Test /register endpoint"""
    print("\n=== Testing /register ===")
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "monthly_income": 50000,
        "phone_number": "9876543210"
    }
    response = requests.post(f"{BASE_URL}/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_check_eligibility():
    """Test /check-eligibility endpoint"""
    print("\n=== Testing /check-eligibility ===")
    data = {
        "customer_id": 1,
        "loan_amount": 50000,
        "interest_rate": 12,
        "tenure": 12
    }
    response = requests.post(f"{BASE_URL}/check-eligibility", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_create_loan():
    """Test /create-loan endpoint"""
    print("\n=== Testing /create-loan ===")
    data = {
        "customer_id": 1,
        "loan_amount": 10000,
        "interest_rate": 10,
        "tenure": 12
    }
    response = requests.post(f"{BASE_URL}/create-loan", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_view_loan():
    """Test /view-loan/<loan_id> endpoint"""
    print("\n=== Testing /view-loan/7798 ===")
    response = requests.get(f"{BASE_URL}/view-loan/7798")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_view_loans():
    """Test /view-loans/<customer_id> endpoint"""
    print("\n=== Testing /view-loans/1 ===")
    response = requests.get(f"{BASE_URL}/view-loans/1")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

if __name__ == "__main__":
    try:
        # Test all endpoints
        test_view_loans()
        test_view_loan()
        test_check_eligibility()
        test_create_loan()
        test_register()
        
        print("\n=== All tests completed ===")
    except Exception as e:
        print(f"Error: {e}")

