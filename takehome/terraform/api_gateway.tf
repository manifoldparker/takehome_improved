#set up the gateway
resource "aws_api_gateway_rest_api" "rest_gw" {
  name        = "json_upload_api"
  description = "Krista Parker Manifold Interview"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# allow the gateway to access the lambda
resource "aws_lambda_permission" "gw_permission" {
   statement_id  = "AllowAPIGatewayInvoke"
   action        = "lambda:InvokeFunction"
   function_name = aws_lambda_function.test_lambda.function_name
   principal     = "apigateway.amazonaws.com"

   source_arn = "${aws_api_gateway_rest_api.rest_gw.execution_arn}/*/*"
}

# configure the resources
# -- resource
# resource "aws_api_gateway_resource" "execute" {
#    rest_api_id = aws_api_gateway_rest_api.rest_gw.id
#    parent_id   = aws_api_gateway_rest_api.rest_gw.root_resource_id
#    path_part   = "execute"
# }

# -- method (post)
resource "aws_api_gateway_method" "method" {
  rest_api_id   = aws_api_gateway_rest_api.rest_gw.id
  resource_id   = aws_api_gateway_rest_api.rest_gw.root_resource_id
  http_method   = "POST"
  authorization = "NONE"
}

# -- integration request
resource "aws_api_gateway_integration" "integration" {
  rest_api_id             = aws_api_gateway_rest_api.rest_gw.id
  resource_id             = aws_api_gateway_rest_api.rest_gw.root_resource_id
  http_method             = aws_api_gateway_method.method.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = aws_lambda_function.test_lambda.invoke_arn
}

# -- method response
resource "aws_api_gateway_method_response" "response_200" {
  rest_api_id = aws_api_gateway_rest_api.rest_gw.id
  resource_id = aws_api_gateway_rest_api.rest_gw.root_resource_id
  http_method = aws_api_gateway_method.method.http_method
  status_code = "200"
  response_models = {
         "application/json" = "Empty"
    }
}

# -- integration response
resource "aws_api_gateway_integration_response" "integration_response" {
  depends_on = [
     aws_api_gateway_integration.integration,
     aws_api_gateway_rest_api.rest_gw,
     aws_api_gateway_method.method,
     aws_api_gateway_method_response.response_200,
   ]
  rest_api_id = aws_api_gateway_rest_api.rest_gw.id
  resource_id = aws_api_gateway_rest_api.rest_gw.root_resource_id
  http_method = aws_api_gateway_method.method.http_method
  status_code = aws_api_gateway_method_response.response_200.status_code
}

# deploy the gateway
resource "aws_api_gateway_deployment" "deploy_config" {
   depends_on = [
     aws_api_gateway_integration.integration,
   ]

   rest_api_id = aws_api_gateway_rest_api.rest_gw.id
   stage_name  = "test"
}

#output the gateway URL
output "base_url" {
  value = aws_api_gateway_deployment.deploy_config.invoke_url
}

# output "base_url_2" {
#   value = aws_api_gateway_resource.execute.path
# }