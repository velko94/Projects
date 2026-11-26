# --- IAM Role and Permissions for Lambda ---

# IAM execution role assumed by the Lambda service at runtime via STS
resource "aws_iam_role" "lambda_exec" {
  name = "${var.project_name}-lambda-role-${var.environment}"

  # Trust policy: allows AWS Lambda (sts:AssumeRole) to take on this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# Attaches AWS managed policy granting permission to write execution logs to CloudWatch Logs
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Inline policy restricting DynamoDB access strictly to the users and zones tables
resource "aws_iam_role_policy" "lambda_dynamo" {
  name = "${var.project_name}-dynamo-access-${var.environment}"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Scan",
        "dynamodb:Query"
      ]
      Resource = [
        aws_dynamodb_table.users.arn,
        aws_dynamodb_table.zones.arn
      ]
    }]
  })
}

# --- Lambda Function ---

# FastAPI backend packaged as a deployment zip running on Python 3.11
resource "aws_lambda_function" "api" {
  function_name    = var.environment == "prod" ? "smart-irrigation-api" : "smart-irrigation-api-${var.environment}"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "main.handler" # Entrypoint function in main.py (verify against your actual handler)
  runtime          = "python3.11"
  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path) # Triggers update when zip contents change
  timeout          = 15
  memory_size      = 256

  # Runtime environment variables injected into the Lambda container
  environment {
    variables = {
      DB_TYPE      = "dynamo"
      USERS_TABLE  = aws_dynamodb_table.users.name
      ZONES_TABLE  = aws_dynamodb_table.zones.name
      CORS_ORIGINS = join(",", var.cors_origins) # [CORS] Comma-separated list read by FastAPI middleware
    }
  }
}

# --- HTTP API Gateway ---

# HTTP API (API Gateway v2) fronting the Lambda function
resource "aws_apigatewayv2_api" "http_api" {
  name          = var.environment == "prod" ? "my-irrigation-app-API" : "my-irrigation-app-API-${var.environment}"
  protocol_type = "HTTP"

  # [CORS] API Gateway-level CORS handling for browser preflight (OPTIONS) and cross-origin responses
  cors_configuration {
    allow_origins = var.cors_origins
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["authorization", "content-type"]
    max_age       = 1200
  }
}

# Lambda proxy integration connecting HTTP API to the Lambda invoke ARN
resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

# Catch-all route forwarding HTTP requests to the Lambda integration
resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Deployment stage (e.g. PROD or ACC) with auto_deploy enabled on config/route changes
resource "aws_apigatewayv2_stage" "stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = upper(var.environment)
  auto_deploy = true
}

# Resource-based permission allowing API Gateway to invoke this specific Lambda function
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}