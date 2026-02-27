# 🚛 Enterprise Logistics Platform

A powerful, multi-tenant logistics management system built with **Django** and **Django REST Framework**. This platform is designed to handle complex logistics operations, including shipment tracking, driver management, automated payments, and secure webhook integrations.

---

## 🚀 Key Features

- **🏢 Multi-Tenancy**: Secure data isolation. Each tenant (logistics provider) only sees their own data.
- **📦 Shipment Lifecycle**: Full management from order placement to final delivery.
- **🚚 Fleet & Driver Management**: Track vehicles, manage driver assignments, and KYC verification.
- **💳 Integrated Payments**: Seamless Razorpay integration for secure transactions.
- **💰 Wallet & Payout System**: Automated driver earnings calculation and wallet management.
- **📍 Real-time Tracking**: Live status updates and historical tracking data for all shipments.
- **🔌 Advanced Webhook System**:
  - **Inbound**: Securely receive events from Razorpay and Shiprocket with HMAC signature verification.
  - **Outbound**: Programmable triggers for status changes, payments, and payouts.
  - **Reliability**: Built-in retry mechanism with exponential backoff for failed deliveries.
- **📜 Audit Logging**: Comprehensive tracking of all sensitive changes and system events.

---

## 📂 Project Structure

The project is organized into several specialized Django apps:

| App | Description |
|-----|-------------|
| `accounts` | User authentication, registration, roles, and profile management. |
| `tenants` | Multi-tenancy management and organization isolation logic. |
| `drivers` | Driver profiles, vehicle assignments, and KYC document uploads. |
| `vehicles` | Fleet management, including vehicle types and maintenance tracking. |
| `shipments` | Core logistics logic: shipments, parcels, and rate calculations. |
| `tracking` | Real-time tracking updates and historical location logs. |
| `deliveries` | Delivery attempts, proof of delivery (POD), and completion logic. |
| `payments` | Integration with Razorpay, payment intent creation, and status tracking. |
| `wallet` | Virtual wallet system for users and drivers. |
| `earnings` | Logistics-specific payout calculations and driver commission management. |
| `notifications` | System-wide alerts via email and push notifications. |
| `webhooks` | Both inbound receiver logic and outbound dispatcher with retry support. |
| `auditlogs` | System auditing and sensitive action tracking. |
| `reports` | Analytical reports and data exports (Excel/CSV). |

---

## 🛠️ Tech Stack

- **Backend**: Django 4.2+, Django REST Framework (DRF)
- **Database**: SQLite (Development) / PostgreSQL (Production ready)
- **Authentication**: SimpleJWT (JSON Web Tokens)
- **Utilities**: 
  - `django-filter` (Advanced API filtering)
  - `Pillow` (Image/KYC handling)
  - `Requests` (Outbound webhook delivery)

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- `pip` or `pipenv`

### 2. Installation
```powershell
# Clone the repository
git clone <repository-url>
cd "API program"

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Initialization
```powershell
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run Development Server
```powershell
python manage.py runserver
```
The API will be available at `http://127.0.0.1:8000/`.

---

## 📍 Key API Endpoints

### 🔐 Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | `POST` | Create a new account |
| `/api/auth/login/` | `POST` | Obtain JWT Access/Refresh tokens |
| `/api/auth/token/refresh/` | `POST` | Refresh expired access tokens |

### 📦 Logistics
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/shipments/` | `GET/POST` | List or create shipments |
| `/api/shipments/calculate-rate/` | `POST` | Estimate shipping costs |
| `/api/drivers/` | `GET/POST` | Manage driver profiles |
| `/api/drivers/<uuid>/location/` | `PATCH` | Update driver's live coordinates |

### 🔌 Webhooks
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/webhooks/payment/` | `POST` | **Inbound**: Razorpay event receiver |
| `/api/webhooks/shipment/` | `POST` | **Inbound**: Shiprocket event receiver |
| `/api/webhooks/retry/` | `POST` | **Management**: Retry failed outbound hooks |

---

## 🔒 Security
- **JWT Auth**: All management endpoints require a valid `Authorization: Bearer <token>` header.
- **HMAC Verification**: Inbound webhooks are validated against `RAZORPAY_WEBHOOK_SECRET`.
- **Tenant Middleware**: Automatic data filtering based on the `tenant_id` associated with the user.

---

## 📄 License
This project is licensed under the MIT License.
