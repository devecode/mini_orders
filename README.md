# Mini Orders Service

Overview

Mini Orders Service is a Laravel-based backend application designed to manage customer orders through a REST API.

The application allows users to:

* Create customer orders.
* Process orders asynchronously using Laravel Queues.
* Consume data from an external public API.
* Store external API responses in the database.
* Retrieve orders through REST endpoints.
* Interact with the system through a Telegram Bot.

The project was developed following Laravel best practices, emphasizing:

* Separation of concerns
* Service Layer architecture
* Dependency Injection
* Background Job Processing
* API Resources
* Form Request Validation
* Automated Testing

⸻

## Technology Stack

* PHP 8+
* Laravel 13
* SQLite
* Laravel Queue (Database Driver)
* Laravel Sanctum
* Scribe (API Documentation)
* PHPUnit
* Python 3
* python-telegram-bot

⸻

## Architecture

The application follows a layered architecture:

Controller
    ↓
Service Layer
    ↓
External API Service
    ↓
Queue Job
    ↓
Model / Database

Components

OrderController

Responsible for handling HTTP requests and responses.

OrderService

Contains the business logic related to order creation and order processing.

ExternalApiService

Encapsulates all communication with external APIs.

ProcessOrderJob

Processes orders asynchronously using Laravel Queues.

Order Model

Represents order records stored in the database.

⸻

## Features

Orders Management

* Create orders
* Retrieve all orders
* Retrieve order details
* Validate incoming requests
* Store order descriptions

Background Processing

Orders are processed asynchronously through Laravel Queues.

Processing flow:

1. Create order
2. Dispatch ProcessOrderJob
3. Consume external API
4. Store external data
5. Update order status
6. Handle failures and log errors

## External API Integration

The application integrates with an external API configured through Laravel services.

Example:

https://api.github.com/zen

Returned data is stored in the external_data field.

## API Documentation

The project uses Scribe to automatically generate:

* HTML Documentation
* OpenAPI Specification
* Postman Collection

Documentation URLs:

/docs
/docs.postman
/docs.openapi

Automated Testing

Feature tests cover:

* Listing orders
* Creating orders
* Retrieving order details
* Validation rules
* 404 responses
* Queue job dispatching

Run tests:

php artisan test

⸻

## Database Structure

orders

Column	Type
id	bigint
customer_name	string
customer_email	string
total_amount	decimal(10,2)
description	text nullable
status	string
external_data	text nullable
error_message	text nullable
created_at	timestamp
updated_at	timestamp

⸻

## Installation

Clone Repository

git clone <repository-url>
cd mini-orders-service

Install Dependencies

composer install

Environment Configuration

cp .env.example .env
php artisan key:generate

Example configuration:

DB_CONNECTION=sqlite
QUEUE_CONNECTION=database
EXTERNAL_API_URL=https://api.github.com/zen

⸻

## Database Setup

Run migrations:

php artisan migrate

⸻

## Running the Application

Start Laravel server:

php artisan serve

Application URL:

http://127.0.0.1:8000

Start Queue Worker:

php artisan queue:work

⸻

## API Documentation Setup

Install Scribe:

composer require --dev knuckleswtf/scribe

Publish configuration:

php artisan vendor:publish --tag=scribe-config

Generate documentation:

php artisan scribe:generate

Open documentation:

http://127.0.0.1:8000/docs

⸻

## API Endpoints

Create Order

POST

/api/orders

Request:

{
    "customer_name": "Jessica",
    "customer_email": "jessica@test.com",
    "total_amount": 3000,
    "description": "2 MacBooks Pro + 1 Monitor"
}

Response:

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

⸻

List Orders

GET

/api/orders

⸻

Get Order Details

GET

/api/orders/{id}

Example:

/api/orders/1

⸻

## Telegram Bot

The project includes a Telegram Bot that acts as an additional interface to the Orders API.

Features:

* Interactive menu
* Guided order creation
* Order listing
* Order details
* Statistics dashboard

Architecture:

Telegram Bot (Python)
        ↓
Laravel REST API
        ↓
SQLite
        ↓
Queue Worker
        ↓
External API

Bot Configuration

TELEGRAM_BOT_TOKEN=your_bot_token
LARAVEL_API_URL=http://127.0.0.1:8000/api

Run Bot

python bot.py

⸻

Error Handling

If the external API request fails:

* Order status becomes failed
* Error message is stored in error_message
* Error is logged in Laravel logs

Log file:

storage/logs/laravel.log

⸻

Design Decisions

* Controllers remain lightweight.
* Business logic is delegated to services.
* External integrations are isolated.
* Queue processing is handled through Jobs.
* Dependency Injection is used throughout the application.
* Laravel Resources format API responses.
* Form Requests handle validation.
* Feature Tests validate API behavior.
* Scribe generates API documentation automatically.
