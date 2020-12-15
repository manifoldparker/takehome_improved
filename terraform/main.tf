terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.2"
    }
  }
}

# set up variables
variable "availability_zone" {
  type    = string
  description = "The availablilty zone all AWS services will be deployed to"
}

variable "bucket_name"{
  type  = string
  description = "The bucket name that this script configures and points to"
}

variable "destroy_resources"{
  type = bool
  description = "A flag indicating if the S3 bucket should be removed even if it has data in it"
}

variable "repo_name"{
  type = string
  description = "stuff"
}

#Set up AWS
provider "aws" {
  profile = "default"
  region  = var.availability_zone
}

# Create the archive for the lambda upload
# data "archive_file" "lambda_pkg" {
#   type = "zip"
#   source_file = "${path.module}/../python/process_json.py"
#   output_path = "${path.module}/lambda_payload.zip"
# }

