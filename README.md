# User Auth API

A robust, production-ready User Authentication API built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. This system provides secure user registration, multi-factor login support (via email), and comprehensive password management features.

## 🚀 Features

- **🔐 Registration**: Secure user registration with unique email validation.
- **🔑 Login**: JWT-based authentication with access and refresh tokens.
- **🛡️ Rate Limiting**: Built-in protection against brute-force attacks using SlowAPI.
- **📧 Password Management**: Integrated with SMTP for password reset flows.
- **💼 Database Migrations**: Easy-to-manage schema updates using Alembic.
- **⚙️ Environment Config**: Centralized configuration via `.env` files.

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL (Support for SQLite/Others)
- **Authentication**: JWT (JSON Web Tokens)
- **Security**: Passlib (Bcrypt)
- **Migrations**: Alembic
- **Package Manager**: uv / pip

## 📂 Project Structure

```text
user-auth-api/
├── app/
│   ├── auth/           # Authentication logic (JWT, hashing)
│   ├── core/           # Configuration & Middleware
│   ├── db/             # Database connection & models
│   ├── migrations/     # Alembic database migration scripts
│   ├── routes/         # API endpoints (Registration, Login, Password)
│   ├── schemas/        # Pydantic models for request/response validation
│   ├── utils/          # Helper functions (Email, etc.)
│   └── main.py         # Application entry point
├── .env.example        # Template for environment variables
├── .gitignore          # Files to ignore in Git
├── requirements.txt    # Python dependencies
└── alembic.ini         # Alembic configuration
```

## 🏗️ Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL (or another supported database)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LikithaDasari/auth-service-backend.git
   cd auth-service-backend
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env`.
   - Fill in your database credentials and secret key.
   ```bash
   cp .env.example .env
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

## 🚀 Running the API

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.  
Visit `/docs` for interactive API documentation (Swagger UI).

## 📡 API Endpoints Summary

| Endpoint | Method | Tag | Description |
| :--- | :--- | :--- | :--- |
| `/user/register` | `POST` | Registration | Register a new user |
| `/user/login` | `POST` | Login | Authenticate and get JWT token |
| `/user/password/reset` | `POST` | Passwords | Initiate password reset |

## 🛡️ Security

- **JWT Tokens**: Used for stateless authentication.
- **Bcrypt**: For secure password hashing.
- **Rate Limiting**: Applied to sensitive endpoints to prevent abuse (SlowAPI).

## 🤝 Contributing

Contributions are welcome! Please fork the repo and submit a PR.
