### Task Description

This project implements a Retail CRM system using FastAPI, SQLAlchemy, PostgreSQL, and Docker. It allows for managing
customers, orders, and payments via an API, integrated with RetailCRM.

## How to Run

Clone the repository:

```bash
git clone https://github.com/YuryHaurylenka/Test_Task_RetailCRM.git
cd Test_Task_RetailCRM
```

### Set up environment variables

```bash
RETAILCRM_API_KEY=your_retailcrm_api_key
RETAILCRM_BASE_URL=https://your_retailcrm_url
RETAILCRM_SITE=you_retailcrm_site

POSTGRES_USER=retailcrm_user
POSTGRES_PASSWORD=retailcrm_password
POSTGRES_DB=retailcrm_db
POSTGRES_HOST=postgresql
POSTGRES_PORT=5432
```

### Build and start the project using Docker Compose

```bash
docker compose build
```

### Start the project

```bash
docker compose up
```

## Accessing the API

Once the containers are up and running, you can access the FastAPI documentation at:

```bash
http://localhost:8000/docs
```

## API Endpoints

### Customers

- `GET /api/v1/customers/`
    - Get a list of customers. Supports filtering by name, email, registration date, pagination.

- `POST /api/v1/customers/`
    - Create a new customer.

### Orders

- `GET /api/v1/orders/customer/{customer_id}`
    - Get a list of orders for a specific customer.

- `POST /api/v1/orders/`
    - Create a new order.

### Payments

- `POST /api/v1/orders/{order_id}/payments`
    - Create a payment for a specific order.

