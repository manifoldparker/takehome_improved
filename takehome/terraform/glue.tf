resource "aws_glue_catalog_database" "aws_glue_catalog_database" {
  name = "kp-manifold-interview"
}

resource "aws_iam_role" "iam_for_glue" {
  name = "kp_iam_for_glue"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "glue.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# attach the policy that allows the role to write to S3
resource "aws_iam_role_policy_attachment" "glue-attach-sr" {
  role       = aws_iam_role.iam_for_glue.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy_attachment" "glue-attach-fa" {
  role       = aws_iam_role.iam_for_glue.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_glue_crawler" "crawler" {
  database_name = aws_glue_catalog_database.aws_glue_catalog_database.name
  name          = "kp_manifold_crawler"
  role          = aws_iam_role.iam_for_glue.arn

  s3_target {
    path = "s3://${aws_s3_bucket.working_bucket.bucket}/${var.glue_folder}"
  }
}