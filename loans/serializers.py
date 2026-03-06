from rest_framework import serializers
from .models import Customer, Loan


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model."""
    
    class Meta:
        model = Customer
        fields = [
            'customer_id', 'first_name', 'last_name', 'age',
            'monthly_salary', 'approved_limit', 'phone_number'
        ]
        read_only_fields = ['customer_id', 'approved_limit']


class CustomerRegisterSerializer(serializers.ModelSerializer):
    """Serializer for registering a new customer."""
    
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_income', 'phone_number']
    
    monthly_income = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2,
        source='monthly_salary'
    )


class LoanSerializer(serializers.ModelSerializer):
    """Serializer for Loan model."""
    
    repayments_left = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = [
            'loan_id', 'customer', 'customer_name', 'loan_amount',
            'interest_rate', 'monthly_repayment', 'tenure',
            'is_approved', 'repayments_left', 'start_date', 'end_date'
        ]
        read_only_fields = ['loan_id', 'monthly_repayment', 'is_approved']
    
    def get_repayments_left(self, obj):
        return obj.get_repayments_left()
    
    def get_customer_name(self, obj):
        return obj.customer.get_full_name()


class LoanDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed loan view."""
    
    customer = serializers.SerializerMethodField()
    repayments_left = serializers.SerializerMethodField()
    monthly_installment = serializers.DecimalField(
        source='monthly_repayment', 
        max_digits=12, 
        decimal_places=2
    )
    
    class Meta:
        model = Loan
        fields = [
            'loan_id', 'customer', 'loan_amount', 'interest_rate',
            'monthly_installment', 'tenure', 'repayments_left'
        ]
        read_only_fields = ['loan_id', 'monthly_repayment']
    
    def get_customer(self, obj):
        return {
            'id': obj.customer.customer_id,
            'first_name': obj.customer.first_name,
            'last_name': obj.customer.last_name,
            'phone_number': obj.customer.phone_number,
            'age': obj.customer.age
        }
    
    def get_repayments_left(self, obj):
        return obj.get_repayments_left()


class CheckEligibilityRequestSerializer(serializers.Serializer):
    """Serializer for check eligibility request."""
    
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField(min_value=1)


class CheckEligibilityResponseSerializer(serializers.Serializer):
    """Serializer for check eligibility response."""
    
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    corrected_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2)


class CreateLoanRequestSerializer(serializers.Serializer):
    """Serializer for create loan request."""
    
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField(min_value=1)


class CreateLoanResponseSerializer(serializers.Serializer):
    """Serializer for create loan response."""
    
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2)


class CustomerLoanSerializer(serializers.Serializer):
    """Serializer for loan in customer loan list."""
    
    loan_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2)
    repayments_left = serializers.IntegerField()
    is_approved = serializers.BooleanField()

