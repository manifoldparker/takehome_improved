resource "aws_athena_workgroup" "workgroup" {
  name = "kp_manifold_wg"
  force_destroy = var.destroy_resources

  configuration {
    result_configuration {
         output_location = "s3://${aws_s3_bucket.working_bucket.bucket}/athena_output/"
    }
  }
}

resource "aws_athena_named_query" "database_query" {
  name      = "kp_address_book_query"
  workgroup = aws_athena_workgroup.workgroup.id
  database  = aws_glue_catalog_database.aws_glue_catalog_database.name
  query     = "SELECT * FROM \"${aws_glue_catalog_database.aws_glue_catalog_database.name}\".\"${var.glue_folder}\" limit 30;"
}