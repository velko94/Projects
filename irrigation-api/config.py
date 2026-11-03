import os

IS_AWS_LAMBDA = bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
API_KEY_NAME = "X-API-KEY"
API_KEY = os.getenv("IRRIGATION_API_KEY", "КОЙ ПОЛИВА И КОГА")

