"""
Application Configuration module.
Loads environment variables, detects AWS Lambda runtime environment,
and enforces critical security configurations such as API key validation.
"""

import os

# Detect if the application is running inside an AWS Lambda environment
IS_AWS_LAMBDA = bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))

# API Key security settings
API_KEY_NAME = "X-API-KEY"
API_KEY = os.getenv("IRRIGATION_API_KEY")

# Fail-fast check to ensure security credentials are properly provisioned
if not API_KEY:
    raise ValueError("CRITICAL ERROR: IRRIGATION_API_KEY environment variable is not set")