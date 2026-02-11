
# TalaTrivia API

## Prerequisites

- Python 3.11+
- Docker & Docker Compose

### Quick Start (Docker)

1.  **Build and run the container:**

    ```bash
    docker compose up --build
    ```

    The API will be available at [http://localhost:8000](http://localhost:8000).

## Testing

Run tests with `pytest`:

```bash
python -m pytest
```

## Linting & Formatting

Run `ruff` for linting:

```bash
ruff check .
```

Run `black` for formatting:

```bash
black .
```
