# AMCC Financial Management System

Financial management system for Arman Maihan Construction Company, built with Django.

## Setup

1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file (see `.env.example` for required variables).
6. Run migrations: `python manage.py migrate`
7. Create a superuser: `python manage.py createsuperuser`
8. Start the server: `python manage.py runserver`

## Features

- Dashboard with KPI cards and project P/L bars
- Project management with budget, documents, income and expenses
- Cash IN / Cash OUT tracking with categories
- Expense reports grouped by category
- PDF report generation (list & profit/loss)
- User authentication and admin-only actions