"""
Main application entry point for the Smart Irrigation API.
Handles FastAPI app initialization, middleware, rate limiting, exception handlers,
database lifespan events, and AWS Lambda integration.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from backend.config import IS_AWS_LAMBDA
from routers import auth, zones
from database.postgres_repo import init_db

@asynccontextmanager
async def lifespan(_: FastAPI):
    """
        Manages application startup and shutdown events.
        Automatically initializes the database tables on startup.
        """
    try:
        init_db()
        print("Базата данни е проверена и основните таблици са създадени успешно.")
    except Exception as e:
        print(f"Грешка при инициализация на базата данни: {e}")
    yield

# Initialize FastAPI application with dynamic titles and root paths based on environment
app = FastAPI(
    title="Smart Irrigation API (Cloud - AWS)" if IS_AWS_LAMBDA else "Smart Irrigation API (Local - Docker)",
    root_path="/PROD/smart-irrigation-api" if IS_AWS_LAMBDA else "",
    lifespan=lifespan
)

# Configure CORS policies
app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Rate Limiter based on client IP address
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app.state.limiter = limiter # type: ignore
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


"""
Custom exception handler for validation errors.
Cleans up error details by removing raw input objects for a cleaner response.
"""
@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(_request: Request, exc: RequestValidationError):
    cleaned_errors = []
    for err in exc.errors():
        err_dict = dict(err)
        err_dict.pop("input", None)
        cleaned_errors.append(err_dict)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": cleaned_errors},
    )

# Register API route modules
app.include_router(auth.router)
app.include_router(zones.router)


def handler(event, context):
    """
        AWS Lambda handler function using Mangum adapter.
        Translates AWS API Gateway events to ASGI for FastAPI execution.
        """
    asgi_handler = Mangum(app)
    return asgi_handler(event, context)



