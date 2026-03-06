"""
Management command to import initial data from Excel files.
"""
import os
import pandas as pd
from decimal import Decimal
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from loans.models import Customer, Loan


class Command(BaseCommand):
    help = 'Import initial customer and loan data from Excel files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--customer-file',
            type=str,
            default='customer_data.xlsx',
            help='Path to customer data Excel file'
        )
        parser.add_argument(
            '--loan-file',
            type=str,
            default='loan_data.xlsx',
            help='Path to loan data Excel file'
        )

    def handle(self, *args, **options):
        # Try to find the data files in common locations
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Look in current directory and parent directories
        possible_paths = [
            os.path.join(base_dir, options['customer_file']),
            os.path.join(base_dir, '..', options['customer_file']),
            os.path.join(base_dir, '..', '..', options['customer_file']),
            options['customer_file'],
        ]
        
        customer_file = None
        for path in possible_paths:
            if os.path.exists(path):
                customer_file = path
                break
        
        possible_paths = [
            os.path.join(base_dir, options['loan_file']),
            os.path.join(base_dir, '..', options['loan_file']),
            os.path.join(base_dir, '..', '..', options['loan_file']),
            options['loan_file'],
        ]
        
        loan_file = None
        for path in possible_paths:
            if os.path.exists(path):
                loan_file = path
                break
        
        if customer_file:
            self.stdout.write(f'Importing customer data from {customer_file}...')
            self.import_customers(customer_file)
        else:
            self.stdout.write(self.style.WARNING('Customer data file not found, skipping...'))
        
        if loan_file:
            self.stdout.write(f'Importing loan data from {loan_file}...')
            self.import_loans(loan_file)
        else:
            self.stdout.write(self.style.WARNING('Loan data file not found, skipping...'))
        
        # Reset sequences for auto-increment fields
        self.reset_sequences()
        
        self.stdout.write(self.style.SUCCESS('Data import completed!'))

    def reset_sequences(self):
        """Reset PostgreSQL sequences for auto-increment fields."""
        from django.db import connection
        
        try:
            # Get the maximum customer_id and set sequence to next value
            max_customer = Customer.objects.order_by('-customer_id').first()
            if max_customer:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT setval(pg_get_serial_sequence('customers', 'customer_id'), %s)",
                        [max_customer.customer_id]
                    )
                    self.stdout.write(f'Reset customer sequence to {max_customer.customer_id}')
            
            # Get the maximum loan_id and set sequence to next value
            max_loan = Loan.objects.order_by('-loan_id').first()
            if max_loan:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT setval(pg_get_serial_sequence('loans', 'loan_id'), %s)",
                        [max_loan.loan_id]
                    )
                    self.stdout.write(f'Reset loan sequence to {max_loan.loan_id}')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not reset sequences: {e}'))

    def import_customers(self, file_path):
        """Import customer data from Excel file."""
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()

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

                    if pd.notna(customer_id):
                        defaults = {
                            'first_name': str(first_name) if pd.notna(first_name) else '',
                            'last_name': str(last_name) if pd.notna(last_name) else '',
                            'age': int(age) if pd.notna(age) else 25,
                            'phone_number': str(int(phone_number)) if pd.notna(phone_number) else '',
                            'monthly_salary': Decimal(str(monthly_salary)) if pd.notna(monthly_salary) else Decimal('0'),
                            'approved_limit': Decimal(str(approved_limit)) if pd.notna(approved_limit) else Decimal('0'),
                        }

                        customer, created = Customer.objects.update_or_create(
                            customer_id=int(customer_id),
                            defaults=defaults
                        )

                        if created:
                            customers_created += 1
                        else:
                            customers_updated += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing customer row: {e}'))
                    continue

            self.stdout.write(self.style.SUCCESS(
                f'Customer data imported: {customers_created} created, {customers_updated} updated'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing customer data: {e}'))

    def import_loans(self, file_path):
        """Import loan data from Excel file."""
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()

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

                    if pd.isna(customer_id) or pd.isna(loan_id):
                        continue

                    try:
                        customer = Customer.objects.get(customer_id=int(customer_id))
                    except Customer.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Customer {customer_id} not found, skipping loan {loan_id}'))
                        continue

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

                    defaults = {
                        'loan_amount': Decimal(str(loan_amount)) if pd.notna(loan_amount) else Decimal('0'),
                        'tenure': int(tenure) if pd.notna(tenure) else 0,
                        'interest_rate': Decimal(str(interest_rate)) if pd.notna(interest_rate) else Decimal('0'),
                        'monthly_repayment': Decimal(str(monthly_payment)) if pd.notna(monthly_payment) else Decimal('0'),
                        'emis_paid_on_time': int(emis_paid_on_time) if pd.notna(emis_paid_on_time) else 0,
                        'start_date': start_date,
                        'end_date': end_date_parsed,
                        'is_approved': True,
                    }

                    loan, created = Loan.objects.update_or_create(
                        loan_id=int(loan_id),
                        customer=customer,
                        defaults=defaults
                    )

                    if created:
                        loans_created += 1
                    else:
                        loans_updated += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing loan row: {e}'))
                    continue

            self.stdout.write(self.style.SUCCESS(
                f'Loan data imported: {loans_created} created, {loans_updated} updated'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing loan data: {e}'))

