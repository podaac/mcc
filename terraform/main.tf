terraform {
  required_version = ">=1.3.4"

  backend "s3" {
    key = "services/mcc/terraform.tfstate"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 2.9.5"
    }
  }
}

provider "aws" {
  region = var.region

  ignore_tags {
    key_prefixes = ["gsfc-ngap"]
  }
}

locals {
  ec2_resources_name = "svc-${var.app_name}-${var.stage}"

  default_tags = length(var.default_tags) == 0 ? {
    application : local.ec2_resources_name,
    Environment = var.stage
  } : var.default_tags

  certificate_name = "mcc.podaac.${var.stage}.earthdatacloud.nasa.gov"
  full_docker_tag = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.docker_image}:${var.app_version}"

}

data "aws_caller_identity" "current" {}

data "aws_ssm_parameter" "private_ca" {
  name = "ngap_private_ca_arn"
}
