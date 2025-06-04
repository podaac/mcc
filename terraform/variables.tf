variable "app_name" {
  default = "mcc"
}

variable "stage" {}

variable "app_version" {}

variable "vpc_id" {}

variable "private_subnets" {
  type = list(string)
}

variable "default_tags" {
  type    = map(string)
  default = {}
}

variable "docker_image" {
  default = "podaac/mcc"
}

variable "task_cpu" {
  type        = number
  description = "(Optional) CPU value for the Fargate task"
  default     = 4096
}

variable "task_memory" {
  type        = number
  description = "(Optional) Memory value for the Fargate task"
  default     = 8192
}

variable "logs_retention_days" {
  type        = number
  description = "(Optional) Retention days for logs of the Fargate task log group "
  default     = 30
}

variable "fargate_desired_count" {
  type        = number
  description = "(Optional) Desired instance count of the Fargate service"
  default     = 5
}

variable "region" {
  default = "us-west-2"
}

variable "load_balancer_name" {}

variable "load_balancer_sg_name" {}
