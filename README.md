# TalaTrivia API
[![codecov](https://codecov.io/github/brutalchrist/talatrivia/graph/badge.svg?token=KB8AQ3WAQA)](https://codecov.io/github/brutalchrist/talatrivia)

## Prerequisites

- Python 3.11+
- Docker & Docker Compose

### Quick Start (Docker)

1.  **Build and run the container:**

    ```bash
    docker compose up --build
    ```

    The API will be available at [http://localhost:8000](http://localhost:8000).

2. **Run migrations:**

    Apply migration:

    ```bash
    docker-compose exec api alembic upgrade head
    ```
