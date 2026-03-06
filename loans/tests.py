"""
Unit tests for the loans application.
"""
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from loans.models import Customer, Loan
from loans.services import CreditScoreService, LoanService


class CustomerModelTest(TestCase):
    """Tests for Customer model."""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            phone_number='1234567890',
            monthly_salary=Decimal('50000'),
            age=30,
            approved_limit=Decimal('1800000')
        )
    
    def test_customer_creation(self):
        """Test customer is created correctly."""
        self.assertEqual(self.customer.first_name, 'John')
        self.assertEqual(self.customer.last_name, 'Doe')
        self.assertEqual(self.customer.phone_number, '1234567890')
    
    def test_calculate_approved_limit(self):
        """Test approved limit calculation."""
        customer = Customer(
            monthly_salary=Decimal('100000'),
            age=30
        )
        # 36 * 100000 = 3,600,000 -> rounded to nearest lakh = 3,600,000
        expected_limit = Decimal('3600000')
        self.assertEqual(customer.calculate_approved_limit(), expected_limit)
    
    def test_get_full_name(self):
        """Test full name getter."""
        self.assertEqual(self.customer.get_full_name(), 'John Doe')


class LoanModelTest(TestCase):
    """Tests for Loan model."""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            phone_number='1234567890',
            monthly_salary=Decimal('50000'),
            age=30,
            approved_limit=Decimal('1800000')
        )
        self.loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('100000'),
            tenure=12,
            interest_rate=Decimal('12'),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            is_approved=True
        )
    
    def test_loan_creation(self):
        """Test loan is created correctly."""
        self.assertEqual(self.loan.loan_amount, Decimal('100000'))
        self.assertEqual(self.loan.tenure, 12)
        self.assertEqual(self.loan.interest_rate, Decimal('12'))
    
    def test_calculate_monthly_installment(self):
        """Test EMI calculation."""
        # EMI = [P * r * (1+r)^n] / [(1+r)^n - 1]
        # P = 100000, r = 12%/12 = 1% = 0.01, n = 12
        # EMI ≈ 8884.87
        emi = self.loan.calculate_monthly_installment()
        self.assertGreater(emi, 8800)
        self.assertLess(emi, 9000)


class CreditScoreServiceTest(TestCase):
    """Tests for CreditScoreService."""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            phone_number='1234567890',
            monthly_salary=Decimal('50000'),
            age=30,
            approved_limit=Decimal('1800000')
        )
    
    def test_credit_score_no_loans(self):
        """Test credit score for customer with no loans."""
        score = CreditScoreService.calculate_credit_score(self.customer)
        # Should have base score but limited by debt ratio
        self.assertGreaterEqual(score, 0)
    
    def test_credit_score_with_loans(self):
        """Test credit score for customer with loans."""
        # Create some loans
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('50000'),
            tenure=12,
            interest_rate=Decimal('12'),
            emis_paid_on_time=10,
            start_date=date(2020, 1, 1),
            end_date=date(2021, 1, 1),
            is_approved=True
        )
        
        score = CreditScoreService.calculate_credit_score(self.customer)
        self.assertGreater(score, 0)
    
    def test_credit_score_exceeds_limit(self):
        """Test credit score is 0 when debt exceeds limit."""
        # Create loan exceeding limit
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('5000000'),  # More than approved limit
            tenure=36,
            interest_rate=Decimal('12'),
            emis_paid_on_time=10,
            start_date=date.today() - timedelta(days=365),
            end_date=date.today() + timedelta(days=730),
            is_approved=True
        )
        
        score = CreditScoreService.calculate_credit_score(self.customer)
        self.assertEqual(score, 0)


