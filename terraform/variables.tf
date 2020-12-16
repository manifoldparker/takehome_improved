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

variable "app_name" {
  type = string
  description = "Application name"
}

variable "app_environment" {
  type = string
  description = "Application environment"
}
