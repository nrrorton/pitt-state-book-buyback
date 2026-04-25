# Pitt State Book Buyback

A web application for Pittsburg State University students to buy and sell textbooks locally.
Built with Flask, this marketplace connects Gorillas directly with one another, keeping
textbook transactions on campus and out of the hands of third-party resellers.

## Features

- Student-only registration restricted to Pitt State email addresses
- Full listing management including book condition, course code, professor, and photo uploads
- Contact sellers directly via email or phone from the listing page
- User profiles displaying ratings and listing history
- Report system for flagging inappropriate listings or users
- Admin dashboard for managing users, resolving reports, and monitoring activity
- REST API with JWT authentication for future mobile client support

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

Clone the repository:

```bash
git clone https://github.com/nrrorton/pitt-state-book-buyback
cd pitt-state-book-buyback
```

Create and activate a virtual environment:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root with the following values:
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password

Run the application:

```bash
python app.py
```

The app will be available at `http://localhost:3000`.


## API Endpoints

The application exposes a REST API for programmatic access. Protected routes require
a Bearer token obtained from the login endpoint.

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | /api/v1/auth/login | No | Obtain a JWT access token |
| GET | /api/v1/listings | No | Retrieve all active listings |
| GET | /api/v1/listings/<id> | No | Retrieve a single listing |
| POST | /api/v1/listings | Yes | Create a new listing |
| PUT | /api/v1/listings/<id> | Yes | Update an existing listing |
| DELETE | /api/v1/listings/<id> | Yes | Delete a listing |
| GET | /api/v1/users/<id> | No | Retrieve a user profile |

## Contributing

This project was built by Nicholas Norton and Travis Sickles as part of a Web Development II
course at Pittsburg State University. If you would like to contribute, please fork the
repository and submit a pull request.

## License

This project is not currently licensed for public use.