# Secure Internship Tracker API

A secure RESTful backend API for tracking internship applications, built with **FastAPI, Python, SQLAlchemy, and MySQL**. The project features JWT authentication, password hashing, input validation, and user-specific access controls.

## Features

- User registration and login
- Password hashing and verification using `pwdlib`
- JWT-based authentication with 30-minute access tokens
- Create, read, update, and delete internship applications (CRUD)
- User-specific internship data access
- Request validation using Pydantic
- MySQL database integration using SQLAlchemy and PyMySQL
- Interactive API documentation with Swagger UI
- Automated API tests using pytest
- SQLite in-memory database for isolated tests

## Tech Stack

| Technology | Purpose                   |
| ---------- | ------------------------- |
| Python     | Backend programming       |
| FastAPI    | REST API framework        |
| MySQL      | Main application database |
| SQLAlchemy | Database ORM              |
| PyMySQL    | MySQL database driver     |
| PyJWT      | JWT authentication        |
| pwdlib     | Password hashing          |
| Pydantic   | Data validation           |
| pytest     | Automated testing         |
| SQLite     | Test database             |

## API Endpoints

| Method | Endpoint                       | Description                        | Authentication |
| ------ | ------------------------------ | ---------------------------------- | -------------- |
| GET    | `/`                            | API welcome message                | No             |
| GET    | `/health`                      | Health check                       | No             |
| POST   | `/register`                    | Register a new user                | No             |
| POST   | `/login`                       | Log in and receive an access token | No             |
| GET    | `/me`                          | Get the current user's profile     | Yes            |
| POST   | `/internships`                 | Create an internship               | Yes            |
| GET    | `/internships`                 | List your internships              | Yes            |
| GET    | `/internships/{internship_id}` | Retrieve an internship             | Yes            |
| PUT    | `/internships/{internship_id}` | Update an internship               | Yes            |
| DELETE | `/internships/{internship_id}` | Delete an internship               | Yes            |

## Getting Started

### Prerequisites

- Python installed
- MySQL Server installed and running
- Git installed

### 1. Clone the repository

```powershell
git clone https://github.com/kaizenO-O/secure-internship-tracker-api.git
cd secure-internship-tracker-api
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a reference.

Configure your local values:

```dotenv
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=internship_tracker
SECRET_KEY=your_generated_secret_key
```

Replace the example values with your actual configuration. Generate a strong, random `SECRET_KEY`.

**Never commit your real `.env` file, database password, or secret key to GitHub.**

### 5. Create the database

Start MySQL Server and create the application database:

```sql
CREATE DATABASE internship_tracker;
```

Ensure the MySQL credentials in `.env` match your local setup. The application currently creates its tables through SQLAlchemy when it starts outside test mode.

### 6. Run the API

```powershell
python -m uvicorn app.main:app --reload
```

The API should now be available at:

- **API root:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Health check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Authentication

The API uses JWT bearer tokens to protect private endpoints.

1. Register an account using `POST /register`.
2. Log in using `POST /login`.
3. Copy the returned `access_token`.
4. Click **Authorize** in Swagger UI and enter the token as requested.
5. Test the protected endpoints.

Access tokens expire after 30 minutes. Protected internship operations use the authenticated user's identity to restrict access to their own records.

## Running Tests

The project includes automated tests using pytest and an in-memory SQLite database.

Run the tests from the project root:

```powershell
python -m pytest -v
```

The current test suite contains **13 tests** covering:

- User registration and duplicate registration
- Login and incorrect passwords
- Authentication requirements
- Internship creation and retrieval
- Internship updates and deletion
- Invalid JWT tokens
- Prevention of cross-user access, updates, and deletion

The tests use a separate database configuration to avoid modifying your MySQL application data.

## Security Considerations

- Passwords are stored as hashes rather than plaintext.
- Protected routes require JWT authentication.
- Internship records are filtered by the authenticated user's ID.
- Input data is validated using Pydantic schemas.
- Secrets should be stored in environment variables and excluded from version control.
- Automated tests verify important user-access restrictions.

This is a portfolio and learning project. Additional hardening is recommended before production use, including database migrations, rate limiting, secure deployment configuration, and production-grade secret management.

## Future Improvements

- Pagination and internship search
- Filtering by application status
- Internship deadline reminders
- Database migrations using Alembic
- Continuous integration with GitHub Actions
- Production deployment
- Additional edge-case and security tests

## Author

**Kyash Thakur**
B.Tech Computer Science Engineering
Specialization: Cyber Security | AI ML

GitHub: [https://github.com/kaizenO-O](https://github.com/kaizenO-O)
