# 🎟️ Concurrency-Safe Ticketing Engine (BookMyShow Clone)

> A high-throughput, enterprise-grade backend API for a movie ticketing platform with race-condition-safe bookings, dynamic pricing, and lazy-expiration checkout.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-black?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Serverless-4169E1?style=for-the-badge&logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 📌 Overview

This project is a **production-ready backend API** for a movie ticketing platform that handles:

- Movie discovery
- Seat selection
- **Concurrency-safe booking** using PostgreSQL row-level locking
- Payment processing via Razorpay
- Automatic release of abandoned checkouts with a **lazy expiration algorithm**

It's designed to prevent race conditions during high-traffic scenarios (e.g., blockbuster movie releases) and ensures **ACID compliance** for all transactions.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **RBAC Authentication** | JWT-based authentication with roles: Customer, Theatre Admin, SuperAdmin |
| 🛡️ **Concurrency-Safe Checkout** | Uses `FOR UPDATE NOWAIT` to serialize transactions and eliminate double-booking |
| ⏱️ **Lazy Expiration Engine** | Dynamically releases unpaid, locked seats after 10 minutes without cron jobs |
| 💰 **Dynamic Pricing & Seat Tiers** | Supports Standard vs. Premium tiers with real-time price calculation |
| 💳 **Razorpay Integration** | Generates secure payment orders and verifies webhook signatures |
| ✅ **ACID Compliant** | Atomic rollbacks on payment failures or external API errors |

---


## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Framework** | FastAPI (Python 3) |
| **Database** | PostgreSQL (Hosted on Neon.tech) |
| **ORM** | SQLAlchemy + Pydantic |
| **Authentication** | JWT + bcrypt |
| **Payment** | Razorpay Python SDK |
| **Server** | Uvicorn (ASGI) |

---

## 🏗️ Architecture

The application follows a **modular, RESTful architecture**:

```text
ticketing-engine/
├── app/
│   ├── api/v1/        # Routing layer
│   ├── schemas/       # Pydantic models
│   ├── db/            # SQLAlchemy ORM
│   ├── core/          # Config, security, dependencies
│   └── main.py        # App entry point
├── .env
├── requirements.txt
└── README.md
```
### Key Components

1. **Routing Layer** (`app/api/v1/`): Handles HTTP requests and response parsing
2. **Schema Layer** (`app/schemas/`): Validates incoming payloads and serializes outbound data
3. **Database Layer** (`app/db/`): SQLAlchemy ORM mapping and connection pooling
4. **Transaction Engine**: Booking module wraps read-write operations in strict SQL transactions with mid-process rollbacks

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/rithvikreddy14/bookmyshow
cd bookmyshow
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Configuration

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@your-neon-host.neon.tech/dbname

# Security Configuration
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Razorpay Sandbox Credentials
RAZORPAY_KEY_ID=rzp_test_yourkey
RAZORPAY_KEY_SECRET=yoursecret
```

---

## ▶️ Usage

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at **http://127.0.0.1:8000**

### Interactive API Documentation

| Documentation | URL |
|---------------|-----|
| **Swagger UI** | http://127.0.0.1:8000/docs |
| **ReDoc** | http://127.0.0.1:8000/redoc |

---

## 🔌 Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register a new user |
| `/api/v1/auth/login` | POST | Obtain JWT access token |
| `/api/v1/shows/{show_id}/seats` | GET | Retrieve real-time seat map with lazy evaluation |
| `/api/v1/bookings/book` | POST | Lock seats and generate Razorpay Order ID |
| `/api/v1/bookings/verify-payment` | POST | Verify webhook signature and finalize booking |

---

## ✅ Testing

### Authentication Testing

1. Create a user via `/api/v1/auth/register`
2. Login via `/api/v1/auth/login` to get a bearer token
3. Click **Authorize** in Swagger UI and inject the token

### Concurrency Testing

Attempt to hit `/api/v1/bookings/book` for the **same seat_ids** simultaneously from two clients:

- First request → ✅ Success
- Second request → ❌ `409 Conflict` (safely rejected)

### Payment Simulation

1. Call `/api/v1/bookings/book` to get `razorpay_order_id`
2. Simulate frontend checkout using **Razorpay Test Cards**
3. Pass `razorpay_payment_id` and signature to `/api/v1/bookings/verify-payment`

---

## ☁️ Deployment

This API is designed for easy deployment to modern PaaS providers:

| Component | Provider |
|-----------|----------|
| **Database** | Neon.tech (Serverless PostgreSQL) |
| **Application** | Render, Railway, or AWS Elastic Beanstalk |

### Deployment Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Make sure to set all environment variables in your PaaS dashboard.

---

## 🛣️ Roadmap

- [ ] **Background Task Ticketing**: Generate PDF tickets and send email confirmations via `BackgroundTasks`
- [ ] **Advanced Discovery Engine**: Filter movies by city, date, genre, and language
- [ ] **Verified Review System**: Allow ratings only for users with confirmed bookings
- [ ] **Caching Layer**: Integrate Redis to cache static metadata and reduce DB load

---

## 🏆 Why This Project Stands Out

This project demonstrates:

- ✅ **Complex backend workflow architecture**
- ✅ **External API integration** (Razorpay)
- ✅ **Distributed systems problem-solving** (race conditions, concurrency)
- ✅ **Production-ready patterns** (RBAC, ACID transactions, lazy expiration)
- ✅ **Scalable foundation** for e-commerce and booking platforms

It's ideal for showcasing **backend engineering**, **system design**, and **database optimization** skills in interviews and portfolios.

---


## 🙌 Acknowledgements

Built using the amazing open-source ecosystem:

- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- Razorpay SDK
- Uvicorn

---

## 🏁 Final Note

The **Concurrency-Safe Ticketing Engine** successfully demonstrates the ability to architect complex backend workflows, handle external API integrations, and mitigate common distributed system issues like **race conditions** and **double-booking**. It serves as a robust foundation for building **scalable e-commerce and booking platforms**.

