# AI Notetaker API

## Overview
The AI Notetaker API is a backend application built using FastAPI that facilitates the management of meetings, notes, and user interactions. It integrates with calendar services and provides a meeting bot to assist users in taking notes during meetings.

## Features
- User management (registration, authentication)
- Meeting scheduling and retrieval
- Note creation and summarization
- Meeting bot integration for automated note-taking
- Calendar integration for scheduling and event management

## Project Structure
```
ai-notetaker-api
├── src
│   ├── main.py                # Entry point of the FastAPI application
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection and ORM setup
│   ├── dependencies.py        # Dependency injection functions
│   ├── models                  # Database models
│   ├── schemas                 # Pydantic schemas for data validation
│   ├── api                     # API endpoints
│   ├── services                # Business logic
│   └── utils                   # Utility functions
├── tests                       # Unit tests
├── alembic                     # Database migrations
├── requirements.txt            # Project dependencies
├── alembic.ini                # Alembic configuration
├── .env.example                # Example environment variables
└── README.md                   # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd ai-notetaker-api
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the environment variables by copying `.env.example` to `.env` and updating the values as needed.

## Running the Application
To start the FastAPI application, run:
```
uvicorn src.main:app --reload
```
The application will be available at `http://127.0.0.1:8000`.

## API Documentation
The API documentation can be accessed at `http://127.0.0.1:8000/docs`.

## Testing
To run the tests, use:
```
pytest
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.