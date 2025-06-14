from django.db import models


class PcfCalculationMethod(models.TextChoices):
    """
    Enum for lifecycle stages of a product based on IRDI 0173-1#09-AAO115#003
    """
    EN_15804 = "EN 15804", "EN 15804 - Product Category Rules (PCR) for construction products"
    GHG_PROTOCOL = "GHG Protocol", "GHG Protocol - Corporate Standard"
    IEC_TS_63058 = "IEC TS 63058", "IEC TS 63058 - Product Category Rules (PCR) for electrical and electronic products"
    IEC_63366 = "IEC 63366", "IEC 63366 - Product Category Rules (PCR) for electrical and electronic products"
    ISO_14040_ISO_14044 = "ISO 14040/14044", "ISO 14040/14044 - Life Cycle Assessment (LCA) principles, framework, and methodology"
    ISO_14067 = "ISO 14067", "ISO 14067 - Carbon footprint of products"
    PEP_ECOPASSPORT = "PEP Ecopassport", "PEP Ecopassport - Product Environmental Profile (PEP) for electrical and electronic products"
    PACT_V2_0_0 = "PACT v2.0.0", "PACT v2.0.0 - Product Category Rules (PCR) for electrical and electronic products"
    PACT_V1_0_1 = "PACT v1.0.1", "PACT v1.0.1 - Product Category Rules (PCR) for electrical and electronic products"
    PACT_V3_0_0 = "PACT v3.0.0", "PACT v3.0.0 - Product Category Rules (PCR) for electrical and electronic products"
    TFS_V2 = "TFS v2", "TFS v2 - Product Category Rules (PCR) for electrical and electronic products"
    TFS_V3 = "TFS v3", "TFS v3 - Product Category Rules (PCR) for electrical and electronic products"
    CATENA_X_V2 = "Catena-X v2", "Catena-X v2 - Product Category Rules (PCR) for electrical and electronic products"
    CATENA_X_V1 = "Catena-X v1", "Catena-X v1 - Product Category Rules (PCR) for electrical and electronic products"
    CATENA_X_V3 = "Catena-X v3", "Catena-X v3 - Product Category Rules (PCR) for electrical and electronic products"
    BS_PAS_2050 = "BS PAS 2050", "BS PAS 2050 - Specification for the assessment of the life cycle greenhouse gas emissions of goods and services"
    IEC_63372 = "IEC 63372", "IEC 63372 - Product Category Rules (PCR) for electrical and electronic products"

    OTHER = "Other", "Other"

    def get_aas_value(self) -> str:
        """
        Returns the AAS-compatible value of a pcf calculation method.

        Returns:
            AAS-compatible value of the pcf calculation method
        """

        match self:
            case PcfCalculationMethod.EN_15804:
                return "EN 15804"
            case PcfCalculationMethod.GHG_PROTOCOL:
                return "GHG Protocol"
            case PcfCalculationMethod.IEC_TS_63058:
                return "IEC TS 63058"
            case PcfCalculationMethod.IEC_63366:
                return "IEC 63366"
            case PcfCalculationMethod.ISO_14040_ISO_14044:
                return "ISO 14040, ISO 14044"
            case PcfCalculationMethod.ISO_14067:
                return "ISO 14067"
            case PcfCalculationMethod.PEP_ECOPASSPORT:
                return "PEP Ecopassport"
            case PcfCalculationMethod.PACT_V2_0_0:
                return "PACT v2.0.0"
            case PcfCalculationMethod.PACT_V1_0_1:
                return "PACT v1.0.1"
            case PcfCalculationMethod.PACT_V3_0_0:
                return "PACT v3.0.0"
            case PcfCalculationMethod.TFS_V2:
                return "TFS v2"
            case PcfCalculationMethod.TFS_V3:
                return "TFS v3"
            case PcfCalculationMethod.CATENA_X_V2:
                return "Catena-X v2"
            case PcfCalculationMethod.CATENA_X_V1:
                return "Catena-X v1"
            case PcfCalculationMethod.CATENA_X_V3:
                return "Catena-X v3"
            case PcfCalculationMethod.BS_PAS_2050:
                return "BS PAS 2050"
            case PcfCalculationMethod.IEC_63372:
                return "IEC 63372"
            case _:
                return "Other"

    def get_aas_value_id(self) -> str:
        """
        Returns the AAS-compatible value ID of a pcf calculation method.

        Returns:
            AAS-compatible value ID of the pcf calculation method
        """

        match self:
            case PcfCalculationMethod.EN_15804:
                return "0173-1#07-ABU223#003"
            case PcfCalculationMethod.GHG_PROTOCOL:
                return "0173-1#07-ABU221#003"
            case PcfCalculationMethod.IEC_TS_63058:
                return "0173-1#07-ABU222#003"
            case PcfCalculationMethod.IEC_63366:
                return "0173-1#07-ACA792#002"
            case PcfCalculationMethod.ISO_14040_ISO_14044:
                return "0173-1#07-ABV505#003"
            case PcfCalculationMethod.ISO_14067:
                return "0173-1#07-ABU218#003"
            case PcfCalculationMethod.PEP_ECOPASSPORT:
                return "0173-1#07-ABU220#003"
            case PcfCalculationMethod.PACT_V2_0_0:
                return "0173-1#07-ACC003#001"
            case PcfCalculationMethod.PACT_V1_0_1:
                return "0173-1#07-ACC004#001"
            case PcfCalculationMethod.PACT_V3_0_0:
                return "0173-1#07-ACC012#001"
            case PcfCalculationMethod.TFS_V2:
                return "0173-1#07-ACC005#001"
            case PcfCalculationMethod.TFS_V3:
                return "0173-1#07-ACC010#001"
            case PcfCalculationMethod.CATENA_X_V2:
                return "0173-1#07-ACC006#001"
            case PcfCalculationMethod.CATENA_X_V1:
                return "0173-1#07-ACC007#001"
            case PcfCalculationMethod.CATENA_X_V3:
                return "0173-1#07-ACC011#001"
            case PcfCalculationMethod.BS_PAS_2050:
                return "0173-1#07-ACC008#001"
            case PcfCalculationMethod.IEC_63372:
                return "0173-1#07-ACC019#001"
            case _:
                return "Other"

    @staticmethod
    def from_aas_value_id(aas_value_id: str) -> "PcfCalculationMethod":
        """
        Converts an AAS value ID to a PcfCalculationMethod value.

        Returns:
            PCF calculation method corresponding to the AAS value ID, or PcfCalculationMethod.OTHER if not found.
        """
        for stage in PcfCalculationMethod:
            if stage.get_aas_value_id() == aas_value_id:
                return stage
        return PcfCalculationMethod.OTHER