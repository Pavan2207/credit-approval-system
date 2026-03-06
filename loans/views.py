from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from decimal import Decimal

from .models import Customer, Loan
from .serializers import (
    CustomerSerializer,
    CheckEligibilityRequestSerializer,
    CheckEligibilityResponseSerializer,
    CreateLoanRequestSerializer,
    CreateLoanResponseSerializer,
    LoanDetailSerializer,
    CustomerLoanSerializer
)
from .services import CreditScoreService, LoanService


@api_view(['GET'])
def api_root(request):
    """
    API Root endpoint.
    GET /
    """
    return Response({
        'message': 'Welcome to Credit Approval System API',
        'endpoints': {
            'register': '/api/register',
            'check_eligibility': '/api/check-eligibility',
            'create_loan': '/api/create-loan',
            'view_loan': '/api/view-loan/<loan_id>',
            'view_loans': '/api/view-loans/<customer_id>'
        }
    })


@api_view(['POST'])
def register_customer(request):
    """
    Register a new customer.
    POST /api/register
    
    Request body:
    - first_name: First Name of customer (string)
    - last_name: Last Name of customer (string)
    - age: Age of customer (int)
    - monthly_income: Monthly income of individual (int)
    - phone_number: Phone number (int)
    
    Response:
    - customer_id: Id of customer (int)
    - name: Name of customer (string)
    - age: Age of customer (int)
    - monthly_income: Monthly income of individual (int)
    - approved_limit: Approved credit limit (int)
    - phone_number: Phone number (int)
    """
    try:
        # Extract data from request
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        age = request.data.get('age')
        monthly_income = request.data.get('monthly_income')
        phone_number = request.data.get('phone_number')
        
        # Validation
        if not all([first_name, last_name, age, monthly_income, phone_number]):
            return Response(
                {'error': 'All fields are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if phone number already exists
        if Customer.objects.filter(phone_number=str(phone_number)).exists():
            return Response(
                {'error': 'Phone number already registered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create customer
        customer = Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            age=age,
            monthly_salary=Decimal(str(monthly_income)),
            phone_number=str(phone_number)
        )
        
        # Calculate approved limit
        customer.approved_limit = customer.calculate_approved_limit()
        customer.save()
        
        # Prepare response
        response_data = {
            'customer_id': customer.customer_id,
            'name': customer.get_full_name(),
            'age': customer.age,
            'monthly_income': float(customer.monthly_salary),
            'approved_limit': float(customer.approved_limit),
            'phone_number': customer.phone_number
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def check_eligibility(request):
    """
    Check loan eligibility based on credit score.
    POST /api/check-eligibility
    
    Request body:
    - customer_id: Id of customer (int)
    - loan_amount: Requested loan amount (float)
    - interest_rate: Interest rate on loan (float)
    - tenure: Tenure of loan (int)
    
    Response:
    - customer_id: Id of customer (int)
    - approval: can loan be approved (bool)
    - interest_rate: Interest rate on loan (float)
    - corrected_interest_rate: Corrected Interest Rate (float)
    - tenure: Tenure of loan (int)
    - monthly_installment: Monthly installment (float)
    """
    try:
        serializer = CheckEligibilityRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']
        
        # Get customer
        customer = get_object_or_404(Customer, customer_id=customer_id)
        
        # Check eligibility
        eligibility = CreditScoreService.check_eligibility(
            customer, loan_amount, interest_rate, tenure
        )
        
        response_data = {
            'customer_id': customer_id,
            'approval': eligibility['approval'],
            'interest_rate': float(eligibility['interest_rate']),
            'corrected_interest_rate': float(eligibility['corrected_interest_rate']),
            'tenure': eligibility['tenure'],
            'monthly_installment': float(eligibility['monthly_installment'])
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def create_loan(request):
    """
    Process a new loan based on eligibility.
    POST /api/create-loan
    
    Request body:
    - customer_id: Id of customer (int)
    - loan_amount: Requested loan amount (float)
    - interest_rate: Interest rate on loan (float)
    - tenure: Tenure of loan (int)
    
    Response:
    - loan_id: Id of approved loan, null otherwise (int)
    - customer_id: Id of customer (int)
    - loan_approved: Is the loan approved (bool)
    - message: Appropriate message if loan is not approved (string)
    - monthly_installment: Monthly installment (float)
    """
    try:
        serializer = CreateLoanRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']
        
        # Get customer
        customer = get_object_or_404(Customer, customer_id=customer_id)
        
        # Create loan
        loan, message = LoanService.create_loan(
            customer, loan_amount, interest_rate, tenure
        )
        
        if loan:
            response_data = {
                'loan_id': loan.loan_id,
                'customer_id': customer_id,
                'loan_approved': True,
                'message': message,
                'monthly_installment': float(loan.monthly_repayment)
            }
        else:
            # Get eligibility info for message
            eligibility = CreditScoreService.check_eligibility(
                customer, loan_amount, interest_rate, tenure
            )
            response_data = {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': eligibility.get('message', message),
                'monthly_installment': 0
            }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def view_loan(request, loan_id):
    """
    View loan details and customer details.
    GET /api/view-loan/<loan_id>
    
    Response:
    - loan_id: Id of approved loan (int)
    - customer: JSON containing id, first_name, last_name, phone_number, age (JSON)
    - loan_amount: Is the loan approved (bool)
    - interest_rate: Interest rate of the approved loan (float)
    - monthly_installment: Monthly installment (float)
    - tenure: Tenure of loan (int)
    - repayments_left: No of EMIs left (int)
    """
    try:
        loan = get_object_or_404(Loan, loan_id=loan_id)
        
        serializer = LoanDetailSerializer(loan)
        response_data = serializer.data
        
        # Format customer JSON
        response_data['customer'] = {
            'id': loan.customer.customer_id,
            'first_name': loan.customer.first_name,
            'last_name': loan.customer.last_name,
            'phone_number': loan.customer.phone_number,
            'age': loan.customer.age
        }
        
        # Add repayments_left
        response_data['repayments_left'] = loan.get_repayments_left()
        
        # Convert Decimal to float for JSON
        response_data['loan_amount'] = float(loan.loan_amount)
        response_data['interest_rate'] = float(loan.interest_rate)
        response_data['monthly_installment'] = float(loan.monthly_repayment)
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def view_customer_loans(request, customer_id):
    """
    View all current loan details by customer id.
    GET /api/view-loans/<customer_id>
    
    Response: List of loan items
    - loan_id: Id of approved loan (int)
    - loan_amount: Is the loan approved (bool)
    - interest_rate: Interest rate of the approved loan (float)
    - monthly_installment: Monthly installment (float)
    - repayments_left: No of EMIs left (int)
    - is_approved: Is the loan approved (bool)
    """
    try:
        customer = get_object_or_404(Customer, customer_id=customer_id)
        
        loans = LoanService.get_customer_loans(customer)
        
        # Convert Decimal to float
        for loan in loans:
            loan['loan_amount'] = float(loan['loan_amount'])
            loan['interest_rate'] = float(loan['interest_rate'])
            loan['monthly_installment'] = float(loan['monthly_installment'])
        
        return Response(loans, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

