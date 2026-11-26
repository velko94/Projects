# Base invoke URL for the HTTP API stage (e.g., https://<api-id>.execute-api.eu-central-1.amazonaws.com/PROD)
output "api_endpoint" {
  description = "Invoke URL for the deployed HTTP API stage"
  value       = "${aws_apigatewayv2_api.http_api.api_endpoint}/${aws_apigatewayv2_stage.stage.name}"
}

# Static website URL for the frontend S3 bucket
output "frontend_website_url" {
  description = "HTTP website endpoint URL for the frontend S3 bucket"
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
}