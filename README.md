# Set & Rep: A Modern Workout Logging Application

Set & Rep is a modern, user-centric web application designed to replace traditional pen-and-paper workout tracking. It provides users with a seamless experience for logging exercises, sets, and reps to monitor their fitness progress.

## Features

- User authentication and authorization
- Pre-populated exercise database with muscle group categorization
- Workout session tracking with exercise logging
- Set and rep tracking with weight recording
- Training plan creation and management
- API-first design for frontend flexibility

## Technical Stack

- Backend: Python 3.11+
- Framework: Django with Django REST Framework
- Database: PostgreSQL
- Authentication: JWT (JSON Web Tokens)
- API Documentation: DRF Spectacular (OpenAPI/Swagger)
- Testing: Pytest with coverage reporting
- Containerization: Docker and Docker Compose

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL (for local development)

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/set-rep.git
   cd set-rep
   ```

2. Create a `.env` file in the project root:
   ```
   DJANGO_DEBUG=True
   DJANGO_SECRET_KEY=your-secret-key-here
   POSTGRES_DB=setrep
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_HOST=db
   ```

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

4. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. Create a superuser (optional):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

The application will be available at http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## Development

### Running Tests

```bash
# Using Docker
docker-compose exec web pytest

# Local development
pytest
```

### Code Style

The project uses Black for code formatting and Flake8 for linting:

```bash
# Format code
black .

# Run linter
flake8
```

## API Endpoints

### Authentication
- POST /api/v1/auth/token/ - Obtain JWT token
- POST /api/v1/auth/token/refresh/ - Refresh JWT token

### Exercises
- GET /api/v1/exercises/ - List all exercises
- GET /api/v1/exercises/{id}/ - Retrieve specific exercise

### Workout Sessions
- GET /api/v1/sessions/ - List user's workout sessions
- POST /api/v1/sessions/ - Create new workout session
- GET /api/v1/sessions/{id}/ - Retrieve specific session
- PUT/PATCH /api/v1/sessions/{id}/ - Update session
- DELETE /api/v1/sessions/{id}/ - Delete session
- POST /api/v1/sessions/{id}/end_session/ - End workout session
- POST /api/v1/sessions/{id}/add_exercise/ - Add exercise to session

### Training Plans
- GET /api/v1/plans/ - List user's training plans
- POST /api/v1/plans/ - Create new training plan
- GET /api/v1/plans/{id}/ - Retrieve specific plan
- PUT/PATCH /api/v1/plans/{id}/ - Update plan
- DELETE /api/v1/plans/{id}/ - Delete plan
- POST /api/v1/plans/{id}/create_from_session/ - Create plan from session

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
