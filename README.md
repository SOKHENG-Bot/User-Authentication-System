# User Authentication System (FastAPI)

## Overview
A secure **User Authentication System** built with **FastAPI**.  
Provides user registration, login/logout, password reset, and session management for web applications.

## Features
- User Registration: Create accounts with email/password validation
- Login / Logout: Session-based authentication using JWT and session tokens
- Password Reset: Secure password reset functionality
- Account Management: Update profile, change password, etc.
- Security: Password hashing, input validation, and token-based authentication

## Technologies Used
- Backend: Python 3.9+, FastAPI
- Database: PostgreSQL
- Authentication: JWT / OAuth2 Password flow
- Environment Management: `venv`

## Installation

### Prerequisites
- Python 3.8
- PostgreSQL
- `pip` for dependency installation

### Steps

**Step 1: Clone the repository**  
Clone the repository and navigate into the project folder:
```bash
git clone https://github.com/SOKHENG-Bot/User-Authentication-System.git
cd User-Authentication-System
```
Step 2: Create and activate a virtual environment
Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```
Step 3: Install dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
```
Step 4: Configure the database
Update the .env file with your database URL and credentials.

Step 5: Run database migrations
Apply database migrations using Alembic:
```bash
alembic upgrade head
```
Step 6: Start the FastAPI server
Run the server with Uvicorn:
```bash
uvicorn app.main:app --reload
```
Usage

Access the API at http://127.0.0.1:8000 and use /docs for interactive API documentation (Swagger UI).
Register, login, reset password, and manage users via the available API endpoints.
Security

Passwords are hashed with bcrypt, JWT tokens are used for authentication, and input validation is implemented to prevent SQL injection and invalid requests.
