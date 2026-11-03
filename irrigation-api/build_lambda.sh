#!/bin/bash
set -e


echo "--- Почистване на стари кешове и архиви ---"
rm -f "lambda.zip"
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete


# Инсталираме зависимостите за AWS в папката package
grep -vE "psycopg2|sqlalchemy|boto3|uvicorn" requirements.txt > requirements_lambda.tmp
pip install --platform manylinux2014_x86_64 --target aws_deploy/package --implementation cp --python-version 3.11 --only-binary=:all: -r requirements_lambda.tmp
rm requirements_lambda.tmp

echo "--- Премахване на ненужни метаданни и лицензи за намаляване на размера ---"
find aws_deploy/package -type d -name "test*" -exec rm -rf {} + 2>/dev/null || true
find aws_deploy/package -type f -name "*.md" -delete 2>/dev/null || true
find aws_deploy/package -name "*.so" -exec strip {} + 2>/dev/null || true

find . -maxdepth 1 ! -name '.' ! -name 'aws_deploy' -exec cp -r {} aws_deploy/package/ \;
cd aws_deploy/package
zip -9 -r ../lambda.zip . -x "aws_deploy*" "requirements*" ".git*" "docker-compose.yaml" ".env" "build_lambda.sh" "*.pyc" "*.pyi" 
cd ../../

echo "--------Чистене на папката---------"
rm -rf aws_deploy/package

echo "--- Готово! Ето размера на архива: ---"
chmod 755 aws_deploy/lambda.zip 
ls -lh aws_deploy/lambda.zip

