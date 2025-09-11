

---

# Developer Foundry 2.0 – Team A AUthentication & Authorization API

## Project Overview

This repository contains the backend API for **Team A** of the Developer Foundry 2.0 Bootcamp.
The project is built with **Django & Django REST Framework (DRF)** and provides APIs for:

* User authentication and signup
* Email verification
* Team management (CRUD operations)
* Role-based authorization
* User sign in

Our goal is to build a secure and scalable foundation for managing users, teams, and permissions.

---

## Features

*  **Authentication** – Secure user login and token management
*  **User Signup** – Register new users with validation
*  **Email Verification** – Ensure user accounts are valid
*  **Team Management (CRUD)** – Create, Read, Update, and Delete teams
*  **Role Management (Authorization)** – Assign and enforce user roles
*  **Sign In** – Seamless access with credential verification

---

## 🛠️ Tech Stack

* **Backend Framework**: Django 5.x
* **API Layer**: Django REST Framework
* **Database**: PostgreSQL (recommended) / SQLite (development)
* **Authentication**: JWT / Token-based (via DRF)
* **Environment Management**: `python-dotenv`
* **Package Management**: `pip-tools`

---

## 👨‍💻 Team Members

* **Chima Enyeribe** – Backend Developer (Python)
* **Oluwatobiloba Okunogbe** – Backend Developer (Python)
* **Richard McAdams** – Backend Developer (Python)

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone git@github.com:Developer-s-Foundry/DF.2.0-task-mgt-authentication.git
cd DF.2.0-task-mgt-authentication
```

### 2️⃣(a) Create Virtual Environment

```bash
python -m venv venv
```

### 2️⃣(b) Activate Virtual Environment
```
source venv/bin/activate     # On Mac/Linux

venv\Scripts\activate        # On Windows

(optionally): source venv/Scripts/activate     # On Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/dbname
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_password
```

### 5️⃣ Run Migrations

```bash
python manage.py migrate
```

### 6️⃣ Create Superuser

```bash
python manage.py createsuperuser
```

### 7️⃣ Run the Development Server

```bash
python manage.py runserver
```

API will be available at:
👉 `http://127.0.0.1:8000/api/`

---

## 📬 API Endpoints (Draft)

| Endpoint                  | Method | Description                |
| ------------------------- | ------ | -------------------------- |
| `/api/auth/signup/`       | POST   | User signup                |
| `/api/auth/login/`        | POST   | User login / token         |
| `/api/auth/verify-email/` | GET    | Email verification         |
| `/api/teams/`             | GET    | List all teams             |
| `/api/teams/`             | POST   | Create team                |
| `/api/teams/{id}/`        | PUT    | Update team                |
| `/api/teams/{id}/`        | DELETE | Delete team                |
| `/api/roles/`             | GET    | Manage roles/authorization |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

---