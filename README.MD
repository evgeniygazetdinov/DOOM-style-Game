# Django REST API Service

A REST API service built with Django REST Framework featuring authentication with bearer tokens.

## Features
- User registration with phone/email
- Bearer token authentication with 5-minute expiry
- Token auto-renewal on requests
- CORS enabled for all domains
- Latency check endpoint
- Token management

## API Endpoints
- `/signup` - Register with ID (phone/email) and password
- `/signin` - Login with credentials
- `/info` - Get user information
- `/latency` - Check latency to ya.ru
- `/logout` - Logout (single or all sessions)

## Setup
1. Clone the repository
2. Create virtual environment: `python -m venv env`
3. Activate virtual environment:
   - Unix/MacOS: `source env/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Start server: `python manage.py runserver`
