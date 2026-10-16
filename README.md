## Author
# Secure Internship Tracker API

A RESTful backend API for tracking internship applications, built with FastAPI and MySQL. It supports user registration, JWT authentication, and private internship management.

## Features

- User registration and login
- Secure password hashing using Argon2
- JWT-based authentication
- Create, read, update, and delete internship applications
- User-specific data access
- Input validation using Pydantic
- MySQL database integration using SQLAlchemy
- Interactive API documentation with Swagger UI

## Tech Stack

- **Language:** Python
- **API Framework:** FastAPI
- **Database:** MySQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT (PyJWT)
- **Password Hashing:** Argon2
- **Validation:** Pydantic
- **Database Driver:** PyMySQL

## API Endpoints

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/register` | Register a user | No |
| POST | `/login` | Log in and receive an access token | No |
| GET | `/me` | Get the current user | Yes |
| POST | `/internships` | Create an internship | Yes |
| GET | `/internships` | List your internships | Yes |
| GET | `/internships/{internship_id}` | Get an internship | Yes |
| PUT | `/internships/{internship_id}` | Update an internship | Yes |
| DELETE | `/internships/{internship_id}` | Delete an internship | Yes |

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/kaizenO-O/secure-internship-tracker-api.git
cd secure-internship-tracker-api
```

Replace `kaizenO-O` with your GitHub username.

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root using `.env.example` as a template.

Set your own MySQL credentials and a strong, randomly generated `SECRET_KEY`. Never commit the real `.env` file.

### 5. Set up MySQL

Install and start MySQL Server. Create a database named `internship_tracker` and configure your database connection variables in `.env`.

### 6. Start the API

```powershell
python -m uvicorn app.main:app --reload
```

The API should be available at:

- API root: http://127.0.0.1:8000/
- Swagger UI: http://127.0.0.1:8000/docs

## Authentication

Register an account and log in to receive an access token. In Swagger UI, use the **Authorize** control to provide the token, then test the protected endpoints.

## Security

- Passwords are stored as password hashes rather than plaintext.
- Protected routes require JWT authentication.
- Internship records are scoped to the authenticated user.
- Environment secrets are excluded from version control.

## Future Improvements

- Automated tests with pytest
- Pagination and search
- Internship deadline reminders
- Deployment with managed database hosting
- Continuous integration



## Author

Yash Singh

B.Tech Computer Science Engineering  
Specialization: Cyber Security  
Interests: AI/ML and Cybersecurity




GitHub: https://github.com/kaizenO-O

