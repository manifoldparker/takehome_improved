# create the S3 bucket
resource "aws_s3_bucket" "working_bucket" {
  bucket = var.bucket_name
  acl    = "private"
  force_destroy = var.destroy_resources
}

# set it to match Amazon's default "block all public access"
resource "aws_s3_bucket_public_access_block" "block" {
  bucket = aws_s3_bucket.working_bucket.id

  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

