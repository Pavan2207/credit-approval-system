$env:DJANGO_SETTINGS_MODULE = "credit_system.settings"
Set-Location "c:/Users/pavan/Downloads/Backend Internship Assignment"
python manage.py migrate
python manage.py runserver 8000

