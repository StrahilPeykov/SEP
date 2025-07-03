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

NAMEPLATE_ID = "https://admin-shell.io/zvei/nameplate/2/0/Nameplate"
CARBON_FOOTPRINT_ID = "https://admin-shell.io/idta/SubmodelTemplate/CarbonFootprint/1/0"

# Mapping for product properties
MLPROP_MAP = {
    "ManufacturerName": "manufacturer_name",
    "ManufacturerProductDesignation": "description",
    "ManufacturerProductRoot": "name",
    "ManufacturerProductFamily": "family",
    "ProductArticleNumberOfManufacturer": "sku",
}
CONTACT_MAP = {
    "NationalCode": "manufacturer_country",
    "CityTown": "manufacturer_city",
    "Street": "manufacturer_street",
    "Zipcode": "manufacturer_zip_code",
}
EMISSION_TYPE_MAP = [
    ("transport", TransportEmission, {"weight": 0, "distance": 0}),
    ("user", UserEnergyEmission, {"energy_consumption": 0}),
    ("production", ProductionEnergyEmission, {"energy_consumption": 0}),
    ("energy", ProductionEnergyEmission, {"energy_consumption": 0}),
    ("manufacturing", ProductionEnergyEmission, {"energy_consumption": 0}),
]

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
    nameplate = objects.get_identifiable(NAMEPLATE_ID)
    contact_info = None

    for elem in nameplate:
        if isinstance(elem, Property) and elem.id_short == "YearOfConstruction":
            product.year_of_construction = int(elem.value)
        elif isinstance(elem, MultiLanguageProperty) and elem.id_short in MLPROP_MAP:
            setattr(product, MLPROP_MAP[elem.id_short], next(iter(elem.value.values())))
        elif isinstance(elem, SubmodelElementCollection) and elem.id_short == "ContactInformation":
            contact_info = elem

    if not contact_info:
        raise ValidationError("ContactInformation not found in Digital Nameplate.")

    for elem in contact_info:
        if isinstance(elem, MultiLanguageProperty) and elem.id_short in CONTACT_MAP:
            setattr(product, CONTACT_MAP[elem.id_short], next(iter(elem.value.values())))

    return product

def _get_emission_instance(source: str) -> Optional[Emission]:
    """
    Creates an Emission subclass instance based on source keywords.
    """
    for key, cls, defaults in EMISSION_TYPE_MAP:
        if key in source:
            inst = cls()
            for attr, val in defaults.items():
                setattr(inst, attr, val)
            return inst
    logger.warning(f"Unknown emission source '{source}' when importing AAS")
    return None

def aas_to_emissions(objects: DictObjectStore) -> Tuple[Iterable[Emission], Iterable[EmissionOverrideFactor]]:
    """
    Parses emission data from an AAS Carbon Footprint submodel.

    Args:
        objects: The AAS object store with the Carbon Footprint submodel.

    Returns:
        A tuple with lists of unsaved Emission and EmissionOverrideFactor instances.
    """
    emissions = []
    override_factors = []
    cf_sm = objects.get_identifiable(CARBON_FOOTPRINT_ID)
    entries = list(list(cf_sm)[0])

    for entry in entries:
        data = {}
        for elem in entry:
            if isinstance(elem, Property):
                data[elem.id_short] = elem.value
            elif isinstance(elem, SubmodelElementList):
                values = [sub.value_id.key[0].value for sub in elem if isinstance(sub, Property)]
                data[elem.id_short] = values

        source = data.get("PcfSource", "").lower()
        emission = _get_emission_instance(source)
        if not emission:
            continue

        methods = data.get("PcfCalculationMethods", [])
        if methods:
            emission.pcf_calculation_method = PcfCalculationMethod.from_aas_value_id(methods[0])
        emission.reference_impact_unit = data.get("ReferenceImpactUnitForCalculation")
        emission.quantity = data.get("QuantityOfMeasureForCalculation")

        phases = data.get("LifeCyclePhases", [])
        co2eq = data.get("PcfCO2eq", Decimal(0))
        phase_count = len(phases) or 1

        for phase in phases:
            factor = EmissionOverrideFactor(
                emission=emission,
                lifecycle_stage=LifecycleStage.from_aas_value_id(phase),
                co_2_emission_factor_biogenic=0,
                co_2_emission_factor_non_biogenic=co2eq / phase_count
            )
            override_factors.append(factor)

        emissions.append(emission)

    return emissions, override_factors

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

