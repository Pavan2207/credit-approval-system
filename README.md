# Credit Approval System

A Django-based credit approval system with PostgreSQL database, DRF (Django Rest Framework), and background task workers (Celery) for data ingestion.

## Live Demo

- **Render**: https://credit-approval-system-tbq6.onrender.com/
- **Vercel**: https://credit-approval-system.vercel.app/

## Features

- **Customer Registration** - Register new customers
- **Loan Eligibility Check** - Check loan eligibility with credit score calculation
- **Loan Processing** - Create and process new loans
- **Loan Details** - View individual loan details
- **Customer Loans** - View all loans for a customer

## Tech Stack

- **Backend**: Django 4.x + Django REST Framework
- **Database**: PostgreSQL (Docker) / SQLite (local)
- **Task Queue**: Celery with Redis
- **Containerization**: Docker & Docker Compose

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register/` | POST | Register new customer |
| `/check-eligibility/` | POST | Check loan eligibility |
| `/create-loan/` | POST | Create new loan |
| `/view-loan/<loan_id>/` | GET | View loan details |
| `/view-loans/<customer_id>/` | GET | View all customer loans |

## Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/Pavan2207/credit-approval-system.git
cd credit-approval-system
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the server:
```bash
python manage.py runserver
```

### Docker Setup

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. The API will be available at `http://localhost:8000`

## Deployment

### Render (Recommended - Free)
1. Go to https://render.com
2. Connect your GitHub account
3. Create "New Web Service"
4. Select your repo
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `gunicorn credit_system.wsgi:application`
7. Click Deploy!

Or use the included `render.yaml` for automatic configuration.

### Vercel
This project is configured for Vercel deployment. Connect your GitHub repository to Vercel for automatic deployments.

## Project Structure

```
├── api/                    # Vercel API handler
├── credit_system/          # Django project settings
├── loans/                  # Loans app (models, views, serializers)
├── templates/              # HTML templates
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── vercel.json             # Vercel configuration
```

## License

MIT License

