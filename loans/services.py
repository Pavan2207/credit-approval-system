from datetime import date
from decimal import Decimal
from typing import Dict, Tuple, Optional
from django.db.models import Sum, Q
from .models import Customer, Loan


class CreditScoreService:
    """Service for calculating credit score and loan eligibility."""
    
    WEIGHT_LOANS_PAID_ON_TIME = 30
    WEIGHT_NUMBER_OF_LOANS = 15
    WEIGHT_LOAN_ACTIVITY_CURRENT_YEAR = 20
    WEIGHT_LOAN_APPROVED_VOLUME = 20
    WEIGHT_DEBT_RATIO = 15
    
    THRESHOLD_EXCELLENT = 50
    THRESHOLD_GOOD = 30
    THRESHOLD_FAIR = 10
    
    MIN_INTEREST_EXCELLENT = 0
    MIN_INTEREST_GOOD = 12
    MIN_INTEREST_FAIR = 16
    MIN_INTEREST_POOR = float('inf')
    
    @staticmethod
    def calculate_credit_score(customer: Customer) -> int:
        """Calculate credit score (0-100) for a customer based on historical loan data."""
        try:
            loans = Loan.objects.filter(customer=customer)
            
            total_current_debt = loans.aggregate(
                total=Sum('loan_amount', filter=Q(end_date__gte=date.today()))
            )['total'] or Decimal('0')
            
            if total_current_debt > customer.approved_limit:
                return 0
            
            score = 0
            
            score += CreditScoreService._calculate_on_time_payment_score(loans)
            score += CreditScoreService._calculate_loan_count_score(loans)
            score += CreditScoreService._calculate_current_year_activity_score(loans)
            score += CreditScoreService._calculate_loan_volume_score(loans, customer.approved_limit)
            score += CreditScoreService._calculate_debt_ratio_score(total_current_debt, customer.approved_limit)
            
            return min(100, max(0, score))
            
        except Exception as e:
            print(f"Error calculating credit score: {e}")
            return 0
    
    @staticmethod
    def _calculate_on_time_payment_score(loans) -> int:
        if not loans.exists():
            return 0
        
        total_emis = loans.aggregate(total_emis=Sum('emis_paid_on_time'))['total_emis'] or 0
        
        if total_emis >= 100:
            return 30
        elif total_emis >= 50:
            return 25
        elif total_emis >= 20:
            return 20
        elif total_emis >= 10:
            return 15
        elif total_emis >= 5:
            return 10
        else:
            return 5
    
    @staticmethod
    def _calculate_loan_count_score(loans) -> int:
        loan_count = loans.count()
        
        if loan_count >= 10:
            return 15
        elif loan_count >= 5:
            return 12
        elif loan_count >= 3:
            return 10
        elif loan_count >= 1:
            return 7
        else:
            return 0
    
    @staticmethod
    def _calculate_current_year_activity_score(loans) -> int:
        current_year = date.today().year
        current_year_loans = loans.filter(start_date__year=current_year).count()
        
        if current_year_loans == 0:
            return 10
        elif current_year_loans == 1:
            return 20
        elif current_year_loans >= 2:
            return 15
        else:
            return 10
    
    @staticmethod
    def _calculate_loan_volume_score(loans, approved_limit: Decimal) -> int:
        if approved_limit == 0:
            return 0
        
        total_loan_volume = loans.aggregate(total=Sum('loan_amount'))['total'] or Decimal('0')
        ratio = total_loan_volume / approved_limit
        
        if ratio <= 0.3:
            return 20
        elif ratio <= 0.5:
            return 15
        elif ratio <= 0.75:
            return 10
        elif ratio <= 1.0:
            return 5
        else:
            return 0
    
    @staticmethod
    def _calculate_debt_ratio_score(total_debt: Decimal, approved_limit: Decimal) -> int:
        if approved_limit == 0:
            return 0
        
        ratio = total_debt / approved_limit
        
        if ratio <= 0.3:
            return 15
        elif ratio <= 0.5:
            return 10
        elif ratio <= 0.75:
            return 5
        else:
            return 0
    
    @staticmethod
    def check_eligibility(customer: Customer, loan_amount: Decimal, interest_rate: Decimal, tenure: int) -> Dict:
        """Check loan eligibility based on credit score."""
        credit_score = CreditScoreService.calculate_credit_score(customer)
        
        total_monthly_emis = Loan.objects.filter(
            customer=customer, end_date__gte=date.today()
        ).aggregate(total=Sum('monthly_repayment'))['total'] or Decimal('0')
        
        if total_monthly_emis > (customer.monthly_salary * Decimal('0.5')):
            return {
                'approval': False,
                'credit_score': credit_score,
                'interest_rate': interest_rate,
                'corrected_interest_rate': interest_rate,
                'monthly_installment': Decimal('0'),
                'tenure': tenure,
                'message': 'Total EMIs exceed 50% of monthly salary'
            }
        
        if credit_score > CreditScoreService.THRESHOLD_EXCELLENT:
            corrected_rate = interest_rate
            approval = True
        elif credit_score > CreditScoreService.THRESHOLD_GOOD:
            if interest_rate >= CreditScoreService.MIN_INTEREST_GOOD:
                corrected_rate = interest_rate
            else:
                corrected_rate = Decimal(str(CreditScoreService.MIN_INTEREST_GOOD))
            approval = True
        elif credit_score > CreditScoreService.THRESHOLD_FAIR:
            if interest_rate >= CreditScoreService.MIN_INTEREST_FAIR:
                corrected_rate = interest_rate
            else:
                corrected_rate = Decimal(str(CreditScoreService.MIN_INTEREST_FAIR))
            approval = True
        else:
            approval = False
            corrected_rate = interest_rate
        
        monthly_installment = CreditScoreService.calculate_emi(loan_amount, corrected_rate, tenure)
        
        return {
            'approval': approval,
            'credit_score': credit_score,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_rate,
            'monthly_installment': monthly_installment,
            'tenure': tenure,
            'message': 'Loan approved' if approval else 'Loan not approved due to low credit score'
        }
    
    @staticmethod
    def calculate_emi(principal: Decimal, annual_interest_rate: Decimal, tenure: int) -> Decimal:
        """Calculate EMI using compound interest formula."""
        if annual_interest_rate == 0:
            return round(principal / Decimal(tenure), 2)
        
        principal_dec = Decimal(str(principal))
        monthly_rate = Decimal(str(annual_interest_rate)) / Decimal('12') / Decimal('100')
        n = Decimal(tenure)
        
        compound_factor = (Decimal('1') + monthly_rate) ** n
        emi = principal_dec * monthly_rate * compound_factor / (compound_factor - Decimal('1'))
        
        return round(emi, 2)


