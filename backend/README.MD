# Home Cleaning Service API

A digital marketplace platform connecting independent home cleaning professionals with customers seeking cleaning services.

## 🚀 Technology Stack

| Category | Technology |
|----------|------------|
| **Framework** | FastAPI |
| **Database** | MongoDB |
| **ODM** | ODMantic |
| **Async Driver** | Motor |
| **Authentication** | JWT (python-jose) |
| **Password Hashing** | Bcrypt (passlib) |
| **Server** | Uvicorn |

## 📁 Project Structure

```
backend/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── test_api.py            # API test script
│
├── core/
│   ├── __init__.py
│   └── apis/
│       ├── api.py         # FastAPI app configuration
│       ├── routers/       # API route handlers
│       │   ├── auth_router.py
│       │   └── user_router.py
│       └── schemas/       # Pydantic models
│           ├── requests/  # Request validation
│           └── responses/ # Response serialization
│
├── models/                 # ODMantic database models
│   └── user_model.py
│
├── controllers/            # Business logic layer
│   ├── auth_controller.py
│   └── user_controller.py
│
├── cruds/                  # Database operations
│   └── user_crud.py
│
├── commons/                # Shared utilities
│   ├── security.py        # JWT & password utilities
│   ├── dependencies.py    # FastAPI dependencies
│   └── logger.py          # Logging configuration
│
├── database/               # MongoDB connection
│   └── database.py
│
└── logs/                   # Application logs
    └── debug.log
```

## 🔧 Setup & Installation

### Prerequisites
- Python 3.10+
- MongoDB (local or cloud)

### 1. Create Virtual Environment
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file with:
```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/home_cleaning_service
DATABASE_NAME=Home_Cleaning_Service

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Reset Token Expiry
RESET_TOKEN_EXPIRE_MINUTES=60
```

### 4. Run the Server
```bash
python -m uvicorn core.apis.api:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Health Check
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info & docs links |
| GET | `/health` | Health check |

### Authentication (`/api/auth`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/register` | Create new account | ❌ |
| POST | `/login` | Login & get tokens | ❌ |
| POST | `/refresh` | Refresh access token | ❌ |
| POST | `/forgot-password` | Request password reset | ❌ |
| POST | `/reset-password` | Reset password with token | ❌ |
| POST | `/change-password` | Change password | ✅ |
| GET | `/me` | Get current user | ✅ |
| POST | `/verify-email` | Verify email | ❌ |
| POST | `/send-verification` | Resend verification | ✅ |

### Users (`/api/users`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/me` | Get profile | ✅ |
| PUT | `/me` | Update profile | ✅ |
| DELETE | `/me` | Delete account | ✅ |
| POST | `/me/deactivate` | Deactivate account | ✅ |
| GET | `/{user_id}` | Get public profile | ❌ |
| GET | `/` | List users | ❌ |

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Register** or **Login** to receive:
   - `access_token` (30 min expiry)
   - `refresh_token` (7 days expiry)

2. **Include token** in requests:
   ```
   Authorization: Bearer <access_token>
   ```

3. **Refresh** when access token expires using refresh token

## 🧪 Testing

Run the API tests:
```bash
# Start server first
python -m uvicorn core.apis.api:app --port 8000

# In another terminal
python test_api.py
```

## 📋 Development Phases

### ✅ Phase 1: Foundation & Core (COMPLETE)
- [x] Project structure setup
- [x] Database connection (MongoDB + ODMantic)
- [x] User model
- [x] Authentication schemas
- [x] Security utilities (JWT, password hashing)
- [x] User CRUD operations
- [x] Auth controller
- [x] Auth router
- [x] User controller
- [x] User router
- [x] API testing

### ✅ Phase 2: Cleaner Profiles (COMPLETE)
- [x] Cleaner profile model
- [x] Service packages model
- [x] Cleaner CRUD operations
- [x] Service CRUD operations
- [x] Cleaner search endpoints
- [x] Location-based search

### ✅ Phase 3: Booking System (COMPLETE)
- [x] Booking model
- [x] Booking workflow
- [x] Availability management
- [x] Booking status updates

### ✅ Phase 4: Reviews & Ratings (COMPLETE)
- [x] Review model
- [x] Review submission
- [x] Rating calculations

### ✅ Phase 5: Payments (COMPLETE)
- [x] Payment integration
- [x] Payment records
- [x] Payment verification
- [ ] Commission handling
- [ ] Payout processing

## 👤 User Roles

| Role | Capabilities |
|------|-------------|
| **Customer** | Book services, leave reviews |
| **Cleaner** | Create services, accept bookings |

## 📝 License

This project is for educational purposes.

---

**Built with ❤️ using FastAPI + MongoDB**
