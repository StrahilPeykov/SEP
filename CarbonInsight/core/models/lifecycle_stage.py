from django.db import models

class LifecycleStage(models.TextChoices):
    """
    Enum for lifecycle stages of a product based on ECLASS 15
    """
    A1 = "A1", "A1 - Raw material supply (and upstream production)"
    A2 = "A2", "A2 - Cradle-to-gate transport to factory"
    A3 = "A3", "A3 - Production"
    A4 = "A4", "A4 - Transport to final destination"
    A5 = "A5", "A5 - Installation"
    A1A3 = "A1-A3", "A1-A3 - Raw material supply and production"
    A4A5 = "A4-A5", "A4-A5 - Transport to final destination and installation"

    B1 = "B1", "B1 - Usage phase"
    B2 = "B2", "B2 - Maintenance"
    B3 = "B3", "B3 - Repair"
    B4 = "B4", "B4 - Replacement"
    B5 = "B5", "B5 - Update/upgrade, refurbishing"
    B6 = "B6", "B6 - Operational energy use"
    B7 = "B7", "B7 - Operational water use"
    B1B7 = "B1-B7", "B1-B7 - Entire usage phase"

    C1 = "C1", "C1 - Reassembly"
    C2 = "C2", "C2 - Transport to recycler"
    C3 = "C3", "C3 - Recycling, waste treatment"
    C4 = "C4", "C4 - Landfill"
    C1C4 = "C1-C4", "C1-C4 - Decommissioning"
    C2C4 = "C2-C4", "C2-C4 - Transport to recycler and landfill"

    D = "D", "D - Reuse"

    OTHER = "Other", "Other"