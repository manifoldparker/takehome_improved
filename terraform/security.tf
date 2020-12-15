# Traffic to the ECS cluster
resource "aws_security_group" "aws_ecs_tasks" {
  name = "${var.app_name}-ecs-tasks"
  description = "task association"
  vpc_id = aws_vpc.aws-vpc.id
  ingress {
    protocol = "tcp"
    from_port = 80
    to_port = 80
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    protocol = "-1"
    from_port = 0
    to_port = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "${var.app_name}-ecs-tasks"
  }
}

resource "aws_iam_role" "kp_ecs_task_role" {
  name               = "kp_ecs_taskrole"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json
}

data "aws_iam_policy_document" "ecs_assume_role" {
  version = "2012-10-17"
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      identifiers = ["ecs-tasks.amazonaws.com"]
      type        = "Service"
    }
  }
}

data "aws_iam_policy_document" "ecs_role_permissions" {
  statement {
    effect  = "Allow"
    actions = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.working_bucket.arn}/*"]
  }
}

resource "aws_iam_policy" "ecs_role_permissions" {
  name               = "ecs_role_permissions"
  policy             = data.aws_iam_policy_document.ecs_role_permissions.json
}

resource "aws_iam_role_policy_attachment" "ecs_role_permissions" {
  role       = aws_iam_role.kp_ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_role_permissions.arn
}