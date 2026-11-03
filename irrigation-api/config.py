import os
from logging import CRITICAL

IS_AWS_LAMBDA = bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
API_KEY_NAME = "X-API-KEY"
API_KEY = os.getenv("IRRIGATION_API_KEY")
if not API_KEY:
 raise ValueError("CRITICAL ERROR: IRRIGATION_API_KEY environment variable is not set")

