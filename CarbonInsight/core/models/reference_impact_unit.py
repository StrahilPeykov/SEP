from django.db import models

class ReferenceImpactUnit(models.TextChoices):
    """
    Enum for the reference impact unit of a product based on IEC61360-3
    Used to determine the quantity unit of the product to which the
    PCF information on the CO2 footprint refers.
    """
    GRAM = "g", "Gram"
    KILOGRAM = "kg", "Kilogram"
    TONNE = "t", "Tonne"
    MILLILITER = "ml", "Milliliter"
    LITER = "l", "Liter"
    CUBIC_METER = "m3", "Cubic meter"
    SQUARE_METER = "m2", "Square meter"
    PIECE = "pc", "Piece"
    KILOWATT_HOUR = "kWh", "Kilowatt hour"

    OTHER = "Other", "Other"

    def get_aas_value(self) -> str:
        """
        Returns the AAS-compatible shorthand name of the ReferenceImpactUnit.

        Returns:
            AAS-compatible shorthand name of the ReferenceImpactUnit
        """
        mapping = {
            ReferenceImpactUnit.GRAM:"g",
            ReferenceImpactUnit.KILOGRAM:"kg",
            ReferenceImpactUnit.TONNE: "t",
            ReferenceImpactUnit.MILLILITER:"ml",
            ReferenceImpactUnit.LITER:"l",
            ReferenceImpactUnit.CUBIC_METER:"cbm",
            ReferenceImpactUnit.SQUARE_METER:"qm",
            ReferenceImpactUnit.PIECE:"piece",
            ReferenceImpactUnit.KILOWATT_HOUR:"kWh"
        }
        return mapping.get(self, "Other")

    def get_aas_value_id(self) -> str:
        """
        Returns the AAS-compatible value ID of the ReferenceImpactUnit.

        Returns:
            AAS-compatible value ID of the ReferenceImpactUnit
        """
        mapping = {
            ReferenceImpactUnit.GRAM:"0173-1#07-ABZ596#003",
            ReferenceImpactUnit.KILOGRAM:"0173-1#07-ABZ597#003",
            ReferenceImpactUnit.TONNE: "0173-1#07-ABZ598#003",
            ReferenceImpactUnit.MILLILITER:"0173-1#07-ABZ599#003",
            ReferenceImpactUnit.LITER:"0173-1#07-ABZ600#003",
            ReferenceImpactUnit.CUBIC_METER:"0173-1#07-ABZ601#003",
            ReferenceImpactUnit.SQUARE_METER:"0173-1#07-ABZ602#003",
            ReferenceImpactUnit.PIECE:"0173-1#07-ABZ603#003",
            ReferenceImpactUnit.KILOWATT_HOUR:"0173-1#07-ACB997#001"
        }
        return mapping.get(self, "Other")
