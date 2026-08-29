variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "eks_role_arn" {
  type    = string
  default = "arn:aws:iam::123456789012:role/EKSClusterRole"
}

variable "subnet_ids" {
  type    = list(string)
  default = ["subnet-0a1b2c3d", "subnet-0e1f2a3b"]
}
