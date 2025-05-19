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

    def get_aas_value(self) -> str:
        match self:
            case LifecycleStage.A1:
                return "A1 - raw material supply (and upstream production)"
            case LifecycleStage.A2:
                return "A2 - cradle-to-gate transport to factory"
            case LifecycleStage.A3:
                return "A3 - production"
            case LifecycleStage.A4:
                return "A4 - transport to final destination"
            case LifecycleStage.A5:
                return "A5 - installation"
            case LifecycleStage.A1A3:
                return "A1-A3"
            case LifecycleStage.A4A5:
                return "A4-A5"
            case LifecycleStage.B1:
                return "B1 - usage phase"
            case LifecycleStage.B2:
                return "B2 - maintenance"
            case LifecycleStage.B3:
                return "B3 - repair"
            case LifecycleStage.B4:
                return "B4 - replacement"
            case LifecycleStage.B5:
                return "B5 - update/upgrade, refurbishing"
            case LifecycleStage.B6:
                return "B6 - operational energy use"
            case LifecycleStage.B7:
                return "B7 - operational water use"
            case LifecycleStage.B1B7:
                return "B1-B7"
            case LifecycleStage.C1:
                return "C1 - reassembly"
            case LifecycleStage.C2:
                return "C2 - transport to recycler"
            case LifecycleStage.C3:
                return "C3 - recycling, waste treatment"
            case LifecycleStage.C4:
                return "C4 - landfill"
            case LifecycleStage.C1C4:
                return "C1-C4"
            case LifecycleStage.C2C4:
                return "C2-C4"
            case LifecycleStage.D:
                return "D - reuse"
            case _:
                return "Other"

    def get_aas_value_id(self) -> str:
        match self:
            case LifecycleStage.A1:
                return "0173-1#07-ABU208#003"
            case LifecycleStage.A2:
                return "0173-1#07-ABU209#003"
            case LifecycleStage.A3:
                return "0173-1#07-ABU210#003"
            case LifecycleStage.A4:
                return "0173-1#07-ABU211#003"
            case LifecycleStage.A5:
                return "0173-1#07-ACC016#001"
            case LifecycleStage.A1A3:
                return "0173-1#07-ABZ789#003"
            case LifecycleStage.A4A5:
                return "0173-1#07-ACC013#001"
            case LifecycleStage.B1:
                return "0173-1#07-ABU212#003"
            case LifecycleStage.B2:
                return "0173-1#07-ABV498#003"
            case LifecycleStage.B3:
                return "0173-1#07-ABV497#003"
            case LifecycleStage.B4:
                return "0173-1#07-ACC017#001"
            case LifecycleStage.B5:
                return "0173-1#07-ABV499#003"
            case LifecycleStage.B6:
                return "0173-1#07-ABV500#003"
            case LifecycleStage.B7:
                return "0173-1#07-ABV501#003"
            case LifecycleStage.B1B7:
                return "0173-1#07-ACC014#001"
            case LifecycleStage.C1:
                return "0173-1#07-ABV502#003"
            case LifecycleStage.C2:
                return "0173-1#07-ABU213#003"
            case LifecycleStage.C3:
                return "0173-1#07-ABV503#003"
            case LifecycleStage.C4:
                return "0173-1#07-ABV504#003"
            case LifecycleStage.C1C4:
                return "0173-1#07-ACC015#001"
            case LifecycleStage.C2C4:
                return "0173-1#07-ACC018#001"
            case LifecycleStage.D:
                return "0173-1#07-ABU214#003"
            case _:
                return "Other"
