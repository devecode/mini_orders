# Mini Orders Service

A Laravel-based REST API for managing customer orders asynchronously, with external API integration and a Telegram Bot interface.

-----

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Features](#features)
- [Database Schema](#database-schema)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Telegram Bot](#telegram-bot)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Error Handling](#error-handling)

-----

## Overview

Mini Orders Service allows you to:

- Create and retrieve customer orders via REST endpoints
- Process orders asynchronously using Laravel Queues
- Consume data from an external public API and store the response
- Interact with the system through a Telegram Bot

The project follows Laravel best practices: **Service Layer**, **Dependency Injection**, **API Resources**, **Form Request Validation**, and **Feature Testing**.

-----

## Tech Stack

|Layer       |Technology                   |
|------------|-----------------------------|
|Backend     |PHP 8+, Laravel 13           |
|Database    |SQLite                       |
|Queue Driver|Laravel Queue (Database)     |
|Auth        |Laravel Sanctum              |
|API Docs    |Scribe                       |
|Testing     |PHPUnit                      |
|Bot         |Python 3, python-telegram-bot|

-----

## Architecture

```
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

**Components:**

- **`OrderController`** — Handles HTTP requests and responses
- **`OrderService`** — Contains business logic for order creation and processing
- **`ExternalApiService`** — Encapsulates communication with external APIs
- **`ProcessOrderJob`** — Processes orders asynchronously via Laravel Queues
- **`Order`** — Eloquent model representing order records

-----

## Features

### Orders Management

- Create, list, and retrieve orders
- Input validation via Form Requests
- Responses formatted with API Resources

### Background Processing

Orders are processed asynchronously through the following flow:

```
1. Create order
2. Dispatch ProcessOrderJob
3. Consume external API  →  https://api.github.com/zen
4. Store external data in external_data field
5. Update order status
6. Handle failures and log errors
```

### External API Integration

The application consumes a configurable external API (default: `https://api.github.com/zen`) and stores the response in the `external_data` column.

-----

## Database Schema

### `orders`

|Column          |Type           |
|----------------|---------------|
|`id`            |bigint         |
|`customer_name` |string         |
|`customer_email`|string         |
|`total_amount`  |decimal(10,2)  |
|`description`   |text (nullable)|
|`status`        |string         |
|`external_data` |text (nullable)|
|`error_message` |text (nullable)|
|`created_at`    |timestamp      |
|`updated_at`    |timestamp      |

-----

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd mini-orders-service
```

### 2. Install dependencies

```bash
composer install
```

### 3. Configure environment

```bash
cp .env.example .env
php artisan key:generate
```

Update `.env` with:

```env
DB_CONNECTION=sqlite
QUEUE_CONNECTION=database
EXTERNAL_API_URL=https://api.github.com/zen
```

### 4. Run migrations

```bash
php artisan migrate
```

-----

## Running the Application

### Start the development server

```bash
php artisan serve
# → http://127.0.0.1:8000
```

### Start the queue worker

```bash
php artisan queue:work
```

> Both processes must be running for orders to be processed correctly.

-----

## API Endpoints

### Create Order

```
POST /api/orders
```

**Request body:**

```json
{
    "customer_name": "Jessica",
    "customer_email": "jessica@test.com",
    "total_amount": 3000,
    "description": "2 MacBooks Pro + 1 Monitor"
}
```

**Response `201`:**

```json
{
    "message": "Order created successfully",
    "data": {
        "id": 1,
        "customer_name": "Jessica",
        "customer_email": "jessica@test.com",
        "total_amount": 3000,
        "description": "2 MacBooks Pro + 1 Monitor",
        "status": "pending"
    }
}
```

-----

### List Orders

```
GET /api/orders
```

-----

### Get Order Details

```
GET /api/orders/{id}
```

**Example:** `GET /api/orders/1`

-----

## Telegram Bot

An interactive Telegram Bot acts as an additional interface to the API.

### Features

- Interactive menu for guided navigation
- Create orders step by step
- List and view order details
- Statistics dashboard

### Architecture

```
Telegram Bot (Python)
        ↓
Laravel REST API
        ↓
SQLite + Queue Worker
        ↓
External API
```

### Configuration

Add to your `.env` (or bot config):

```env
TELEGRAM_BOT_TOKEN=your_bot_token
LARAVEL_API_URL=http://127.0.0.1:8000/api
```

### Run the bot

```bash
python bot.py
```

-----

## Testing

Feature tests cover: listing orders, creating orders, order details, validation rules, 404 responses, and queue job dispatching.

```bash
php artisan test
```

-----

## API Documentation

The project uses [Scribe](https://scribe.knuckles.wtf/) to auto-generate documentation.

### Setup

```bash
composer require --dev knuckleswtf/scribe
php artisan vendor:publish --tag=scribe-config
php artisan scribe:generate
```

### Documentation URLs

|Format            |URL            |
|------------------|---------------|
|HTML              |`/docs`        |
|OpenAPI           |`/docs.openapi`|
|Postman Collection|`/docs.postman`|

-----

## Error Handling

If the external API call fails during job processing:

- Order `status` is set to `failed`
- The error message is stored in `error_message`
- The error is logged in `storage/logs/laravel.log`

-----

## Design Decisions

- Controllers are kept **thin** — no business logic
- Business logic lives in **Service classes**
- External integrations are **isolated** in their own service
- Queue processing is handled through **dedicated Jobs**
- **Dependency Injection** is used throughout
- **Laravel Resources** format all API responses
- **Form Requests** handle input validation
- **Feature Tests** validate end-to-end API behavior
- **Scribe** generates API documentation automatically