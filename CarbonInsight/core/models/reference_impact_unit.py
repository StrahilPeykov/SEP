from django.db import models

class ReferenceImpactUnit(models.TextChoices):
    """
    Enum for the reference impact unit of a product based on IEC61360-3
    Used to determine the quantity unit of the product to which the
    PCF information on the CO2 footprint refers.
    """
    GRAM = "g", "Gram"
    KILOGRAM = "kg", "Kilogram"
    TON = "t", "Ton"
    MILLILITER = "ml", "Milliliter"
    LITER = "l", "Liter"
    CUBIC_METER = "m3", "Cubic meter"
    SQUARE_METER = "m2", "Square meter"
    PIECE = "pc", "Piece"
    KILOWATT_HOUR = "kWh", "Kilowatt hour"

    OTHER = "Other", "Other"

    def get_aas_value(self) -> str:
        match self:
            case ReferenceImpactUnit.GRAM:
                return "g"
            case ReferenceImpactUnit.KILOGRAM:
                return "kg"
            case ReferenceImpactUnit.TON:
                return "t"
            case ReferenceImpactUnit.MILLILITER:
                return "ml"
            case ReferenceImpactUnit.LITER:
                return "l"
            case ReferenceImpactUnit.CUBIC_METER:
                return "cbm"
            case ReferenceImpactUnit.SQUARE_METER:
                return "qm"
            case ReferenceImpactUnit.PIECE:
                return "piece"
            case ReferenceImpactUnit.KILOWATT_HOUR:
                return "kWh"
            case _:
                return "Other"

    def get_aas_value_id(self) -> str:
        match self:
            case ReferenceImpactUnit.GRAM:
                return "0173-1#07-ABZ596#003"
            case ReferenceImpactUnit.KILOGRAM:
                return "0173-1#07-ABZ597#003"
            case ReferenceImpactUnit.TON:
                return "0173-1#07-ABZ598#003"
            case ReferenceImpactUnit.MILLILITER:
                return "0173-1#07-ABZ599#003"
            case ReferenceImpactUnit.LITER:
                return "0173-1#07-ABZ600#003"
            case ReferenceImpactUnit.CUBIC_METER:
                return "0173-1#07-ABZ601#003"
            case ReferenceImpactUnit.SQUARE_METER:
                return "0173-1#07-ABZ602#003"
            case ReferenceImpactUnit.PIECE:
                return "0173-1#07-ABZ603#003"
            case ReferenceImpactUnit.KILOWATT_HOUR:
                return "0173-1#07-ACB997#001"
            case _:
                return "Other"
