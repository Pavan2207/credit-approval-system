import pandas as pd
import os
from celery import shared_task
from decimal import Decimal
from datetime import datetime
from django.utils.dateparse import parse_date


@shared_task
def import_customer_data(file_path=None):
    """
    Background task to import customer data from Excel file.
    """
    if file_path is None:
        file_path = os.environ.get(
            'CUSTOMER_DATA_PATH', 
            '/data/customer_data.xlsx'
        )
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Map columns to model fields
        from loans.models import Customer
        
        customers_created = 0
        customers_updated = 0
        
        for _, row in df.iterrows():
            try:
                customer_id = row.get('Customer ID')
                first_name = row.get('First Name')
                last_name = row.get('Last Name')
                age = row.get('Age')
                phone_number = row.get('Phone Number')
                monthly_salary = row.get('Monthly Salary')
                approved_limit = row.get('Approved Limit')
                
                # Check if customer exists
                if pd.notna(customer_id):
                    customer, created = Customer.objects.update_or_create(
                        customer_id=int(customer_id),
                        defaults={
                            'first_name': str(first_name) if pd.notna(first_name) else '',
                            'last_name': str(last_name) if pd.notna(last_name) else '',
                            'age': int(age) if pd.notna(age) else 25,
                            'phone_number': str(int(phone_number)) if pd.notna(phone_number) else '',
                            'monthly_salary': Decimal(str(monthly_salary)) if pd.notna(monthly_salary) else Decimal('0'),
                            'approved_limit': Decimal(str(approved_limit)) if pd.notna(approved_limit) else Decimal('0'),
                        }
                    )
                    if created:
                        customers_created += 1
                    else:
                        customers_updated += 1
                        
            except Exception as e:
                print(f"Error processing customer row: {e}")
                continue
        
        return {
            'status': 'success',
            'message': f'Customer data imported: {customers_created} created, {customers_updated} updated'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error importing customer data: {str(e)}'
        }


@shared_task
def import_loan_data(file_path=None):
    """
    Background task to import loan data from Excel file.
    """
    if file_path is None:
        file_path = os.environ.get(
            'LOAN_DATA_PATH', 
            '/data/loan_data.xlsx'
        )
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Map columns to model fields
        from loans.models import Customer, Loan
        
        loans_created = 0
        loans_updated = 0
        
        for _, row in df.iterrows():
            try:
                customer_id = row.get('Customer ID')
                loan_id = row.get('Loan ID')
                loan_amount = row.get('Loan Amount')
                tenure = row.get('Tenure')
                interest_rate = row.get('Interest Rate')
                monthly_payment = row.get('Monthly payment')
                emis_paid_on_time = row.get('EMIs paid on Time')
                date_of_approval = row.get('Date of Approval')
                end_date = row.get('End Date')
                
                # Skip if no customer_id or loan_id
                if pd.isna(customer_id) or pd.isna(loan_id):
                    continue
                
                # Get customer
                try:
                    customer = Customer.objects.get(customer_id=int(customer_id))
                except Customer.DoesNotExist:
                    print(f"Customer {customer_id} not found, skipping loan {loan_id}")
                    continue
                
                # Parse dates
                start_date = None
                if pd.notna(date_of_approval):
                    if isinstance(date_of_approval, datetime):
                        start_date = date_of_approval.date()
                    else:
                        start_date = parse_date(str(date_of_approval))
                
                end_date_parsed = None
                if pd.notna(end_date):
                    if isinstance(end_date, datetime):
                        end_date_parsed = end_date.date()
                    else:
                        end_date_parsed = parse_date(str(end_date))
                
                # Create or update loan
                loan, created = Loan.objects.update_or_create(
                    loan_id=int(loan_id),
                    customer=customer,
                    defaults={
                        'loan_amount': Decimal(str(loan_amount)) if pd.notna(loan_amount) else Decimal('0'),
                        'tenure': int(tenure) if pd.notna(tenure) else 0,
                        'interest_rate': Decimal(str(interest_rate)) if pd.notna(interest_rate) else Decimal('0'),
                        'monthly_repayment': Decimal(str(monthly_payment)) if pd.notna(monthly_payment) else Decimal('0'),
                        'emis_paid_on_time': int(emis_paid_on_time) if pd.notna(emis_paid_on_time) else 0,
                        'start_date': start_date,
                        'end_date': end_date_parsed,
                        'is_approved': True,
                    }
                )
                
                if created:
                    loans_created += 1
                else:
                    loans_updated += 1
                        
            except Exception as e:
                print(f"Error processing loan row: {e}")
                continue
        
        return {
            'status': 'success',
            'message': f'Loan data imported: {loans_created} created, {loans_updated} updated'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error importing loan data: {str(e)}'
        }


@shared_task
def import_all_data():
    """
    Task to import both customer and loan data.
    """
    customer_result = import_customer_data()
    loan_result = import_loan_data()
    
    return {
        'customer_result': customer_result,
        'loan_result': loan_result
    }

