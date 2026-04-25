# Ecosort Backend API

Backend infrastructure for Ecosort — Nigeria's community-powered waste sorting and marketplace platform.

## Tech Stack

- Python 3.11
- Django 5.2
- Django REST Framework
- SQLite (development)
- PostgreSQL (production)

## Features

- User registration for all user types (Household, Collector, Buyer, Brand)
- User profile storage and management
- Onboarding session tracking
- Onboarding completion trigger with automatic reward notification queuing

## Setup Instructions

### 1. Clone the repository

git clone <your-github-repo-url>
cd ecosort-backend

### 2. Create and activate virtual environment

python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # Mac/Linux

### 3. Install dependencies

pip install -r requirements.txt

### 4. Run migrations

python manage.py migrate

### 5. Start the server

python manage.py runserver

## API Endpoints

| Method | Endpoint                  | Description                        | Auth Required |
| ------ | ------------------------- | ---------------------------------- | ------------- |
| POST   | /api/auth/register/       | Register a new user                | No            |
| GET    | /api/profile/me/          | Get current user profile           | Yes           |
| PUT    | /api/profile/me/          | Update user profile                | Yes           |
| POST   | /api/onboarding/complete/ | Complete onboarding + queue reward | Yes           |
| GET    | /api/onboarding/status/   | Check onboarding progress          | Yes           |

## Sample Registration Request

POST /api/auth/register/

{
"username": "testuser",
"email": "test@ecosort.com",
"password": "password123",
"phone_number": "08012345678",
"user_type": "household"
}

## Sample Response

{
"message": "Registration successful!",
"user_id": 1,
"user_type": "household"
}

## User Types

- household — Community household users
- collector — Informal waste collectors
- buyer — Recycling buyers and scrap dealers
- brand — FMCG brands for EPR compliance

## Team

Team 3 — Eco-Sorters
Hackathon Submission — April 2026
