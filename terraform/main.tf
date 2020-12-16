terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.2"
    }
  }
}

#Set up AWS
provider "aws" {
  profile = "default"
  region  = var.availability_zone
}

