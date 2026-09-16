# Infrastructure de collecte : S3, Lambda, EventBridge.
#
# A ECRIRE. Ressources prévues :
#
#   aws_s3_bucket                    bucket bronze
#   aws_s3_bucket_lifecycle_configuration
#                                    transition vers Glacier après 90 jours
#   aws_iam_role                     rôle d'exécution de la Lambda
#   aws_iam_role_policy              droit PutObject sur le bucket uniquement
#   aws_lambda_function              collecteur
#   aws_scheduler_schedule           déclenchement périodique
#   aws_cloudwatch_log_group         logs avec rétention courte
#
# Terraform est ici autant un outil qu'un exercice : c'est une compétence
# demandée dans les offres visées, et l'infra de ce projet est assez simple
# pour l'apprendre sans se noyer.

terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
