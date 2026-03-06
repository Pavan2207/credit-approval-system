# Credit Approval System - Implementation Plan

## Project Overview
Build a Django-based credit approval system with:
- PostgreSQL database
- DRF (Django Rest Framework)
- Background task workers (Celery) for data ingestion
- Dockerized application
- 5 API endpoints

## Data Summary
- **Customer Data**: 300 records with columns: Customer ID, First Name, Last Name, Age, Phone Number, Monthly Salary, Approved Limit
- **Loan Data**: 782 records with columns: Customer ID, Loan ID, Loan Amount, Tenure, Interest Rate, Monthly payment, EMIs paid on Time, Date of Approval, End Date

## Implementation Plan

### Phase 1: Project Setup
- [x] Create Django project structure
- [x] Configure settings.py with PostgreSQL, DRF, Celery
- [x] Set up Docker and docker-compose.yml
- [x] Create requirements.txt

### Phase 2: Database Models
- [x] Create Customer model
- [x] Create Loan model
- [x] Run migrations

### Phase 3: Data Ingestion
- [x] Create Celery task for importing customer_data.xlsx
- [x] Create Celery task for importing loan_data.xlsx
- [x] Configure Celery beat for background processing

### Phase 4: API Endpoints
- [x] /register - Register new customer
- [x] /check-eligibility - Check loan eligibility with credit score
- [x] /create-loan - Process new loan
- [x] /view-loan/<loan_id> - View loan details
- [x] /view-loans/<customer_id> - View all loans for customer

### Phase 5: Credit Score Logic
- [x] Implement credit score calculation:
  - Past Loans paid on time
  - No of loans taken in past
  - Loan activity in current year
  - Loan approved volume
  - Check if sum of current loans > approved limit
- [x] Implement approval logic based on credit score slabs
- [x] Implement EMI calculation with compound interest

### Phase 6: Testing
- [x] Write unit tests for models
- [x] Write unit tests for API endpoints
- [x] Write unit tests for credit score calculation

### Phase 7: Final Setup
- [x] Ensure Docker configuration works
- [x] Test all endpoints
- [x] Final verification

