resource "random_string" "session_cookie_secret" {
  length  = 16
  special = true
}

resource "aws_ssm_parameter" "session_cookie_secret" {
  name      = "${local.ec2_resources_name}-session-cookie-secret"
  type      = "SecureString"
  value     = random_string.session_cookie_secret.result
  tags      = local.default_tags
}

resource "aws_security_group" "mcc" {
  name        = "${local.ec2_resources_name}-sg"
  description = "Control traffic for the MCC api"
  vpc_id      = var.vpc_id

  ingress = [
    {
      description      = "TLS"
      from_port        = 443
      to_port          = 443
      protocol         = "tcp"
      security_groups  = []
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      self             = true
    }
  ]

  egress = [
    {
      description      = "Outbound traffic"
      prefix_list_ids  = []
      security_groups  = []
      self             = false
      from_port        = 0
      to_port          = 0
      protocol         = "-1"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }
  ]
  tags = local.default_tags
}

resource "aws_ecs_cluster" "fargate_cluster" {
  name = "${local.ec2_resources_name}-fargate-cluster"
  tags = local.default_tags
}

resource "aws_cloudwatch_log_group" "fargate_task_log_group" {
  name              = "${local.ec2_resources_name}-fargate-worker"
  retention_in_days = var.logs_retention_days
  tags              = local.default_tags
}

resource "aws_ecs_task_definition" "fargate_task" {
  family                   = "${local.ec2_resources_name}-fargate-task"
  requires_compatibilities = ["FARGATE"]
  container_definitions = jsonencode([
    {
      name    = "${local.ec2_resources_name}-fargate-task"
      image   = local.full_docker_tag
      essential = true
      environment = [
        {
          name  = "NUM_PROXY_SERVERS_FOR_API"
          value = "1"
        }
      ]
      portMappings = [{
        containerPort = 8080
        protocol      = "tcp"
      }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-region        = var.region
          awslogs-group         = aws_cloudwatch_log_group.fargate_task_log_group.name
          awslogs-stream-prefix = aws_cloudwatch_log_group.fargate_task_log_group.name
        }
      }
    },
    {
      name  = "${local.ec2_resources_name}-proxy"
      image = "ghcr.io/podaac/ngap-dit-proxy"
      essential = true
      environment = [
        {
          name  = "HOSTNAME"
          value = data.aws_acm_certificate.issued.domain
        }, {
          name = "NGAP_CERTIFICATE_ARN"
          value = data.aws_acm_certificate.issued.arn
        }, {
          name = "APP_PORT"
          value = "8080"
        }
      ]
      portMappings = [{
        containerPort = 443
        protocol      = "tcp"
      }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-region        = var.region
          awslogs-group         = aws_cloudwatch_log_group.fargate_task_log_group.name
          awslogs-stream-prefix = aws_cloudwatch_log_group.fargate_task_log_group.name
        }
      }
    }
  ])

  network_mode = "awsvpc"
  cpu          = var.task_cpu
  memory       = var.task_memory

  ephemeral_storage {
    size_in_gib = 100
  }

  execution_role_arn = aws_iam_role.fargate_task_execution_role.arn
  task_role_arn      = aws_iam_role.ecs_task_role.arn
  tags               = local.default_tags
}

resource "aws_ecs_service" "mcc" {
  name            = "${local.ec2_resources_name}-ecs-service"
  cluster         = aws_ecs_cluster.fargate_cluster.arn
  task_definition = aws_ecs_task_definition.fargate_task.arn
  launch_type     = "FARGATE"
  desired_count   = var.fargate_desired_count
  health_check_grace_period_seconds = 30

  network_configuration {
    subnets         = var.private_subnets
    security_groups = [aws_security_group.mcc.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.fargate_service_tg.arn
    container_name   = "${local.ec2_resources_name}-proxy"
    container_port   = 443
  }

  tags = local.default_tags

  depends_on = [
    aws_ecs_cluster.fargate_cluster
  ]
}
