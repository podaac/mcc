data "aws_lb" "alb" {
  name = var.load_balancer_name
}

data "aws_security_group" "alb_sg" {
  name = var.load_balancer_sg_name
}

data "aws_acm_certificate" "issued" {
  domain = local.certificate_name
  most_recent = true
}

resource "aws_lb_target_group" "fargate_service_tg" {
  name        = "${local.ec2_resources_name}-tg"
  port        = 443
  protocol    = "HTTPS"
  target_type = "ip"
  vpc_id      = var.vpc_id

  health_check {
    enabled  = true
    matcher  = "200"
    path     = "/about_api"
    port     = 443
    protocol = "HTTPS"
  }

  lifecycle {
    create_before_destroy = true
  }
}
