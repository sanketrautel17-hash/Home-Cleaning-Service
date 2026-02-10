"""
Home Cleaning Service API
=========================
Main FastAPI application configuration.
Includes all routers, middleware, and startup/shutdown events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from core.apis.routers.auth_router import router as auth_router
from core.apis.routers.user_router import router as user_router
from core.apis.routers.cleaner_router import router as cleaner_router
from core.apis.routers.service_router import router as service_router

# Import database functions
from database.database import connect_to_mongo, close_mongo_connection


# =============================================================================
# APPLICATION LIFECYCLE
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown events.

    - On startup: Connect to MongoDB
    - On shutdown: Close MongoDB connection
    """
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


# =============================================================================
# CREATE APPLICATION
# =============================================================================

app = FastAPI(
    title="Home Cleaning Service API",
    description="""
## Home Cleaning Service Marketplace API

A digital marketplace platform connecting independent home cleaning 
professionals with customers seeking cleaning services.

### Features:
- 🔐 **Authentication**: JWT-based login with access & refresh tokens
- 👤 **User Management**: Customer and Cleaner profiles
- 🧹 **Services**: Cleaners create custom service packages (coming soon)
- 📅 **Bookings**: Search, book, and manage cleaning services (coming soon)
- ⭐ **Reviews**: Rate and review completed services (coming soon)
- 💳 **Payments**: Secure payment processing (coming soon)

### User Roles:
- **Customer**: Book cleaning services, leave reviews
- **Cleaner**: Create services, accept bookings, earn money
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# =============================================================================
# MIDDLEWARE
# =============================================================================

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# REGISTER ROUTERS
# =============================================================================

# Auth routes: /api/auth/*
app.include_router(auth_router)

# User routes: /api/users/*
app.include_router(user_router)

# Cleaner routes: /api/cleaners/*
app.include_router(cleaner_router)

# Service routes: /api/services/*
app.include_router(service_router)


# =============================================================================
# ROOT ENDPOINTS
# =============================================================================


@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - API information.

    Returns basic API info and documentation links.
    """
    return {
        "message": "Welcome to Home Cleaning Service API",
        "status": "running",
        "version": "1.0.0",
        "docs": {"swagger": "/docs", "redoc": "/redoc", "openapi": "/openapi.json"},
        "endpoints": {"auth": "/api/auth", "users": "/api/users"},
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns the current health status of the API.
    """
    return {"status": "healthy", "database": "connected"}
