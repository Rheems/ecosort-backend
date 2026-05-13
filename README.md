# 🌿 Ecosort Backend API

Backend infrastructure for Ecosort — Nigeria's first community-powered
waste sorting and marketplace platform.

Built by **Team 3 Eco-Sorters** | Hackathon 2026

## 🚀 Live API

Base URL: https://ecosort-backend-01ta.onrender.com

API Documentation: https://rheems.github.io/ecosort-backend/

## 🛠️ Tech Stack

- Python 3.11
- Django 5.2
- Django REST Framework
- Token Authentication
- CamelCase Middleware
- PostgreSQL (production)
- SQLite (development)
- Render (deployment)

---

## ✨ Features

- User registration for 4 user types (Household, Collector, Buyer, Brand)
- Phone number + password login
- OTP login for non-tech-savvy users (expires in 10 minutes)
- User profile storage and management
- 5-step onboarding session tracking
- Automatic reward notification queuing on onboarding completion
- camelCase API responses for frontend compatibility

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint               | Description                 | Auth |
| ------ | ---------------------- | --------------------------- | ---- |
| POST   | /api/auth/register/    | Register a new user         | No   |
| POST   | /api/auth/login/       | Login with phone + password | No   |
| POST   | /api/auth/request-otp/ | Request 4-digit OTP         | No   |
| POST   | /api/auth/verify-otp/  | Verify OTP and get token    | No   |

### User Profile

| Method | Endpoint         | Description                 | Auth |
| ------ | ---------------- | --------------------------- | ---- |
| GET    | /api/profile/me/ | Get current user profile    | Yes  |
| PUT    | /api/profile/me/ | Update current user profile | Yes  |

### Onboarding

| Method | Endpoint                  | Description                      | Auth |
| ------ | ------------------------- | -------------------------------- | ---- |
| GET    | /api/onboarding/status/   | Check onboarding progress        | Yes  |
| POST   | /api/onboarding/complete/ | Complete a step + trigger reward | Yes  |

---

## 🔐 Authentication

Protected endpoints require a token in the request header:
Get your token by calling the login or verify-otp endpoint.

---

## 👥 User Types

- `household` — Community household users (e.g. Amina)
- `collector` — Informal waste collectors (e.g. Chinedu)
- `buyer` — Recycling buyers and scrap dealers (e.g. Hassan)
- `brand` — FMCG brands for EPR compliance (e.g. Chidinma)

## 📝 Sample Register Request

json
{
"email": "amina@ecosort.com",
"phone_number": "08011111111",
"password": "1234",
"user_type": "household",
"full_name": "Amina Yusuf",
"location": "Bariga, Lagos",
"language": "pidgin",
"waste_type": "plastic"
}

````

## 📝 Sample Login Request

```json
{
    "phone_number": "08011111111",
    "password": "1234",
}

## 🔗 Links

- Live API: https://ecosort-backend-01ta.onrender.com
- API Docs: https://rheems.github.io/ecosort-backend/
- GitHub: https://github.com/Rheems/ecosort-backend

Team 3 Eco-Sorters | Hackathon 2026
````
