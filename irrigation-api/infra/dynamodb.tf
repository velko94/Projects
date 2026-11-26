# DynamoDB table for users: partition key is username (String)
resource "aws_dynamodb_table" "users" {
  name         = var.environment == "prod" ? "users" : "users-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "username"

  attribute {
    name = "username"
    type = "S"
  }
}

# DynamoDB table for zones: partition key is zone_id (Number)
resource "aws_dynamodb_table" "zones" {
  name         = var.environment == "prod" ? "zones" : "zones-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "zone_id"

  attribute {
    name = "zone_id"
    type = "N"
  }
}