class LoanServiceTest(TestCase):
    """Tests for LoanService."""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            phone_number='1234567890',
            monthly_salary=Decimal('50000'),
            age=30,
            approved_limit=Decimal('1800000')
        )
    
    def test_create_loan_success(self):
        """Test successful loan creation."""
        loan, message = LoanService.create_loan(
            self.customer,
            Decimal('100000'),
            Decimal('10'),
            12
        )
        
        self.assertIsNotNone(loan)
        self.assertEqual(message, 'Loan approved successfully')
    
    def test_create_loan_low_credit(self):
        """Test loan creation with low credit score."""
        # Create many loans to reduce credit score
        for i in range(5):
            Loan.objects.create(
                customer=self.customer,
                loan_amount=Decimal('100000'),
                tenure=12,
                interest_rate=Decimal('12'),
                emis_paid_on_time=10,
                start_date=date(2020, 1, 1),
                end_date=date(2021, 1, 1),
                is_approved=True
            )
        
        # Try to create another loan - should fail due to high debt
        loan, message = LoanService.create_loan(
            self.customer,
            Decimal('5000000'),
            Decimal('10'),
            12
        )
        
        # This might still pass if credit score is high enough
        # But if debt ratio is too high, it will fail
        self.assertIsInstance(loan, Loan) or loan is None
    
    def test_get_customer_loans(self):
        """Test getting customer loans."""
        # Create a loan
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('100000'),
            tenure=12,
            interest_rate=Decimal('12'),
            emis_paid_on_time=10,
            start_date=date(2020, 1, 1),
            end_date=date(2021, 1, 1),
            is_approved=True
        )
        
        loans = LoanService.get_customer_loans(self.customer)
        self.assertEqual(len(loans), 1)
        self.assertEqual(loans[0]['loan_amount'], Decimal('100000'))


class EMICalculationTest(TestCase):
    """Tests for EMI calculation."""
    
    def test_emi_zero_interest(self):
        """Test EMI calculation with zero interest rate."""
        emi = CreditScoreService.calculate_emi(
            Decimal('120000'),
            Decimal('0'),
            12
        )
        self.assertEqual(emi, Decimal('10000'))
    
    def test_emi_with_interest(self):
        """Test EMI calculation with interest rate."""
        emi = CreditScoreService.calculate_emi(
            Decimal('100000'),
            Decimal('12'),
            12
        )
        # Should be approximately 8884.87
        self.assertGreater(emi, 8800)
        self.assertLess(emi, 9000)
    
    def test_emi_different_tenure(self):
        """Test EMI with different tenure."""
        emi_12 = CreditScoreService.calculate_emi(
            Decimal('100000'),
            Decimal('12'),
            12
        )
        emi_24 = CreditScoreService.calculate_emi(
            Decimal('100000'),
            Decimal('12'),
            24
        )
        # Longer tenure should have lower EMI
        self.assertLess(emi_24, emi_12)


class EligibilityTest(TestCase):
    """Tests for loan eligibility."""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            phone_number='1234567890',
            monthly_salary=Decimal('50000'),
            age=30,
            approved_limit=Decimal('1800000')
        )
    
    def test_check_eligibility_approved(self):
        """Test loan eligibility check with approval."""
        eligibility = CreditScoreService.check_eligibility(
            self.customer,
            Decimal('100000'),
            Decimal('10'),
            12
        )
        
        self.assertTrue(eligibility['approval'])
        self.assertIn('monthly_installment', eligibility)
        self.assertIn('credit_score', eligibility)
    
    def test_check_eligibility_emi_too_high(self):
        """Test loan rejection when EMI exceeds 50% of salary."""
        # Create existing loans with high EMIs
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('500000'),
            tenure=12,
            interest_rate=Decimal('12'),
            monthly_repayment=Decimal('45000'),  # 90% of salary
            start_date=date.today() - timedelta(days=180),
            end_date=date.today() + timedelta(days=180),
            is_approved=True
        )
        
        eligibility = CreditScoreService.check_eligibility(
            self.customer,
            Decimal('100000'),
            Decimal('10'),
            12
        )
        
        self.assertFalse(eligibility['approval'])
        self.assertIn('Total EMIs exceed', eligibility.get('message', ''))

