# Mini Orders Service

## Overview

Mini Orders Service is a Laravel-based backend application designed to manage customer orders through a REST API.

The application allows users to:

- Create new orders.
- Process orders asynchronously using Laravel Queues.
- Consume data from an external public API.
- Store relevant external information in the order record.
- Retrieve orders through REST endpoints.

The project was developed following Laravel best practices, emphasizing separation of concerns, dependency injection, service layers, and background job processing.

---

## Technology Stack

- PHP 8+
- Laravel 13
- SQLite
- Laravel Queue (Database Driver)
- Composer
- Python 3
- python-telegram-bot

---

## Architecture

The application follows a layered architecture:

```text
Controller
    ↓
Service Layer
    ↓
External API Service
    ↓
Queue Job
    ↓
Model / Database
```

### Components

#### OrderController

Responsible for handling HTTP requests and responses.

#### OrderService

Contains the business logic related to order creation and processing.

#### ExternalApiService

Encapsulates all communication with external APIs.

#### ProcessOrderJob

Processes orders asynchronously using Laravel Queues.

#### Order Model

Represents order records stored in the database.

---

## Features

### Create Orders

Creates a new order and dispatches a queue job for processing.

### Process Orders in Background

Each order is processed asynchronously.

The processing flow:

1. Retrieve order from database.
2. Call external public API.
3. Store relevant data from API response.
4. Mark order as processed.
5. If an error occurs, mark order as failed and log the error.

### Retrieve Orders

- List all orders.
- Retrieve a specific order by ID.

### Telegram Integration

A Telegram bot was implemented as an additional interface for interacting with the Orders API.

Users can:

- Create orders from Telegram.
- Retrieve orders.
- View order details.

---

## Database Structure

### orders

| Column         | Type            |
| -------------- | --------------- |
| id             | bigint          |
| customer_name  | string          |
| customer_email | string          |
| total_amount   | decimal(10,2)   |
| status         | string          |
| external_data  | string nullable |
| error_message  | text nullable   |
| created_at     | timestamp       |
| updated_at     | timestamp       |

### queue tables

Laravel database queue tables are used to process background jobs.

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd mini-orders-service
```

### Install Dependencies

```bash
composer install
```

### Environment Configuration

Copy the environment file:

```bash
cp .env.example .env
```

Generate application key:

```bash
php artisan key:generate
```

---

## Database Configuration

```env
DB_CONNECTION=sqlite

QUEUE_CONNECTION=database
```

Create the database:

```sql
CREATE DATABASE mini_orders;
```

---

## Run Migrations

```bash
php artisan migrate
```

---

## Start Application

Start Laravel server:

```bash
php artisan serve
```

Application will be available at:

```text
http://127.0.0.1:8000
```

---

## Start Queue Worker

In a separate terminal:

```bash
php artisan queue:work
```

This worker is responsible for processing order jobs in the background.

---

# Telegram Bot Integration

As an additional feature, a Telegram Bot was implemented to interact with the Orders API.

The bot communicates with the Laravel backend through REST API endpoints and allows users to:

- Create new orders.
- List existing orders.
- Retrieve order details by ID.

Architecture:

```text
Telegram Bot (Python)
        ↓
Laravel REST API
        ↓
SQLite
        ↓
Queue Worker
        ↓
External API (GitHub Zen)
```

---

## Telegram Bot Setup

Navigate to the bot directory:

```bash
cd telegram-bot
```

Create virtual environment:

```bash
python3 -m venv venv
```

Activate virtual environment:

### Mac/Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Telegram Bot Configuration

Create a `.env` file inside the `telegram-bot` folder:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
LARAVEL_API_URL=http://127.0.0.1:8000/api
```

---

## Running the Telegram Bot

Start the bot:

```bash
python bot.py
```

---

## Telegram Commands

### Start Bot

```text
/start
```

Displays available commands.

---

### Create Order

```text
/create_order Jessica|jessica@test.com|3000
```

Example response:

```text
Order created successfully

ID: 5
Customer: Jessica
Email: jessica@test.com
Amount: 3000
Status: pending
```

---

### List Orders

```text
/orders
```

Returns the latest orders.

---

### Get Order Details

```text
/order 1
```

Returns detailed information for a specific order.

---

## Telegram Bot Link

```text
https://t.me/mini_orders_bot
```

---

## API Endpoints

### Create Order

**POST**

```http
/api/orders
```

Request:

```json
{
    "customer_name": "Jessica",
    "customer_email": "jessica@test.com",
    "total_amount": 3000,
    "description": "2 MacBooks Pro + 1 Monitor"
}
```

Response:

```json
{
    "message": "Order created successfully",
    "data": {
        "id": 1,
        "customer_name": "Ricardo Saucedo",
        "customer_email": "ricardo@test.com",
        "total_amount": 1500.5,
        "status": "pending"
    }
}
```

---

### List Orders

**GET**

```http
/api/orders
```

Response:

```json
[
    {
        "id": 1,
        "customer_name": "Ricardo Saucedo",
        "customer_email": "ricardo@test.com",
        "total_amount": 1500.5,
        "status": "processed",
        "external_data": "Avoid administrative distraction."
    }
]
```

---

### Get Order Details

**GET**

```http
/api/orders/{id}
```

Example:

```http
/api/orders/1
```

---

## External API Integration

The application integrates with:

```text
https://api.github.com/zen
```

The response text is stored in the `external_data` field of the order.

Example:

```text
Avoid administrative distraction.
```

---

## Error Handling

If an external API request fails:

- Order status is changed to `failed`.
- Error message is stored in `error_message`.
- Error details are logged using Laravel logging.

Logs are available at:

```text
storage/logs/laravel.log
```

---

## Example cURL Requests

Create Order:

```bash
curl -X POST http://127.0.0.1:8000/api/orders \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{
  "customer_name":"Ricardo Saucedo",
  "customer_email":"ricardo@test.com",
  "total_amount":1500.50
}'
```

List Orders:

```bash
curl http://127.0.0.1:8000/api/orders
```

Get Order Details:

```bash
curl http://127.0.0.1:8000/api/orders/1
```

---

## Design Decisions

- Controllers remain lightweight.
- Business logic is delegated to services.
- External integrations are isolated.
- Queue processing is handled through Jobs.
- Dependency Injection is used throughout the application.
- Laravel Resources are used to format API responses.
- Form Requests are used for validation.
