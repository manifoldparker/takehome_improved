import boto3
import logging
import datetime
import uuid

## ---- Configuration Variables ---- ##
bucket_name = "kp-manifold-working-bucket" # The AWS bucket to store the data in

if __name__ == "__main__":
    print("Hello world")

    s3 = boto3.client('s3')

    file_name = "output.txt"
    full_path = file_name

    s3.put_object(Bucket=bucket_name,
                  Key=full_path,
                  Body="hello world")

    print("Wrote to S3! (probably)")
