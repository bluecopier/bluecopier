# TODO: VPC
# Lambda deployment options
# * On VPC
# * Iff VPC, allow external access
# * Allow to specify VPC

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.15.0"
    }
  }
  required_version = "~> 1.0"
}

provider "aws" {
  region = var.region_name
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam-for-lambda-${var.function_name}"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Sid       = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },

    ]
  })
}

resource "aws_iam_policy" "function_logging_policy" {
  name   = "function-logging-policy-${var.function_name}"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Action : [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Effect : "Allow",
        Resource : "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "function_logging_policy_attachment" {
  role       = aws_iam_role.iam_for_lambda.id
  policy_arn = aws_iam_policy.function_logging_policy.arn
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

// ! if blueprint.feature_enabled("zip")
data "archive_file" "lambda_function_zip" {
  type        = "zip"
  output_path = "package.zip"
  source_dir  = "${path.module}/${var.source_root}"
}
// ! elif blueprint.feature_enabled("docker")
data "aws_ecr_repository" "lambda_ecr_repo" {
  name = "lambda-${var.function_name}"
}
// ! endif

resource "aws_lambda_function" "lambda_function" {
  function_name = var.function_name
  depends_on    = [aws_cloudwatch_log_group.lambda_log_group]
  role          = aws_iam_role.iam_for_lambda.arn

// ! if blueprint.feature_enabled("zip")
  filename         = data.archive_file.lambda_function_zip.output_path
  handler          = "handler.lambda_handler"
  source_code_hash = data.archive_file.lambda_function_zip.output_base64sha256
  runtime          = "python3.10"
// ! elif blueprint.feature_enabled("docker")
  image_uri        = "${data.aws_ecr_repository.lambda_ecr_repo.repository_url}:latest"
  package_type     = "Image"
// ! endif
  timeout          = 120
  publish          = true
}

// ! if blueprint.feature_enabled("url")
resource "aws_lambda_function_url" "lambda_function_url" {
  function_name      = aws_lambda_function.lambda_function.arn
  authorization_type = "NONE"
}

output "function_url" {
  description = "AWS Lambda Function URL"
  value       = aws_lambda_function_url.lambda_function_url.function_url
}
// ! endif
