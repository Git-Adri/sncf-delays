variable "aws_region" {
  type        = string
  default     = "eu-west-3"
  description = "Région AWS. Paris par défaut, pour la latence et la résidence des données."
}

variable "bucket_name" {
  type        = string
  description = "Nom du bucket S3 de la couche bronze. Doit être globalement unique."
}

variable "poll_interval_minutes" {
  type        = number
  default     = 5
  description = "Intervalle de collecte. Vérifier le quota API avant de descendre."
}
