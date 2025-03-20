# Microservices Monorepo with Pants

This is a production-ready microservices monorepo built with the [Pants](https://www.pantsbuild.org/) build system. It demonstrates how to structure a monorepo with multiple services that can run separately in Docker but can also be imported and used by one another.

## Architecture

The monorepo contains the following services:

- **API Gateway Service**: Entry point for clients, routes requests to appropriate services
- **User Service**: Manages user data and authentication
- **Product Service**: Manages product information
- **Notification Service**: Handles sending notifications (email, SMS, push)

Each service is containerized with Docker and can be run independently or together using Docker Compose.

## Project Structure

```
monorepo/
├── pants.toml                  # Pants configuration
├── BUILD                       # Root BUILD file
├── pyproject.toml              # Python project metadata
├── docker-compose.yml          # Docker Compose configuration
├── README.md                   # Project documentation
├── Makefile                    # Convenience commands
│
├── shared/                     # Shared libraries
│   ├── BUILD                   # Pants BUILD file
│   ├── models/                 # Shared data models
│   ├── utils/                  # Shared utilities
│   └── db/                     # Database utilities
│
├── services/                   # Service implementations
│   ├── api_gateway/            # API Gateway Service
│   │   ├── BUILD              
│   │   ├── Dockerfile
│   │   ├── src/
│   │   └── tests/
│   │
│   ├── user_service/           # User Service
│   │   ├── BUILD
│   │   ├── Dockerfile
│   │   ├── src/
│   │   └── tests/
│   │
│   ├── product_service/        # Product Service
│   │   ├── BUILD
│   │   ├── Dockerfile
│   │   ├── src/
│   │   └── tests/
│   │
│   └── notification_service/   # Notification Service
│       ├── BUILD
│       ├── Dockerfile
│       ├── src/
│       └── tests/
│
├── .github/                    # GitHub configuration
│   └── workflows/              # GitHub Actions workflows
│       ├── test.yml            # Testing workflow
│       └── deploy.yml          # Deployment workflow
│
└── scripts/                    # Utility scripts
    ├── setup.sh                # Setup script
    └── deploy.sh               # Deployment script
```

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Git

## Getting Started

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/monorepo.git
cd monorepo
```

2. Set up the development environment:

```bash
make setup
```

This will download the Pants build system and install pre-commit hooks.

### Running Services

#### Running All Services

To run all services together using Docker Compose:

```bash
make run-all
```

This will start all services, along with PostgreSQL and Redis, as defined in the `docker-compose.yml` file.

#### Running Individual Services

To run a specific service:

```bash
make run-service SERVICE=<service_name>
```

Where `<service_name>` is one of:
- `api_gateway`
- `user_service`
- `product_service`
- `notification_service`

For example:

```bash
make run-service SERVICE=user_service
```

### Testing

#### Running All Tests

To run tests for all services:

```bash
make test
```

#### Testing Individual Services

To test a specific service:

```bash
make test SERVICE=<service_name>
```

For example:

```bash
make test SERVICE=product_service
```

### Linting

To lint all code:

```bash
make lint
```

To lint a specific service:

```bash
make lint SERVICE=<service_name>
```

### Formatting

To format all code:

```bash
make format
```

## Service Endpoints

### API Gateway Service

- **URL**: http://localhost:8000
- **Health Check**: GET /health
- **API Documentation**: GET /docs

### User Service

- **URL**: http://localhost:8001
- **Health Check**: GET /health
- **API Documentation**: GET /docs

### Product Service

- **URL**: http://localhost:8002
- **Health Check**: GET /health
- **API Documentation**: GET /docs

### Notification Service

- **URL**: http://localhost:8003
- **Health Check**: GET /health
- **API Documentation**: GET /docs

## CI/CD

The project includes GitHub Actions workflows for continuous integration and deployment:

- **Test Workflow**: Runs on pull requests and pushes to main. It runs linting, type checking, and tests for all services.
- **Deploy Workflow**: Runs on pushes to main and tags. It builds and pushes Docker images for changed services and deploys them to the appropriate environment.

### Deployment Strategy

The deployment workflow uses a smart detection system to determine which services have changed and only builds and deploys those services. This is particularly useful in a monorepo with multiple services, as it avoids unnecessary builds and deployments.

If changes are made to shared code, all services are rebuilt and deployed.

## Development Guidelines

### Adding a New Service

1. Create a new directory under `services/` with the service name
2. Create a `BUILD` file for the service
3. Implement the service code in the `src/` directory
4. Add tests in the `tests/` directory
5. Create a `Dockerfile` for the service
6. Add the service to the `docker-compose.yml` file
7. Update the CI/CD workflows if necessary

### Making Changes to Existing Services

1. Make the necessary changes to the service code
2. Add or update tests as needed
3. Run the tests for the service: `make test SERVICE=<service_name>`
4. Run the linter for the service: `make lint SERVICE=<service_name>`
5. Format the code: `make format`
6. Commit and push your changes

### Working with Shared Code

The `shared/` directory contains code that is shared across multiple services. When making changes to shared code, be aware that it may affect multiple services. Always run tests for all services after making changes to shared code.

## Troubleshooting

### Common Issues

- **Pants Build Issues**: If you encounter issues with Pants, try running `./pants clean-all` to clean the build cache.
- **Docker Compose Issues**: If you encounter issues with Docker Compose, try running `docker-compose down -v` to remove all containers and volumes, then run `make run-all` again.
- **Database Issues**: If you encounter database issues, check that the PostgreSQL container is running and that the database connection settings are correct.

### Logs

- **Service Logs**: When running with Docker Compose, you can view the logs for a specific service with `docker-compose logs <service_name>`.
- **Database Logs**: You can view the PostgreSQL logs with `docker-compose logs postgres`.
- **Redis Logs**: You can view the Redis logs with `docker-compose logs redis`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
