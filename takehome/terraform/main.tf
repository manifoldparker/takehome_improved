terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 2.70"
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

variable "glue_folder"{
  type  = string
  description = "The folder within S3 that the python script is writing data to"
}

variable "destroy_resources"{
  type = bool
  description = "A flag indicating if the S3 bucket should be removed even if it has data in it"
}

#Set up AWS
provider "aws" {
  profile = "default"
  region  = var.availability_zone
}

# Create the archive for the lambda upload
data "archive_file" "lambda_pkg" {
  type = "zip"
  source_file = "${path.module}/../python/process_json.py"
  output_path = "${path.module}/lambda_payload.zip"
}

