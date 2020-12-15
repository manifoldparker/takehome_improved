
#deploy the lambda function
resource "aws_iam_role" "iam_for_lambda" {
  name = "kp_iam_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# attach the policy that allows the role to write to S3
resource "aws_iam_role_policy_attachment" "lambda-attach" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaExecute"
}

# create the actual lambda
resource "aws_lambda_function" "test_lambda" {
  filename      = data.archive_file.lambda_pkg.output_path
  function_name = "process_json"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "process_json.lambda_handler"

  runtime = "python3.7"
}