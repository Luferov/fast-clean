# Layered architecture

Python is a high-level programming language with a simple and clear syntax, which significantly speeds up development and makes code maintenance easier. Its readability and conciseness allow development teams to add new features and fix bugs quickly without sacrificing quality. This is especially important when building the architecture of complex systems, where clarity and maintainability are paramount.
## Tooling
Two main package managers are used:

1. [uv](https://docs.astral.sh/uv/) - a fast and efficient Python package manager (recommended);
2. [pip](https://pip.pypa.io/) - the standard package dependency manager, used when a project is small, "one-off," and not planned to evolve after development is finished.

The core tooling for backend service development can be split into two sections: tools for the application's runtime work, and tools that assist development. Before starting development, you should review the core tooling listed below:

1. Core tools to use when implementing services:
    - [FastAPI](https://fastapi.tiangolo.com/)
    - [Pydantic](https://docs.pydantic.dev/latest/)
    - [taskiq](https://taskiq-python.github.io)
    - [SqlAlchemy](https://www.sqlalchemy.org/)
    - [Alembic](https://alembic.sqlalchemy.org/en/latest/)
    - [Httpx](https://www.python-httpx.org/)
    - [Python-Jwt](https://pyjwt.readthedocs.io/en/stable/)
    - [Prefect](https://www.prefect.io/)
    - [FastStream](https://faststream.airt.ai/latest)
    - [Taskiq](https://taskiq-python.github.io)
    - [uvicorn](https://www.uvicorn.org/)
    - [sentry](https://docs.sentry.io/platforms/python/)
2. Supporting tools for development:
    - [pytest](https://docs.pytest.org/en/stable/)
    - [pytest-coverage](https://github.com/pytest-dev/pytest-cov)
    - [ruff](https://github.com/astral-sh/ruff)
    - [mypy](https://www.mypy-lang.org/)
    - [pre-commit](https://pre-commit.com/)
    - [ipykernel](https://ipython.readthedocs.io/en/)

## Typical service structure

Below is a typical service structure and a description of directories and files. Deviating from the structure is allowed only with the approval of the tech lead or the competency lead for the corresponding area, as well as the development lead.
```
📁 {{ project name }}           // Project name
| 📁 .vscode                    // vscode configurations
| |- tasks.json                 // File with commands for the TaskExprorer extension
| |- launch.json                // File with commands to start the service with the debugger
| |- settings.json              // vscode editor configuration file
| 📁 migrations                 // Alembic database migrations
| | 📁 versions
| | | 2024_09_11_comment.py     // Database migration file
| | __init__.py
| | env.py                      // Environment settings for generating and applying migrations
| | script.py.mako              // Template for generating migrations
| | utils.py                    // Helper utilities for generating migrations
| 📁 {{ service name }}         // Service name, e.g.: portal, users, processing ...
| | 📁 apps
| | | 📁 healthcheck            // Healthcheck app
| | | | __init__.py             // Healthcheck module imports
| | | | router.py               // Healthcheck app routes
| | | | schemas.py              // Healthcheck app DTO schemas
| | | 📁 users                  // Users app
| | | | 📁 repositories         // Repository layer of the users app
| | | | | __init__.py           // Users repository exports
| | | | | users.py              // Users repository
| | | | | company.py            // Companies repository
| | | | 📁 services             // Service layer of the users app
| | | | | __init__.py           // Users service layer exports
| | | | | users.py              // Users service
| | | | | company.py            // Companies service
| | | | 📁 use_cases            // UseCase (UserStory) layer
| | | | | __init__.py           // UseCases exports
| | | | | user_list.py          // Get user list
| | | | | create_user.py        // Create user
| | | | | update_user.py        // Update user
| | | | | delete_user.py        // Delete user
| | | | 📁 schemas              // Project schemas
| | | | | __init__.py           // Users app schemas exports
| | | | | users.py              // User schemas
| | | | | company.py            // Company schemas
| | | | __init__.py
| | | | container.py            // Build IoC container
| | | | enums.py                // Enumeration constants
| | | | models.py               // Database schema models for the users app
| | | | serializers.py          // Serialization rules and mechanisms
| | | | router.py               // Router and controllers
| | | | exceptions.py           // Exceptions inherited from core/exceptions
| | | 📁 other...               // Other apps in the service
| | 📁 certs                    // Certificates for local development
| | | 📁 elasticsearh           // Certificates for elastic search
| | | | ca.pem                  // Root certificate
| | | 📁 kafka                  // Certificates for kafka
| | | | ca.pem                  // Root certificate
| | | | cert.pem                // User certificate
| | | | key.crt                 // Key
| | 📁 entrypoints              // Application entry points
| | | | __init__.py
| | | | rest.py                 // Start REST applications
| | | | grpc.py                 // Start gRPC applications
| | | __init__.py
| | | db.py                     // Database connection settings
| | | depends.py                // Build IoC container
| | | enums.py                  // List of Enums
| | | exceptions.py             // Set of common exceptions
| | | loggers.py                // Logger settings
| | | models.py                 // Mixins for database schema models
| | | schemas.py                // Common schemas (DTO)
| | | use_cases.py              // Common UseCase elements
| | 📁 cli                      // CLI utilities
| | | 📁 core                   // Common commands module
| | | | __init__.py             // Common commands module
| | | | cryptography.py         // Cryptography command
| | | app.py                    // CLI application entry point
| | | utils.py                  // CLI application utilities
| | __init__.py
| | bootstrap.py                // Application build file
| | exceptions.py               // File with exception handlers
| | main.py                     // Application entry point
| | middleware.py               // Add service middleware
| | router.py                   // Application root router
| | settings.py                 // Application configuration file
| | swagger.py                  // File for additional Swagger configuration
| 📁 seed                       // Data presets for loading into the DBMS
| | 001.users.json              // User template
| | 002.groups.json             // User groups
| 📁 tests                      // Service unit tests
| | 📁 apps                     // Set of apps
| | | 📁 healthcheck            // Tests for the healthcheck app
| | | | conftest.py             // Fixtures related to the healthcheck app
| | | | test_router.py          // Route tests
| | | | test_repositories.py    // Repository layer tests
| | | | test_services.py        // Service layer tests
| | conftest.py                 // File containing fixtures for the entire project
| .dockerignore                 // Ignore during Docker image build
| .env.example                  // Example .env file
| .gitignore                    // Git ignore
| .isort.cfg                    // Import sorting parameters
| .logging.dev.yaml             // Logging parameters for local development
| .logging.yaml                 // Logging parameters for production
| .pre-commit-config.yaml       // Pre-commit configuration
| .python-version               // Python version for pyenv
| .alembic.ini                  // Alembic configuration file
| .docker-compose.yaml          // Infrastructure file for isolated development
| Dockerfile                    // Docker container description file
| entrypoint.sh                 // Docker entrypoint
| Makefile                      // Helper commands file
| manage.py                     // Entry point for CLI utilities
| uv.lock                       // Installed dependencies and their versions
| pyproject.toml                // Project configuration file
| pytest.ini                    // Unit test configuration
| README.md                     // Project and domain description
```
### Project files

```
📁 .devcontainer            // Files for organizing development in a container
📁 .vscode                  // vscode editor settings
📁 migrations               // Alembic migrations for sqlalchemy
📁 seed                     // Seed data and dictionaries
📁 src | {{ service name }} // Project structure files
📁 tests                    // Project tests
.dockerignore               // File for ignoring when copying files into images
.env.example                // Example file for
.gitignore                  // Ignore files in VCS
.pre-commit-config.yaml     // Pre-commit configuration
.python-version             // Python version for package managers
alembic.ini                 // Configuration for running migrations
docker-compose.yaml         // Infrastructure startup file
Dockerfile                  // Docker image build file
entrypoint.sh               // Application entry point
Makefile                    // List of helper commands
manage.py                   // Entry point for CLI commands
pyproject.toml              // Dependencies and project configuration
README.md                   // Project description
```
