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
        """
        Returns the str name of a lifecycle stage

        Returns:
            name of the lifecycle stage
        """
        mapping = {
            LifecycleStage.A1:"A1 - raw material supply (and upstream production)",
            LifecycleStage.A2:"A2 - cradle-to-gate transport to factory",
            LifecycleStage.A3:"A3 - production",
            LifecycleStage.A4:"A4 - transport to final destination",
            LifecycleStage.A5:"A5 - installation",
            LifecycleStage.A1A3:"A1-A3",
            LifecycleStage.A4A5:"A4-A5",
            LifecycleStage.B1:"B1 - usage phase",
            LifecycleStage.B2:"B2 - maintenance",
            LifecycleStage.B3:"B3 - repair",
            LifecycleStage.B4:"B4 - replacement",
            LifecycleStage.B5:"B5 - update/upgrade, refurbishing",
            LifecycleStage.B6:"B6 - operational energy use",
            LifecycleStage.B7:"B7 - operational water use",
            LifecycleStage.B1B7:"B1-B7",
            LifecycleStage.C1:"C1 - reassembly",
            LifecycleStage.C2:"C2 - transport to recycler",
            LifecycleStage.C3:"C3 - recycling, waste treatment",
            LifecycleStage.C4:"C4 - landfill",
            LifecycleStage.C1C4:"C1-C4",
            LifecycleStage.C2C4:"C2-C4",
            LifecycleStage.D:"D - reuse"
        }
        return mapping.get(self, "Other")

    def get_aas_value_id(self) -> str:
        """
        Returns the value ID of a lifecycle stage

        Returns:
            value ID of the lifecycle stage
        """
        mapping = {
            LifecycleStage.A1:"0173-1#07-ABU208#003",
            LifecycleStage.A2:"0173-1#07-ABU209#003",
            LifecycleStage.A3:"0173-1#07-ABU210#003",
            LifecycleStage.A4:"0173-1#07-ABU211#003",
            LifecycleStage.A5:"0173-1#07-ACC016#001",
            LifecycleStage.A1A3:"0173-1#07-ABZ789#003",
            LifecycleStage.A4A5:"0173-1#07-ACC013#001",
            LifecycleStage.B1:"0173-1#07-ABU212#003",
            LifecycleStage.B2:"0173-1#07-ABV498#003",
            LifecycleStage.B3:"0173-1#07-ABV497#003",
            LifecycleStage.B4:"0173-1#07-ACC017#001",
            LifecycleStage.B5:"0173-1#07-ABV499#003",
            LifecycleStage.B6:"0173-1#07-ABV500#003",
            LifecycleStage.B7:"0173-1#07-ABV501#003",
            LifecycleStage.B1B7:"0173-1#07-ACC014#001",
            LifecycleStage.C1:"0173-1#07-ABV502#003",
            LifecycleStage.C2:"0173-1#07-ABU213#003",
            LifecycleStage.C3:"0173-1#07-ABV503#003",
            LifecycleStage.C4:"0173-1#07-ABV504#003",
            LifecycleStage.C1C4:"0173-1#07-ACC015#001",
            LifecycleStage.C2C4:"0173-1#07-ACC018#001",
            LifecycleStage.D:"0173-1#07-ABU214#003"
        }
        return mapping.get(self, "Other")

    @staticmethod
    def from_aas_value_id(aas_value_id: str) -> "LifecycleStage":
        """
        Converts an AAS value ID to a LifecycleStage value.

        Returns:
            value ID of the lifecycle stage
        """
        for stage in LifecycleStage:
            if stage.get_aas_value_id() == aas_value_id:
                return stage
        return LifecycleStage.OTHER