import logging
from decimal import Decimal
from io import BytesIO, TextIOWrapper
from typing import Iterable, Tuple

from basyx.aas.adapter.aasx import DictSupplementaryFileContainer, AASXReader
from basyx.aas.adapter.json import read_aas_json_file_into
from basyx.aas.adapter.xml import read_aas_xml_file_into
from basyx.aas.model import DictObjectStore, Property, MultiLanguageProperty, SubmodelElementCollection, \
    SubmodelElementList
from aas_test_engines.file import *
from rest_framework.exceptions import ValidationError

from core.importers.aas_validators import validate_aas_xml, validate_aas_json, validate_aas_aasx
from core.models import Product, Company, Emission, LifecycleStage, TransportEmission, UserEnergyEmission, \
    ProductionEnergyEmission, EmissionOverrideFactor
from core.models.pcf_calculation_method import PcfCalculationMethod
from core.models.reference_impact_unit import ReferenceImpactUnit

logger = logging.getLogger(__name__)

def aas_to_product(objects: DictObjectStore) -> Product:
    """
    Parses product data from an AAS Digital Nameplate submodel.

    Args:
        objects: The AAS object store containing the submodels.

    Returns:
        A new, unsaved Product instance with data from the nameplate.

    Raises:
        ValidationError: If 'ContactInformation' is missing from the nameplate.
    """
    product = Product()

    digital_nameplate = objects.get_identifiable("https://admin-shell.io/zvei/nameplate/2/0/Nameplate")
    contact_information = None
    for prop in list(digital_nameplate):
        if isinstance(prop, Property):
            match prop.id_short:
                case "URIOfTheProduct":
                    pass
                case "YearOfConstruction":
                    product.year_of_construction = int(prop.value)
        elif isinstance(prop, MultiLanguageProperty):
            match prop.id_short:
                case "ManufacturerName":
                    product.manufacturer_name = next(iter(prop.value.values()))
                case "ManufacturerProductDesignation":
                    product.description = next(iter(prop.value.values()))
                case "ManufacturerProductRoot":
                    product.name = next(iter(prop.value.values()))
                case "ManufacturerProductFamily":
                    product.family = next(iter(prop.value.values()))
                case "ProductArticleNumberOfManufacturer":
                    product.sku = next(iter(prop.value.values()))
        elif isinstance(prop, SubmodelElementCollection):
            match prop.id_short:
                case "ContactInformation":
                    contact_information = prop

    if contact_information is None:
        raise ValidationError("ContactInformation not found in Digital Nameplate.")
    for prop in list(contact_information):
        if isinstance(prop, MultiLanguageProperty):
            match prop.id_short:
                case "NationalCode":
                    product.manufacturer_country = next(iter(prop.value.values()))
                case "CityTown":
                    product.manufacturer_city = next(iter(prop.value.values()))
                case "Street":
                    product.manufacturer_street = next(iter(prop.value.values()))
                case "Zipcode":
                    product.manufacturer_zip_code = next(iter(prop.value.values()))

    return product

