resource "aws_ecs_task_definition" "krista" {
  family                   = "krista_fargate"
  cpu                      = 1024
  memory                   = 2048
  requires_compatibilities = ["FARGATE"]
  task_role_arn            = aws_iam_role.kp_ecs_task_role.arn
  execution_role_arn       = "arn:aws:iam::720068558948:role/ecsTaskExecutionRole"
  network_mode             = "awsvpc"
  container_definitions    = <<DEFINITION
[
    {
      "logConfiguration": {
        "logDriver": "awslogs",
        "secretOptions": null,
        "options": {
          "awslogs-group": "/ecs/test_output",
          "awslogs-region": "us-east-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "image": "720068558948.dkr.ecr.us-east-2.amazonaws.com/hello-world:s3",
      "name": "hello-world",
      "cpu": 1,
      "memory": 512,
      "essential": true,
      "command": ["python", "/mnt/deploy.py"]
    }
  ]
DEFINITION
}

# Cluster definition
resource "aws_ecs_cluster" "demo" {
  name = "kp_cluster"
}

# ECS service
resource "aws_ecs_service" "kp_service" {
  name = "kp_service"
  cluster = aws_ecs_cluster.demo.id
  task_definition = aws_ecs_task_definition.krista.arn
  desired_count = 1
  launch_type = "FARGATE"
  network_configuration {
    security_groups = [aws_security_group.aws_ecs_tasks.id]
    subnets = aws_subnet.aws-subnet.*.id
    assign_public_ip = true
  }
}