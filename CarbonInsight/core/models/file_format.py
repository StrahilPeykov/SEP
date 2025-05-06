from django.db import models

class FileFormat(models.TextChoices):
    AASX = "AASX", "AASX"
    XML = "XML", "XML"
    JSON = "JSON", "JSON"
    CSV = "CSV", "CSV"
    XLSX = "XLSX", "XLSX"
    PDF = "PDF", "PDF"
