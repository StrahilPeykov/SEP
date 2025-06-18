from django.db import models


class PcfCalculationMethod(models.TextChoices):
    """
    Enum for lifecycle stages of a product based on IRDI 0173-1#09-AAO115#003
    """
    EN_15804 = "EN 15804", "EN 15804 - Sustainability rules for construction products"
    GHG_PROTOCOL = "GHG Protocol", "GHG Protocol - Corporate Standard"
    IEC_TS_63058 = "IEC TS 63058", "IEC TS 63058 -Guidelines for eco-design of low-voltage gear"
    IEC_63366 = "IEC 63366", "IEC 63366 - Guidance for commissioning VSC HVDC systems"
    ISO_14040_ISO_14044 = "ISO 14040/14044", "ISO 14040/14044 - Life cycle assessment principles & methods"
    ISO_14067 = "ISO 14067", "ISO 14067 - Carbon footprint of products"
    PEP_ECOPASSPORT = "PEP Ecopassport", "PEP Ecopassport - Chemical product eco-toxicity report"
    PACT_V2_0_0 = "PACT v2.0.0", "PACT v2.0.0 - V2 for Scope 3 carbon footprint data"
    PACT_V1_0_1 = "PACT v1.0.1", "PACT v1.0.1 - Early version of Scope 3 carbon data standard"
    PACT_V3_0_0 = "PACT v3.0.0", "PACT v3.0.0 - Updated Scope 3 carbon footprint standard"
    TFS_V2 = "TFS v2", "TFS v2 - Chemical industry's product carbon footprint guide"
    TFS_V3 = "TFS v3", "TFS v3 - Chemical industry's product carbon footprint guide"
    CATENA_X_V2 = "Catena-X v2", "Catena-X v2 - Digital twin & data exchange for auto supply"
    CATENA_X_V1 = "Catena-X v1", "Catena-X v1 - Digital twin & data exchange for auto supply"
    CATENA_X_V3 = "Catena-X v3", "Catena-X v3 - Digital twin & data exchange for auto supply"
    BS_PAS_2050 = "BS PAS 2050", "BS PAS 2050 - Specification for the assessment of the life cycle greenhouse gas emissions of goods and services"
    IEC_63372 = "IEC 63372", "IEC 63372 - Guidelines for energy storage system testing"

    OTHER = "Other", "Other"

    def get_aas_value(self) -> str:
        """
        Returns the AAS-compatible value of a pcf calculation method.

        Returns:
            AAS-compatible value of the pcf calculation method
        """
        mapping = {
            PcfCalculationMethod.EN_15804:"EN 15804",
            PcfCalculationMethod.GHG_PROTOCOL:"GHG Protocol",
            PcfCalculationMethod.IEC_TS_63058:"IEC TS 63058",
            PcfCalculationMethod.IEC_63366:"IEC 63366",
            PcfCalculationMethod.ISO_14040_ISO_14044:"ISO 14040, ISO 14044",
            PcfCalculationMethod.ISO_14067:"ISO 14067",
            PcfCalculationMethod.PEP_ECOPASSPORT:"PEP Ecopassport",
            PcfCalculationMethod.PACT_V2_0_0:"PACT v2.0.0",
            PcfCalculationMethod.PACT_V1_0_1:"PACT v1.0.1",
            PcfCalculationMethod.PACT_V3_0_0:"PACT v3.0.0",
            PcfCalculationMethod.TFS_V2:"TFS v2",
            PcfCalculationMethod.TFS_V3:"TFS v3",
            PcfCalculationMethod.CATENA_X_V2:"Catena-X v2",
            PcfCalculationMethod.CATENA_X_V1:"Catena-X v1",
            PcfCalculationMethod.CATENA_X_V3:"Catena-X v3",
            PcfCalculationMethod.BS_PAS_2050:"BS PAS 2050",
            PcfCalculationMethod.IEC_63372:"IEC 63372"
        }
        return mapping.get(self, "Other")

    def get_aas_value_id(self) -> str:
        """
        Returns the AAS-compatible value ID of a pcf calculation method.

        Returns:
            AAS-compatible value ID of the pcf calculation method
        """
        mapping = {
            PcfCalculationMethod.EN_15804: "0173-1#07-ABU223#003",
            PcfCalculationMethod.GHG_PROTOCOL: "0173-1#07-ABU221#003",
            PcfCalculationMethod.IEC_TS_63058: "0173-1#07-ABU222#003",
            PcfCalculationMethod.IEC_63366: "0173-1#07-ACA792#002",
            PcfCalculationMethod.ISO_14040_ISO_14044: "0173-1#07-ABV505#003",
            PcfCalculationMethod.ISO_14067: "0173-1#07-ABU218#003",
            PcfCalculationMethod.PEP_ECOPASSPORT: "0173-1#07-ABU220#003",
            PcfCalculationMethod.PACT_V2_0_0: "0173-1#07-ACC003#001",
            PcfCalculationMethod.PACT_V1_0_1: "0173-1#07-ACC004#001",
            PcfCalculationMethod.PACT_V3_0_0: "0173-1#07-ACC012#001",
            PcfCalculationMethod.TFS_V2: "0173-1#07-ACC005#001",
            PcfCalculationMethod.TFS_V3: "0173-1#07-ACC010#001",
            PcfCalculationMethod.CATENA_X_V2: "0173-1#07-ACC006#001",
            PcfCalculationMethod.CATENA_X_V1: "0173-1#07-ACC007#001",
            PcfCalculationMethod.CATENA_X_V3: "0173-1#07-ACC011#001",
            PcfCalculationMethod.BS_PAS_2050: "0173-1#07-ACC008#001",
            PcfCalculationMethod.IEC_63372: "0173-1#07-ACC019#001",
        }
        return mapping.get(self, "Other")


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