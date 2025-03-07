# BAS License Checker

BAS License Checker is an API designed to provide real-time license validation for scripts developed using [Browser Automation Studio (BAS)](https://bablosoft.com/). Unlike traditional license servers, which only verify the license at the script's start, this API allows for license checks during the script's execution. This approach prevents users from running expired licenses for extended periods without re-validation.

---

## Table of Contents

1. [Motivation](#motivation)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Usage](#usage)
   - [API Endpoints](#api-endpoints)
   - [Security](#security)
6. [Testing](#testing)
7. [Contributing](#contributing)
8. [License](#license)
9. [Acknowledgments](#acknowledgments)

---

## Motivation

Native BAS license server validate licenses only at script startup. If a license expires during the script's execution, the system cannot verify it until the script restarts. This gap allows for prolonged use of expired licenses, posing challenges for license enforcement.

BAS License Checker addresses this issue by introducing real-time license validation capabilities. This ensures scripts remain compliant with licensing terms throughout their execution.

---

## Features

- **Real-Time Validation**: Check licenses during script execution.
- **Scalable**: Built with FastAPI and SQLAlchemy for high performance.
- **Secure**: Uses cryptography to ensure safe data transmission and validation.
- **Extensible**: Easily integrates into existing BAS templates.

---

## Prerequisites

- **Docker**: For containerized deployment. [Get Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: For multi-container setup. [Install Docker Compose](https://docs.docker.com/compose/install/)

---

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/bahkadomos/bas_license.git
    cd bas_license
    ```

2. **Set Up Environment**:
    - Copy the example `.env` file:
        ```bash
        cp .env.example .env
        ```
    - Update the `.env` file with your configuration (e.g., database credentials, grafana password, API keys for captcha services etc.).

3. **Generate Keys**:
    - **Set up local dependencies**:
        Create a virtual environment and install required dependencies for key generation:
        ```bash
        python -m venv .venv
        source .venv/bin/activate  # On Windows: .venv\Scripts\activate
        pip install -r requirements.txt
        ```
        Alternatively, install only the necessary modules:
        ```bash
        pip install cryptography==43.0.3
        ```
        Check the current version of the package in `requirements.txt`.

    - **Generate the keys**:
        ```bash
        make keys
        ```
    - Add the generated private key to the `.env` file as:
        ```
        PRIVATE_KEY=<YOUR-BASE64-PRIVATE-KEY>
        ```
    - Save both keys and keep them securely!

4. **Start Services**:
    - Using Docker Compose:
        ```bash
        docker compose up --build
        ```

    This will start the following services:
    - **API Server**: Available at `http://localhost:8000`.
    - **Grafana**: Available at `http://localhost:3000` (default credentials: `admin` / `.env: GRAFANA_PASSWORD`).
    - **Loki**: Integrated for logging (no direct UI, logs are accessible via Grafana).
    - **PostgreSQL**: Database backend.

5. **Access Services**:
    - **API Documentation**:
        Navigate to `http://localhost:8000/docs` for interactive API documentation.
    - **Grafana Dashboards**:
        Visit `http://localhost:3000` to monitor metrics and logs.

---

## Usage

### API Endpoints

1. **Create Task**:

    ```http
    POST /v1/license/
    ```

    **Request Body**:

    ```json
    {
        "username": "string",
        "script_name": "string"
    }
    ```

    **Response**:

    ```json
    {
        "error": false,
        "data": {
            "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "credentials": {
                "username": "string",
                "script_name": "string"
            }
        },
        "server_info": {
            "request_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "created_at": "2024-12-11T15:45:06.793Z"
        }
    }
    ```

2. **Get Task Result**:

    ```http
    POST /v1/license/result/
    ```

    **Request Body**:

    ```json
    {
        "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }
    ```

    **Response**:

    ```json
    {
        "error": false,
        "data": {
            "status": "ok",
            "credentials": {
                "is_expired": true,
                "expires_in": "2024-12-11T15:46:22.282Z"
            }
        },
        "server_info": {
            "request_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "created_at": "2024-12-11T15:46:22.282Z"
        }
    }
    ```

See more detailed swagger documentation here: `http://localhost:8000/docs/`.

### Security

To prevent spoofing the server or replay attacks, the API utilizes a signing mechanism with the `X-Signature` header. The server signs the response body using its private key, and the client must validate this signature using the server's public key.

#### Replay Attack Prevention

Each response contains a `server_info` mapping with an unique `request_id` (UUID) and `created_at` (ISO datetime):
- `request_id` is used to make each body and their hashes unique;
- `created_at` is used to compare server's and current client datetime.

The client should verify:
- `X-Signature` matches the signed body.
- The `created_at` timestamp is within an acceptable range (e.g., less than 1 hour old).

See [examples](examples).

---

## Testing

**Prerequisites**:
- `python 3.13.0` or above;
- `docker` and `docker-compose`;
- [poetry](https://python-poetry.org/docs/#installation).

1. Create local environment (see [Installation](#installation) section).

2. Install all dependencies (including dev) via `poetry`:
    ```bash
    poetry install
    ```

3. Run necessary services using `docker compose`:
    ```bash
    docker compose up --build
    ```
    or run only necessary containers, like postgres.

4. Run tests locally using `pytest`:
    ```bash
    make test
    ```

---

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix:
    ```bash
    git checkout -b feature-name
    ```
3. Commit your changes and push to your branch.
4. Create a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments

- Developed by [bahladamos](mailto:bahladamos@protonmail.com).
- Powered by [FastAPI](https://fastapi.tiangolo.com/) and [SQLAlchemy](https://www.sqlalchemy.org/).
