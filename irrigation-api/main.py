from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from config import  IS_AWS_LAMBDA
from routers import auth, zones

if IS_AWS_LAMBDA:
    app = FastAPI(title="Smart irrigation api (PROD)", root_path="/PROD/smart-irrigation-api")
else:
    app = FastAPI(title="Smart irrigation api (ACC)")
    from database.connection import engine, Base
    Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    cleaned_errors = []
    for err in exc.errors():
        err_dict = dict(err)
        err_dict.pop("input", None)
        cleaned_errors.append(err_dict)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": cleaned_errors},
    )

app.include_router(auth.router)
app.include_router(zones.router)

def handler(event, context):
    asgi_handler = Mangum(app)
    return asgi_handler(event, context)