def aas_to_emissions(objects: DictObjectStore) -> Tuple[Iterable[Emission], Iterable[EmissionOverrideFactor]]:
    """
    Parses emission data from an AAS Carbon Footprint submodel.

    Args:
        objects: The AAS object store with the Carbon Footprint submodel.

    Returns:
        A tuple with lists of unsaved Emission and EmissionOverrideFactor instances.
    """
    emissions = []
    emission_override_factors = []
    carbon_footprint_sm = objects.get_identifiable("https://admin-shell.io/idta/SubmodelTemplate/CarbonFootprint/1/0")
    for emission_sm in list(list(carbon_footprint_sm)[0]):
        source:str = None
        pcf_calculation_methods:set[PcfCalculationMethod] = set()
        pcf_co_2_eq:Decimal = None
        reference_impact_unit:ReferenceImpactUnit = None
        quantity_of_measure:float = None
        life_cycle_phases:set[LifecycleStage] = set()
        for prop in list(emission_sm):
            if isinstance(prop, Property):
                match prop.id_short:
                    case "PcfSource":
                        source = prop.value
                    case "PcfCO2eq":
                        pcf_co_2_eq = prop.value
                    case "ReferenceImpactUnitForCalculation":
                        reference_impact_unit = prop.value
                    case "QuantityOfMeasureForCalculation":
                        quantity_of_measure = prop.value
            elif isinstance(prop, SubmodelElementList):
                for sub_prop in list(prop):
                    if isinstance(sub_prop, Property):
                        match prop.id_short:
                            case "PcfCalculationMethods":
                                pcf_calculation_methods.add(PcfCalculationMethod.from_aas_value_id(sub_prop.value_id.key[0].value))
                            case "LifeCyclePhases":
                                life_cycle_phases.add(LifecycleStage.from_aas_value_id(sub_prop.value_id.key[0].value))

        emission = None
        source = source.lower()
        if "transport" in source:
            emission = TransportEmission()
            emission.weight = 0
            emission.distance = 0
        elif "user" in source:
            emission = UserEnergyEmission()
            emission.energy_consumption = 0
        elif "production" in source or "energy" in source or "manufacturing" in source:
            emission = ProductionEnergyEmission()
            emission.energy_consumption = 0
        else:
            logger.warning(f"Unknown emission source {source} when importing AAS")
            continue

        if emission is not None:
            emission.pcf_calculation_method = list(pcf_calculation_methods)[0]
            emission.reference_impact_unit = reference_impact_unit
            emission.quantity = quantity_of_measure
            for lifecycle_stage in life_cycle_phases:
                emission_override_factor = EmissionOverrideFactor()
                emission_override_factor.emission = emission
                emission_override_factor.lifecycle_stage = lifecycle_stage
                emission_override_factor.co_2_emission_factor_biogenic = 0
                emission_override_factor.co_2_emission_factor_non_biogenic = pcf_co_2_eq / len(life_cycle_phases)
                emission_override_factors.append(emission_override_factor)
            emissions.append(emission)

    return emissions, emission_override_factors

def aas_objects_to_db(objects: DictObjectStore, supplier:Company) -> Product:
    """
    Converts AAS objects to a Product and its Emissions, then saves to the database.

    Args:
        objects: The AAS object store with product and emission data.
        supplier: The company to associate as the product's supplier.

    Returns:
        The newly created and saved Product instance.
    """
    product = aas_to_product(objects)
    product.supplier = supplier
    product.full_clean()
    product.save()

    emissions, emission_override_factors = aas_to_emissions(objects)
    for emission in emissions:
        emission.parent_product = product
        emission.save()
    for override_factor in emission_override_factors:
        override_factor.save()
    return product

def aas_aasx_to_db(file:BytesIO, supplier:Company) -> Product:
    """
    Reads, validates, and imports an AASX file into the database.

    Args:
        file: The AASX file content as a byte stream.
        supplier: The supplier company for the product.

    Returns:
        The newly created and saved Product instance.
    """
    validate_aas_aasx(file)

    objects = DictObjectStore()
    files = DictSupplementaryFileContainer()
    with AASXReader(file) as reader:
        core_props = reader.get_core_properties()
        ids = reader.read_into(objects, files)

    return aas_objects_to_db(objects, supplier)

def aas_json_to_db(file:BytesIO, supplier:Company) -> Product:
    """
    Reads, validates, and imports an AAS JSON file into the database.

    Args:
        file: The AAS JSON file content as a byte stream.
        supplier: The supplier company for the product.

    Returns:
        The newly created and saved Product instance.
    """
    validate_aas_json(file)

    objects = DictObjectStore()
    read_aas_json_file_into(objects, file)

    return aas_objects_to_db(objects, supplier)

def aas_xml_to_db(file:BytesIO, supplier:Company) -> Product:
    """
    Reads, validates, and imports an AAS XML file into the database.

    Args:
        file: The AAS XML file content as a byte stream.
        supplier: The supplier company for the product.

    Returns:
        The newly created and saved Product instance.
    """
    validate_aas_xml(file)

    objects = DictObjectStore()
    read_aas_xml_file_into(objects, file)

    return aas_objects_to_db(objects, supplier)

