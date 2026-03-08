"""
Management command to create sample data for testing.
"""
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from loans.models import Customer, Loan


class Command(BaseCommand):
    help = 'Create sample customer and loan data for testing'

    def handle(self, *args, **options):
        # Check if data already exists
        if Customer.objects.exists():
            self.stdout.write(self.style.WARNING('Data already exists. Use --force to recreate.'))
            if not options.get('force'):
                return
        
        # Clear existing data if force is used
        if options.get('force'):
            Loan.objects.all().delete()
            Customer.objects.all().delete()
            self.stdout.write('Existing data cleared.')
        
        # Create sample customers
        customers = [
            {'customer_id': 1, 'first_name': 'John', 'last_name': 'Doe', 'age': 35, 'monthly_salary': Decimal('50000'), 'phone_number': '1234567890', 'approved_limit': Decimal('1800000')},
            {'customer_id': 2, 'first_name': 'Jane', 'last_name': 'Smith', 'age': 28, 'monthly_salary': Decimal('45000'), 'phone_number': '1234567891', 'approved_limit': Decimal('1620000')},
            {'customer_id': 3, 'first_name': 'Bob', 'last_name': 'Johnson', 'age': 42, 'monthly_salary': Decimal('75000'), 'phone_number': '1234567892', 'approved_limit': Decimal('2700000')},
            {'customer_id': 4, 'first_name': 'Alice', 'last_name': 'Williams', 'age': 31, 'monthly_salary': Decimal('55000'), 'phone_number': '1234567893', 'approved_limit': Decimal('1980000')},
            {'customer_id': 5, 'first_name': 'Charlie', 'last_name': 'Brown', 'age': 45, 'monthly_salary': Decimal('80000'), 'phone_number': '1234567894', 'approved_limit': Decimal('2880000')},
            {'customer_id': 6, 'first_name': 'Diana', 'last_name': 'Miller', 'age': 29, 'monthly_salary': Decimal('48000'), 'phone_number': '1234567895', 'approved_limit': Decimal('1728000')},
            {'customer_id': 7, 'first_name': 'Edward', 'last_name': 'Davis', 'age': 38, 'monthly_salary': Decimal('65000'), 'phone_number': '1234567896', 'approved_limit': Decimal('2340000')},
            {'customer_id': 8, 'first_name': 'Fiona', 'last_name': 'Garcia', 'age': 33, 'monthly_salary': Decimal('58000'), 'phone_number': '1234567897', 'approved_limit': Decimal('2088000')},
            {'customer_id': 9, 'first_name': 'George', 'last_name': 'Martinez', 'age': 50, 'monthly_salary': Decimal('90000'), 'phone_number': '1234567898', 'approved_limit': Decimal('3240000')},
            {'customer_id': 10, 'first_name': 'Hannah', 'last_name': 'Anderson', 'age': 27, 'monthly_salary': Decimal('42000'), 'phone_number': '1234567899', 'approved_limit': Decimal('1512000')},
            {'customer_id': 11, 'first_name': 'Ivan', 'last_name': 'Taylor', 'age': 36, 'monthly_salary': Decimal('60000'), 'phone_number': '1234567900', 'approved_limit': Decimal('2160000')},
            {'customer_id': 12, 'first_name': 'Julia', 'last_name': 'Thomas', 'age': 30, 'monthly_salary': Decimal('52000'), 'phone_number': '1234567901', 'approved_limit': Decimal('1872000')},
            {'customer_id': 13, 'first_name': 'Kevin', 'last_name': 'Jackson', 'age': 41, 'monthly_salary': Decimal('70000'), 'phone_number': '1234567902', 'approved_limit': Decimal('2520000')},
            {'customer_id': 14, 'first_name': 'Laura', 'last_name': 'White', 'age': 34, 'monthly_salary': Decimal('56000'), 'phone_number': '1234567903', 'approved_limit': Decimal('2016000')},
            {'customer_id': 15, 'first_name': 'Michael', 'last_name': 'Harris', 'age': 39, 'monthly_salary': Decimal('68000'), 'phone_number': '1234567904', 'approved_limit': Decimal('2448000')},
        ]
        
        created_customers = []
        for c in customers:
            customer = Customer.objects.create(**c)
            created_customers.append(customer)
            self.stdout.write(f'Created customer: {customer.get_full_name()}')
        
        # Create sample loans
        base_date = datetime.now().date() - timedelta(days=90)
        
        loans = [
            {'loan_id': 1, 'customer': created_customers[0], 'loan_amount': Decimal('500000'), 'tenure': 24, 'interest_rate': Decimal('12.5'), 'monthly_repayment': Decimal('23557'), 'emis_paid_on_time': 3, 'start_date': base_date, 'end_date': base_date + timedelta(days=730), 'is_approved': True},
            {'loan_id': 2, 'customer': created_customers[1], 'loan_amount': Decimal('300000'), 'tenure': 18, 'interest_rate': Decimal('14.0'), 'monthly_repayment': Decimal('18567'), 'emis_paid_on_time': 5, 'start_date': base_date - timedelta(days=30), 'end_date': base_date + timedelta(days=510), 'is_approved': True},
            {'loan_id': 3, 'customer': created_customers[2], 'loan_amount': Decimal('1000000'), 'tenure': 36, 'interest_rate': Decimal('11.5'), 'monthly_repayment': Decimal('32567'), 'emis_paid_on_time': 8, 'start_date': base_date - timedelta(days=60), 'end_date': base_date + timedelta(days=990), 'is_approved': True},
            {'loan_id': 4, 'customer': created_customers[3], 'loan_amount': Decimal('250000'), 'tenure': 12, 'interest_rate': Decimal('13.0'), 'monthly_repayment': Decimal('22679'), 'emis_paid_on_time': 10, 'start_date': base_date - timedelta(days=120), 'end_date': base_date + timedelta(days=240), 'is_approved': True},
            {'loan_id': 5, 'customer': created_customers[4], 'loan_amount': Decimal('800000'), 'tenure': 30, 'interest_rate': Decimal('12.0'), 'monthly_repayment': Decimal('28567'), 'emis_paid_on_time': 12, 'start_date': base_date - timedelta(days=180), 'end_date': base_date + timedelta(days=720), 'is_approved': True},
            {'loan_id': 6, 'customer': created_customers[5], 'loan_amount': Decimal('150000'), 'tenure': 9, 'interest_rate': Decimal('15.0'), 'monthly_repayment': Decimal('18234'), 'emis_paid_on_time': 7, 'start_date': base_date - timedelta(days=45), 'end_date': base_date + timedelta(days=225), 'is_approved': True},
            {'loan_id': 7, 'customer': created_customers[6], 'loan_amount': Decimal('450000'), 'tenure': 20, 'interest_rate': Decimal('12.5'), 'monthly_repayment': Decimal('24678'), 'emis_paid_on_time': 6, 'start_date': base_date - timedelta(days=15), 'end_date': base_date + timedelta(days=585), 'is_approved': True},
            {'loan_id': 8, 'customer': created_customers[7], 'loan_amount': Decimal('350000'), 'tenure': 15, 'interest_rate': Decimal('13.5'), 'monthly_repayment': Decimal('25890'), 'emis_paid_on_time': 11, 'start_date': base_date - timedelta(days=90), 'end_date': base_date + timedelta(days=360), 'is_approved': True},
            {'loan_id': 9, 'customer': created_customers[8], 'loan_amount': Decimal('1200000'), 'tenure': 48, 'interest_rate': Decimal('11.0'), 'monthly_repayment': Decimal('30456'), 'emis_paid_on_time': 15, 'start_date': base_date - timedelta(days=200), 'end_date': base_date + timedelta(days=1160), 'is_approved': True},
            {'loan_id': 10, 'customer': created_customers[9], 'loan_amount': Decimal('200000'), 'tenure': 10, 'interest_rate': Decimal('14.5'), 'monthly_repayment': Decimal('21987'), 'emis_paid_on_time': 8, 'start_date': base_date - timedelta(days=60), 'end_date': base_date + timedelta(days=240), 'is_approved': True},
            {'loan_id': 11, 'customer': created_customers[10], 'loan_amount': Decimal('600000'), 'tenure': 28, 'interest_rate': Decimal('12.0'), 'monthly_repayment': Decimal('23245'), 'emis_paid_on_time': 4, 'start_date': base_date, 'end_date': base_date + timedelta(days=840), 'is_approved': True},
            {'loan_id': 12, 'customer': created_customers[11], 'loan_amount': Decimal('180000'), 'tenure': 8, 'interest_rate': Decimal('15.5'), 'monthly_repayment': Decimal('24789'), 'emis_paid_on_time': 6, 'start_date': base_date - timedelta(days=30), 'end_date': base_date + timedelta(days=210), 'is_approved': True},
            {'loan_id': 13, 'customer': created_customers[12], 'loan_amount': Decimal('750000'), 'tenure': 32, 'interest_rate': Decimal('11.5'), 'monthly_repayment': Decimal('25678'), 'emis_paid_on_time': 9, 'start_date': base_date - timedelta(days=75), 'end_date': base_date + timedelta(days=885), 'is_approved': True},
            {'loan_id': 14, 'customer': created_customers[13], 'loan_amount': Decimal('400000'), 'tenure': 22, 'interest_rate': Decimal('13.0'), 'monthly_repayment': Decimal('20123'), 'emis_paid_on_time': 2, 'start_date': base_date + timedelta(days=10), 'end_date': base_date + timedelta(days=670), 'is_approved': True},
            {'loan_id': 15, 'customer': created_customers[14], 'loan_amount': Decimal('550000'), 'tenure': 26, 'interest_rate': Decimal('12.5'), 'monthly_repayment': Decimal('23098'), 'emis_paid_on_time': 5, 'start_date': base_date - timedelta(days=20), 'end_date': base_date + timedelta(days=770), 'is_approved': True},
        ]
        
        for l in loans:
            loan = Loan.objects.create(**l)
            self.stdout.write(f'Created loan #{loan.loan_id} for {loan.customer.get_full_name()}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(customers)} customers and {len(loans)} loans!'))

