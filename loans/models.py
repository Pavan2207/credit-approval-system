from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Customer(models.Model):
    """Customer model for storing customer information."""
    
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    monthly_salary = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    age = models.IntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(100)]
    )
    approved_limit = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0
    )
    current_debt = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.customer_id})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def calculate_approved_limit(self):
        """
        Calculate approved limit based on monthly salary.
        Formula: approved_limit = 36 * monthly_salary (rounded to nearest lakh)
        """
        limit = Decimal('36') * self.monthly_salary
        # Round to nearest lakh (100000)
        lakhs = limit / Decimal('100000')
        rounded_lakhs = round(lakhs)
        return Decimal(rounded_lakhs) * Decimal('100000')


class Loan(models.Model):
    """Loan model for storing loan information."""
    
    loan_id = models.IntegerField(primary_key=True)
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='loans'
    )
    loan_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    tenure = models.IntegerField(
        validators=[MinValueValidator(1)]
    )  # in months
    interest_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    monthly_repayment = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0
    )
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loans'
        ordering = ['-created_at']

    def __str__(self):
        return f"Loan {self.loan_id} - Customer {self.customer_id}"

    def calculate_monthly_installment(self):
        """
        Calculate monthly EMI using compound interest formula.
        EMI = [P * r * (1+r)^n] / [(1+r)^n - 1]
        Where:
        - P = Principal (loan_amount)
        - r = Monthly interest rate (annual_rate / 12 / 100)
        - n = Number of installments (tenure)
        """
        if self.interest_rate == 0:
            return self.loan_amount / Decimal(self.tenure)
        
        principal = self.loan_amount
        monthly_rate = self.interest_rate / Decimal('12') / Decimal('100')
        n = Decimal(self.tenure)
        
        # (1 + r)^n
        compound_factor = (Decimal('1') + monthly_rate) ** n
        
        # EMI = P * r * (1+r)^n / [(1+r)^n - 1]
        emi = principal * monthly_rate * compound_factor / (compound_factor - Decimal('1'))
        
        return round(emi, 2)

    def get_repayments_left(self):
        """Calculate remaining EMIs to be paid."""
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        # Calculate expected payments made
        start = self.start_date
        today = date.today()
        
        if today >= self.end_date:
            return 0
        
        # Months passed since start
        months_passed = (today.year - start.year) * 12 + today.month - start.month
        
        # EMIs paid on time is tracked separately
        # We use the start date to calculate expected payments
        expected_payments = min(months_passed, self.tenure)
        
        return max(0, self.tenure - expected_payments)

