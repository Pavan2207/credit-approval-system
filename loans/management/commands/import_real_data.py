"""
Management command to import real customer and loan data from Excel files.
Includes robust error handling and data validation.
"""
import os
import pandas as pd
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_date
from loans.models import Customer, Loan


class Command(BaseCommand):
    help = 'Import real customer and loan data from Excel files with error handling'

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
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force import even if data exists'
        )
        parser.add_argument(
            '--skip-errors',
            action='store_true',
            help='Continue importing even if some records fail validation'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting real data import with error handling...'))
        
        # Check if data already exists
        if not options.get('force'):
            if Customer.objects.exists() or Loan.objects.exists():
                self.stdout.write(self.style.WARNING(
                    'Data already exists in database. Use --force to reimport.'
                ))
                return
        
        # Clear existing data if force is used
        if options.get('force'):
            Loan.objects.all().delete()
            Customer.objects.all().delete()
            self.stdout.write('Existing data cleared.')
        
        # Find the data files
        customer_file = self._find_file(options['customer_file'])
        loan_file = self._find_file(options['loan_file'])
        
        skip_errors = options.get('skip_errors', False)
        
        customer_count = 0
        customer_errors = 0
        loan_count = 0
        loan_errors = 0
        
        if customer_file:
            self.stdout.write(f'Importing customer data from {customer_file}...')
            customer_count, customer_errors = self.import_customers(customer_file, skip_errors)
        else:
            self.stdout.write(self.style.ERROR('Customer data file not found!'))
            self.stdout.write(self.style.WARNING(
                'Please provide customer_data.xlsx file or check the path.'
            ))
        
        if loan_file:
            self.stdout.write(f'Importing loan data from {loan_file}...')
            loan_count, loan_errors = self.import_loans(loan_file, skip_errors)
        else:
            self.stdout.write(self.style.ERROR('Loan data file not found!'))
            self.stdout.write(self.style.WARNING(
                'Please provide loan_data.xlsx file or check the path.'
            ))
        
        # Reset sequences for auto-increment fields
        self.reset_sequences()
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== Import Summary ==='))
        self.stdout.write(f'Customers imported: {customer_count}')
        if customer_errors > 0:
            self.stdout.write(self.style.WARNING(f'Customer errors: {customer_errors}'))
        self.stdout.write(f'Loans imported: {loan_count}')
        if loan_errors > 0:
            self.stdout.write(self.style.WARNING(f'Loan errors: {loan_errors}'))
        
        if customer_count > 0 or loan_count > 0:
            self.stdout.write(self.style.SUCCESS('Data import completed!'))
        else:
            self.stdout.write(self.style.ERROR('No data was imported. Please check your data files.'))

    def _find_file(self, filename):
        """Find the data file in various possible locations."""
        # Get the base directory (project root)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # Possible paths to search
        possible_paths = [
            os.path.join(base_dir, filename),
            os.path.join(base_dir, '..', filename),
            os.path.join(base_dir, '..', '..', filename),
            os.path.join(base_dir, 'data', filename),
            os.path.join(base_dir, '..', 'data', filename),
            os.path.join(os.getcwd(), filename),
            filename,
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None

    def reset_sequences(self):
        """Reset PostgreSQL sequences for auto-increment fields."""
        from django.db import connection
        
        try:
            max_customer = Customer.objects.order_by('-customer_id').first()
            if max_customer:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT setval(pg_get_serial_sequence('loans_customer', 'customer_id'), %s)",
                        [max_customer.customer_id]
                    )
                    self.stdout.write(f'Reset customer sequence to {max_customer.customer_id}')
            
            max_loan = Loan.objects.order_by('-loan_id').first()
            if max_loan:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT setval(pg_get_serial_sequence('loans_loan', 'loan_id'), %s)",
                        [max_loan.loan_id]
                    )
                    self.stdout.write(f'Reset loan sequence to {max_loan.loan_id}')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not reset sequences: {e}'))

    def import_customers(self, file_path, skip_errors=False):
        """Import customer data from Excel file with error handling."""
        customers_created = 0
        customers_updated = 0
        errors = 0
        
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()
            
            self.stdout.write(f'Found {len(df)} customer records to process')
            
            for idx, row in df.iterrows():
                try:
                    customer_id = row.get('Customer ID')
                    
                    if pd.isna(customer_id):
                        self.stdout.write(self.style.WARNING(
                            f'Row {idx + 1}: Missing Customer ID, skipping'
                        ))
                        errors += 1
                        if not skip_errors:
                            continue
                    
                    # Validate and clean data
                    validated_data = self._validate_customer_row(row)
                    
                    if validated_data is None:
                        errors += 1
                        if not skip_errors:
                            continue
                    
                    with transaction.atomic():
                        customer, created = Customer.objects.update_or_create(
                            customer_id=int(customer_id),
                            defaults=validated_data
                        )
                        
                        if created:
                            customers_created += 1
                        else:
                            customers_updated += 1
                            
                except Exception as e:
                    errors += 1
                    self.stdout.write(self.style.ERROR(
                        f'Row {idx + 1}: Error processing customer: {str(e)}'
                    ))
                    if not skip_errors:
                        continue
            
            self.stdout.write(self.style.SUCCESS(
                f'Customer data imported: {customers_created} created, {customers_updated} updated'
            ))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing customer data: {str(e)}'))
        
        return customers_created + customers_updated, errors

    def _validate_customer_row(self, row):
        """Validate and clean customer data."""
        try:
            # Validate customer_id
            customer_id = row.get('Customer ID')
            if pd.isna(customer_id):
                return None
            
            # Validate first_name
            first_name = row.get('First Name')
            if pd.isna(first_name):
                first_name = ''
            else:
                first_name = str(first_name).strip()
            
            # Validate last_name
            last_name = row.get('Last Name')
            if pd.isna(last_name):
                last_name = ''
            else:
                last_name = str(last_name).strip()
            
            # Validate age
            age = row.get('Age')
            if pd.isna(age):
                age = 25  # Default age
            else:
                try:
                    age = int(age)
                    if age < 18 or age > 100:
                        age = 25  # Default if invalid
                except (ValueError, TypeError):
                    age = 25
            
            # Validate phone_number
            phone_number = row.get('Phone Number')
            if pd.isna(phone_number):
                phone_number = ''
            else:
                # Convert to string and remove any non-digit characters
                phone_number = str(phone_number).replace('.', '').replace('-', '').strip()
                # Take first 20 characters max
                phone_number = phone_number[:20]
            
            # Validate monthly_salary
            monthly_salary = row.get('Monthly Salary')
            if pd.isna(monthly_salary):
                monthly_salary = Decimal('0')
            else:
                try:
                    monthly_salary = Decimal(str(monthly_salary))
                except (InvalidOperation, ValueError):
                    monthly_salary = Decimal('0')
            
            # Validate approved_limit
            approved_limit = row.get('Approved Limit')
            if pd.isna(approved_limit):
                # Calculate if not provided
                approved_limit = Decimal('36') * monthly_salary
                lakhs = approved_limit / Decimal('100000')
                rounded_lakhs = round(lakhs)
                approved_limit = Decimal(rounded_lakhs) * Decimal('100000')
            else:
                try:
                    approved_limit = Decimal(str(approved_limit))
                except (InvalidOperation, ValueError):
                    # Calculate from salary
                    approved_limit = Decimal('36') * monthly_salary
                    lakhs = approved_limit / Decimal('100000')
                    rounded_lakhs = round(lakhs)
                    approved_limit = Decimal(rounded_lakhs) * Decimal('100000')
            
            return {
                'first_name': first_name,
                'last_name': last_name,
                'age': age,
                'phone_number': phone_number,
                'monthly_salary': monthly_salary,
                'approved_limit': approved_limit,
            }
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Validation error: {str(e)}'))
            return None

    def import_loans(self, file_path, skip_errors=False):
        """Import loan data from Excel file with error handling."""
        loans_created = 0
        loans_updated = 0
        errors = 0
        
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()
            
            self.stdout.write(f'Found {len(df)} loan records to process')
            
            for idx, row in df.iterrows():
                try:
                    customer_id = row.get('Customer ID')
                    loan_id = row.get('Loan ID')
                    
                    if pd.isna(customer_id) or pd.isna(loan_id):
                        self.stdout.write(self.style.WARNING(
                            f'Row {idx + 1}: Missing Customer ID or Loan ID, skipping'
                        ))
                        errors += 1
                        if not skip_errors:
                            continue
                    
                    # Check if customer exists
                    try:
                        customer = Customer.objects.get(customer_id=int(customer_id))
                    except Customer.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f'Row {idx + 1}: Customer {customer_id} not found, skipping loan {loan_id}'
                        ))
                        errors += 1
                        if not skip_errors:
                            continue
                    
                    # Validate and clean loan data
                    validated_data = self._validate_loan_row(row)
                    
                    if validated_data is None:
                        errors += 1
                        if not skip_errors:
                            continue
                    
                    with transaction.atomic():
                        loan, created = Loan.objects.update_or_create(
                            loan_id=int(loan_id),
                            customer=customer,
                            defaults=validated_data
                        )
                        
                        if created:
                            loans_created += 1
                        else:
                            loans_updated += 1
                            
                except Exception as e:
                    errors += 1
                    self.stdout.write(self.style.ERROR(
                        f'Row {idx + 1}: Error processing loan: {str(e)}'
                    ))
                    if not skip_errors:
                        continue
            
            self.stdout.write(self.style.SUCCESS(
                f'Loan data imported: {loans_created} created, {loans_updated} updated'
            ))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing loan data: {str(e)}'))
        
        return loans_created + loans_updated, errors

    def _validate_loan_row(self, row):
        """Validate and clean loan data."""
        try:
            # Validate loan_amount
            loan_amount = row.get('Loan Amount')
            if pd.isna(loan_amount):
                loan_amount = Decimal('0')
            else:
                try:
                    loan_amount = Decimal(str(loan_amount))
                except (InvalidOperation, ValueError):
                    loan_amount = Decimal('0')
            
            # Validate tenure
            tenure = row.get('Tenure')
            if pd.isna(tenure):
                tenure = 0
            else:
                try:
                    tenure = int(tenure)
                    if tenure < 1:
                        tenure = 1
                except (ValueError, TypeError):
                    tenure = 1
            
            # Validate interest_rate
            interest_rate = row.get('Interest Rate')
            if pd.isna(interest_rate):
                interest_rate = Decimal('0')
            else:
                try:
                    interest_rate = Decimal(str(interest_rate))
                    if interest_rate < 0:
                        interest_rate = Decimal('0')
                    elif interest_rate > 100:
                        interest_rate = Decimal('100')
                except (InvalidOperation, ValueError):
                    interest_rate = Decimal('0')
            
            # Validate monthly_payment
            monthly_payment = row.get('Monthly payment')
            if pd.isna(monthly_payment):
                monthly_payment = Decimal('0')
            else:
                try:
                    monthly_payment = Decimal(str(monthly_payment))
                except (InvalidOperation, ValueError):
                    monthly_payment = Decimal('0')
            
            # Validate emis_paid_on_time
            emis_paid_on_time = row.get('EMIs paid on Time')
            if pd.isna(emis_paid_on_time):
                emis_paid_on_time = 0
            else:
                try:
                    emis_paid_on_time = int(emis_paid_on_time)
                    if emis_paid_on_time < 0:
                        emis_paid_on_time = 0
                except (ValueError, TypeError):
                    emis_paid_on_time = 0
            
            # Parse start_date
            start_date = None
            date_of_approval = row.get('Date of Approval')
            if pd.notna(date_of_approval):
                start_date = self._parse_date(date_of_approval)
            
            # Parse end_date
            end_date = None
            end_date_raw = row.get('End Date')
            if pd.notna(end_date_raw):
                end_date = self._parse_date(end_date_raw)
            
            return {
                'loan_amount': loan_amount,
                'tenure': tenure,
                'interest_rate': interest_rate,
                'monthly_repayment': monthly_payment,
                'emis_paid_on_time': emis_paid_on_time,
                'start_date': start_date,
                'end_date': end_date,
                'is_approved': True,
            }
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Validation error: {str(e)}'))
            return None

    def _parse_date(self, date_value):
        """Parse date from various formats."""
        try:
            # If it's already a datetime object
            if isinstance(date_value, datetime):
                return date_value.date()
            
            # If it's a date object
            if isinstance(date_value, date):
                return date_value
            
            # Try to parse as string
            date_str = str(date_value).strip()
            
            # Try multiple date formats
            date_formats = [
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%Y-%m-%d',
                '%d-%m-%Y',
                '%d.%m.%Y',
                '%Y/%m/%d',
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            # Try Django's dateparse
            parsed = parse_date(date_str)
            if parsed:
                return parsed
            
            return None
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Date parsing error: {str(e)}'))
            return None

