# Frontend S3 bucket: uses the existing prod bucket name or a per-environment name (e.g. acc)
resource "aws_s3_bucket" "frontend" {
  bucket = var.environment == "prod" ? "irrigation-api-fe-velko-125570278217-eu-central-1-an" : "irrigation-api-fe-velko-${var.environment}-eu-central-1"
}

# Enables S3 static website hosting and sets index.html as the default entry document
resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }
}

# Disables S3 Block Public Access settings so the bucket policy can allow public reads
# Note: Once CloudFront with OAC is added later, set these back to true to restrict direct S3 access
resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# Allows anonymous visitors (Principal = "*") to read objects (s3:GetObject) for website hosting
# depends_on ensures public access block changes are applied before attaching the policy
resource "aws_s3_bucket_policy" "frontend_public_read" {
  bucket     = aws_s3_bucket.frontend.id
  depends_on = [aws_s3_bucket_public_access_block.frontend]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })
}