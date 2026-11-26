#!/bin/bash
set -e

LOG_FILE="aws_deploy/build_lambda.log"
mkdir -p aws_deploy
: > "$LOG_FILE"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "--- Cleaning up old caches and archives ---"
rm -f "aws_deploy/lambda.zip"
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# Install AWS-compatible dependencies into the package directory, excluding local/unsupported libraries
grep -vE "^(psycopg2|sqlalchemy|boto3|uvicorn|pytest|httpx)" requirements.txt > requirements_lambda.tmp
pip install --platform manylinux2014_x86_64 --target aws_deploy/package --implementation cp --python-version 3.11 --only-binary=:all: -r requirements_lambda.tmp
rm requirements_lambda.tmp

echo "--- Removing unnecessary metadata and licenses to reduce package size ---"
find aws_deploy/package -type d -name "test*" -exec rm -rf {} + 2>/dev/null || true
find aws_deploy/package -type f -name "*.md" -delete 2>/dev/null || true
find aws_deploy/package -name "*.so" -exec strip {} + 2>/dev/null || true

find . -maxdepth 1 ! -name '.' ! -name 'aws_deploy' -exec cp -r {} aws_deploy/package/ \;
cd aws_deploy/package
zip -9 -r ../lambda.zip . \
  -x "aws_deploy*" \
  -x "requirements*" \
  -x ".git*" \
  -x "docker-compose.yaml" \
  -x ".env" \
  -x "build_lambda.sh" \
  -x "*.pyc" \
  -x "*.pyi" \
  -x "tests*" \
  -x "*test_*.py" \
  -x "infra*" \
  -x "venv*" \
  -x ".venv*" \
  -x "__pycache__*" \
  -x "*__pycache__*" \
  -x "pytest*" \
  -x "frontend*" \
  -x ".pytest_cache*"
cd ../../

echo "--- Cleaning up temporary build directory ---"
rm -rf aws_deploy/package

echo "--- Done! Lambda deployment archive size: ---"
chmod 755 aws_deploy/lambda.zip
ls -lh aws_deploy/lambda.zip