class LoanService:
    """Service for loan operations."""
    
    @staticmethod
    def create_loan(customer: Customer, loan_amount: Decimal, interest_rate: Decimal, tenure: int) -> Tuple[Optional[Loan], str]:
        """Create a new loan for a customer."""
        eligibility = CreditScoreService.check_eligibility(customer, loan_amount, interest_rate, tenure)
        
        if not eligibility['approval']:
            return None, eligibility['message']
        
        from dateutil.relativedelta import relativedelta
        
        start_date = date.today()
        end_date = start_date + relativedelta(months=tenure)
        
        max_loan_id = Loan.objects.order_by('-loan_id').first()
        next_loan_id = (max_loan_id.loan_id + 1) if max_loan_id else 1
        
        loan = Loan.objects.create(
            loan_id=next_loan_id,
            customer=customer,
            loan_amount=loan_amount,
            tenure=tenure,
            interest_rate=eligibility['corrected_interest_rate'],
            monthly_repayment=eligibility['monthly_installment'],
            start_date=start_date,
            end_date=end_date,
            is_approved=True
        )
        
        return loan, 'Loan approved successfully'
    
    @staticmethod
    def get_customer_loans(customer: Customer) -> list:
        """Get all loans for a customer."""
        loans = Loan.objects.filter(customer=customer).order_by('-created_at')
        
        result = []
        for loan in loans:
            result.append({
                'loan_id': loan.loan_id,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'monthly_installment': loan.monthly_repayment,
                'repayments_left': loan.get_repayments_left(),
                'is_approved': loan.is_approved,
                'tenure': loan.tenure
            })
        
        return result

