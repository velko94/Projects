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
    try:
        init_db()
        print("Базата данни е проверена и основните таблици са създадени успешно.")
    except Exception as e:
        print(f"Грешка при инициализация на базата данни: {e}")
    yield

app = FastAPI(
    title="Smart Irrigation API (PROD)" if IS_AWS_LAMBDA else "Smart Irrigation API (ACC)",
    root_path="/PROD/smart-irrigation-api" if IS_AWS_LAMBDA else "",
    lifespan=lifespan
)

# CORS с # type: ignore to ignore the pycharm warning
app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter # type: ignore
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom Validation Exception Handler
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

# routers
app.include_router(auth.router)
app.include_router(zones.router)

# AWS Lambda Handler (Mangum)
def handler(event, context):
    asgi_handler = Mangum(app)
    return asgi_handler(event, context)