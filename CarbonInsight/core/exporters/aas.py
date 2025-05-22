from datetime import datetime, timezone, timedelta
from decimal import Decimal
from io import BytesIO
from typing import TYPE_CHECKING, Tuple, Iterable

from basyx.aas import model
from basyx.aas.adapter.aasx import AASXWriter, DictSupplementaryFileContainer
from basyx.aas.adapter.xml import write_aas_xml_file
from basyx.aas.adapter.json import write_aas_json_file
from basyx.aas.model import DictObjectStore, SubmodelElementCollection, SubmodelElementList, Property, \
    File, MultiLanguageProperty, MultiLanguageTextType, ConceptDescription, MultiLanguageNameType
from django.urls import reverse

from CarbonInsight.settings import BASE_URL

if TYPE_CHECKING:
    from core.models import Product

def product_to_aas(product: 'Product') -> Tuple[str | Iterable[str], DictObjectStore, DictSupplementaryFileContainer]:
    aas_identifier = f"{BASE_URL}/AAS"
    pcf_submodel_identifier = "https://admin-shell.io/idta/SubmodelTemplate/CarbonFootprint/1/0"
    dn_submodel_identifier = "https://admin-shell.io/zvei/nameplate/2/0/Nameplate"

    asset_info = model.AssetInformation(
        asset_kind=model.AssetKind.INSTANCE,
        global_asset_id=BASE_URL + reverse("product-detail", args=[product.supplier.id, product.id]),
    )

    aas = model.AssetAdministrationShell(asset_information=asset_info, id_=model.Identifier(aas_identifier))

    """
    DIGITAL NAMEPLATE SUBMODEL
    """

    dn_submodel = model.Submodel(
        id_short="DigitalNameplate",
        id_=model.Identifier(dn_submodel_identifier),
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="https://admin-shell.io/zvei/nameplate/2/0/Nameplate"
            ),)
        ),
    )
    dn_submodel_reference = model.ModelReference.from_referable(dn_submodel)
    aas.submodel.add(dn_submodel_reference)

    uri_of_the_product = Property(
        id_short="URIOfTheProduct",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAY811#001"
            ),)
        ),
        value_type=model.datatypes.String,
        value=BASE_URL + reverse("product-detail", args=[product.supplier.id, product.id])
    )
    dn_submodel.submodel_element.add(uri_of_the_product)

    manufacturer_name = MultiLanguageProperty(
        id_short="ManufacturerName",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAO677#002"
            ),)
        ),
        value=MultiLanguageTextType({"en": product.manufacturer_name}),
    )
    dn_submodel.submodel_element.add(manufacturer_name)

    manufacturer_product_designation = MultiLanguageProperty(
        id_short="ManufacturerProductDesignation",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAW338#001"
            ),)
        ),
        value=MultiLanguageTextType({"en": product.description}),
    )
    dn_submodel.submodel_element.add(manufacturer_product_designation)

    contact_information = SubmodelElementCollection(
        id_short="ContactInformation",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="https://admin-shell.io/zvei/nameplate/1/0/ContactInformations/ContactInformation"
            ),)
        ),
    )
    dn_submodel.submodel_element.add(contact_information)

    national_code = MultiLanguageProperty(
        id_short="NationalCode",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAO678#002"
            ),)
        ),
        value=MultiLanguageTextType({product.manufacturer_country.code.lower(): product.manufacturer_country.code}),
    )
    contact_information.value.add(national_code)

    city_town = MultiLanguageProperty(
        id_short="CityTown",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAO132#002"
            ),)
        ),
        value=MultiLanguageTextType({product.manufacturer_country.code.lower(): product.manufacturer_city}),
    )
    contact_information.value.add(city_town)

    street = MultiLanguageProperty(
        id_short="Street",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAO128#002"
            ),)
        ),
        value=MultiLanguageTextType({product.manufacturer_country.code.lower(): product.manufacturer_street}),
    )
    contact_information.value.add(street)

    zipcode = MultiLanguageProperty(
        id_short="Zipcode",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAO129#002"
            ),)
        ),
        value=MultiLanguageTextType({product.manufacturer_country.code.lower(): product.manufacturer_zip_code}),
    )
    contact_information.value.add(zipcode)

    manufacturer_product_root = MultiLanguageProperty(
        id_short="ManufacturerProductRoot",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAU732#001"
            ),)
        ),
        value=MultiLanguageTextType({"en": product.name}),
    )
    dn_submodel.submodel_element.add(manufacturer_product_root)


    manufacturer_product_family = MultiLanguageProperty(
        id_short="ManufacturerProductFamily",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAU731#001"
            ),)
        ),
        value=MultiLanguageTextType({"en": product.family}),
    )
    dn_submodel.submodel_element.add(manufacturer_product_family)

    """
    manufacturer_product_type = MultiLanguageProperty(
        id_short="ManufacturerProductType",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAO057#002"
            ),)
        ),
        value=MultiLanguageTextType({"en": "PLACEHOLDER"}),
    )
    dn_submodel.submodel_element.add(manufacturer_product_type)

    order_code_of_manufacturer = MultiLanguageProperty(
        id_short="OrderCodeOfManufacturer",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAO227#002"
            ),)
        ),
        value=MultiLanguageTextType({"en": "PLACEHOLDER"}),
    )
    dn_submodel.submodel_element.add(order_code_of_manufacturer)
    """

    product_article_number_of_manufacturer = MultiLanguageProperty(
        id_short="ProductArticleNumberOfManufacturer",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAO676#003"
            ),)
        ),
        value=MultiLanguageTextType({"en": product.sku}),
    )
    dn_submodel.submodel_element.add(product_article_number_of_manufacturer)

    """
    serial_number = Property(
        id_short="SerialNumber",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAM556#002"
            ),)
        ),
        value_type=model.datatypes.String,
        value="PLACEHOLDER",  # TODO: Implement properly
    )
    dn_submodel.submodel_element.add(serial_number)
    """

    year_of_construction = Property(
        id_short="YearOfConstruction",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAP906#001"
            ),)
        ),
        value_type=model.datatypes.String,
        value="2099",
    )
    dn_submodel.submodel_element.add(year_of_construction)

    """
    date_of_manufacture = Property(
        id_short="DateOfManufacture",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAR972#002"
            ),)
        ),
        value_type=model.datatypes.Date,
        value=datetime.now()
    )
    dn_submodel.submodel_element.add(date_of_manufacture)

    hardware_version = MultiLanguageProperty(
        id_short="HardwareVersion",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAN270#002"
            ),)
        ),
        value=MultiLanguageTextType({"en": "PLACEHOLDER"}),
    )
    dn_submodel.submodel_element.add(hardware_version)

    firmware_version = MultiLanguageProperty(
        id_short="FirmwareVersion",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAM985#002"
            ),)
        ),
        value=MultiLanguageTextType({"en": "PLACEHOLDER"}),
    )
    dn_submodel.submodel_element.add(firmware_version)

    software_version = MultiLanguageProperty(
        id_short="SoftwareVersion",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAM737#002"
            ),)
        ),
        value=MultiLanguageTextType({"en": "PLACEHOLDER"}),
    )
    dn_submodel.submodel_element.add(software_version)
    
    country_of_origin = Property(
        id_short="CountryOfOrigin",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-AAO259#004"
            ),)
        ),
        value_type=model.datatypes.String,
        value="PLACEHOLDER",
    )
    dn_submodel.submodel_element.add(country_of_origin)
    """

    # TODO: CompanyLogo
    # TODO: Markings
    # TODO: AssetSpecificProperties

    """
    PCF SUBMODEL
    """

    pcf_submodel = model.Submodel(
        id_short="CarbonFootprint",
        id_=model.Identifier(pcf_submodel_identifier),
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="https://admin-shell.io/idta/SubmodelTemplate/CarbonFootprint/1/0"
            ),)
        ),
    )
    pcf_submodel_reference = model.ModelReference.from_referable(pcf_submodel)
    aas.submodel.add(pcf_submodel_reference)

    pcf_list = SubmodelElementList(
        id_short="ProductCarbonFootprints",
        semantic_id=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="https://admin-shell.io/idta/CarbonFootprint/ProductCarbonFootprints/1/0"
            ),)
        ),
        order_relevant=False,
        type_value_list_element=SubmodelElementCollection,
        semantic_id_list_element=model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value="https://admin-shell.io/idta/CarbonFootprint/ProductCarbonFootprint/1/0"
            ),)
        )
    )

    pcf_submodel.submodel_element.add(pcf_list)

    # START OF LOOP
    for emission_trace_child in product.get_emission_trace().children:
        emission_quantity = emission_trace_child.quantity
        emission_trace = emission_trace_child.emission_trace
        pcf_step_collection = SubmodelElementCollection(
            id_short=None,
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value="https://admin-shell.io/idta/CarbonFootprint/ProductCarbonFootprint/1/0"
                ),)
            ),
            display_name=MultiLanguageNameType(
                {"en": f"{emission_trace.label} - {emission_trace.methodology}"}
            )
        )
        pcf_list.value.add(pcf_step_collection)

        pcf_label = Property(
            id_short="PcfLabel",
            value_type=model.datatypes.String,
            value = emission_trace.label,
        )
        pcf_step_collection.value.add(pcf_label)

        if emission_trace.methodology:
            pcf_methodology = Property(
                id_short="PcfMethodology",
                value_type=model.datatypes.String,
                value = emission_trace.methodology,
            )
            pcf_step_collection.value.add(pcf_methodology)

        pcf_source = Property(
            id_short="PcfSource",
            value_type=model.datatypes.String,
            value = emission_trace.source,
        )
        pcf_step_collection.value.add(pcf_source)

        pcf_calculation_methods = SubmodelElementList(
            id_short="PcfCalculationMethods",
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value="https://admin-shell.io/idta/CarbonFootprint/PcfCalculationMethods/1/0"
                ),)
            ),
            order_relevant=False,
            type_value_list_element=Property,
            value_type_list_element=model.datatypes.String,
            semantic_id_list_element=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value="0173-1#02-ABG854#003"
                ),)
            ),
        )

        pcf_step_collection.value.add(pcf_calculation_methods)


        pcf_calculation_method = Property(
            id_short=None,
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value="0173-1#02-ABG854#003"
                ),)
            ),
            value_type=model.datatypes.String
        )
        pcf_calculation_method.value = emission_trace.pcf_calculation_method.get_aas_value()
        pcf_calculation_method.value_id = model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value=emission_trace.pcf_calculation_method.get_aas_value_id(),
            ),)
        )
        pcf_calculation_methods.value.add(pcf_calculation_method)

        pcf_co_2_eq = Property(
            id_short="PcfCO2eq",
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value="0173-1#02-ABG855#003"
                ),)
            ),
            value_type=model.datatypes.Decimal
        )

        pcf_step_collection.value.add(pcf_co_2_eq)
        pcf_co_2_eq.value = Decimal(emission_quantity * emission_trace.total)

        reference_impact_unit_for_calculation = Property(
            id_short="ReferenceImpactUnitForCalculation",
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value="0173-1#02-ABG856#003"
                ),)
            ),
            value_type=model.datatypes.String
        )
        pcf_step_collection.value.add(reference_impact_unit_for_calculation)

        # Allowed values: g/kg/t/ml/l/cbm/qm/piece/kWh
        reference_impact_unit_for_calculation.value = emission_trace.reference_impact_unit.get_aas_value()
        reference_impact_unit_for_calculation.value_id = model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.GLOBAL_REFERENCE,
                value=emission_trace.reference_impact_unit.get_aas_value_id(),
            ),)
        )

        quantity_of_measure_for_calculation = Property(
            id_short="QuantityOfMeasureForCalculation",
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value="0173-1#02-ABG857#003"
                ),)
            ),
            value_type=model.datatypes.Double
        )
        pcf_step_collection.value.add(quantity_of_measure_for_calculation)
        quantity_of_measure_for_calculation.value = emission_quantity

        life_cycle_phases = SubmodelElementList(
            id_short="LifeCyclePhases",
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value="https://admin-shell.io/idta/CarbonFootprint/LifeCyclePhases/1/0"
                ),)
            ),
            order_relevant=False,
            type_value_list_element=Property,
            value_type_list_element=model.datatypes.String,
            semantic_id_list_element=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value="0173-1#02-ABG858#003"
                ),)
            )
        )
        pcf_step_collection.value.add(life_cycle_phases)

        for emission_trace_lc_phase in emission_trace.emissions_subtotal:
            life_cycle_phase = Property(
                id_short=None,
                semantic_id=model.ExternalReference(
                    (model.Key(
                        type_=model.KeyTypes.GLOBAL_REFERENCE,
                        value="0173-1#02-ABG858#003"
                    ),)
                ),
                value_type=model.datatypes.String
            )
            life_cycle_phases.value.add(life_cycle_phase)
            #life_cycle_phase.id_short = f"LifecyclePhase_{str(emission_trace_lc_phase.value).replace('-','')}_{hash(emission_trace)}"
            life_cycle_phase.value = emission_trace_lc_phase.get_aas_value()
            life_cycle_phase.value_id = model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value=emission_trace_lc_phase.get_aas_value_id()
                ),)
            )

        """
        explanatory_statement = File(
            id_short="ExplanatoryStatement",
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value="https://admin-shell.io/idta/CarbonFootprint/ExplanatoryStatement/1/0"
                ),)
            ),
            content_type="application/pdf"
        )
        pcf_step_collection.value.add(explanatory_statement)
        #explanatory_statement.value = f"{BASE_URL}/ExplanatoryStatement.pdf"
        """

        """
        goods_handover_address = SubmodelElementCollection(
            id_short="GoodsHandoverAddress",
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value="https://admin-shell.io/zvei/nameplate/1/0/ContactInformations/AddressInformation"
                ),)
            ),
            supplemental_semantic_id=[
                model.ExternalReference(
                    (model.Key(
                        type_=model.KeyTypes.GLOBAL_REFERENCE,
                        value="https://admin-shell.io/smt-dropin/smt-dropin-use/1/0"
                    ),)
                ),
                model.ExternalReference(
                    (model.Key(
                        type_=model.KeyTypes.GLOBAL_REFERENCE,
                        value="0112/2///61360_7#AAS002#001"
                    ),)
                ),
                model.ExternalReference(
                    (model.Key(
                        type_=model.KeyTypes.GLOBAL_REFERENCE,
                        value="0173-1#02-AAQ837#008"
                    ),)
                )
            ]
        )
        pcf_step_collection.value.add(goods_handover_address)
        """

        publication_date = Property(
            id_short="PublicationDate",
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value="https://admin-shell.io/idta/CarbonFootprint/PublicationDate/1/0"
                ),)
            ),
            value_type=model.datatypes.DateTime
        )
        pcf_step_collection.value.add(publication_date)
        publication_date.value = datetime.now()

        """
        expiration_date = Property(
            id_short="ExpirationDate",
            semantic_id=model.ExternalReference(
                (model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value="https://admin-shell.io/idta/CarbonFootprint/ExpirationDate/1/0"
                ),)
            ),
            value_type=model.datatypes.DateTime
        )
        pcf_step_collection.value.add(expiration_date)
        expiration_date.value = datetime.now() + timedelta(days=365)
        """

    """
    PACKAGING
    """

    aas_ids = [aas_identifier]
    object_store = DictObjectStore([aas, pcf_submodel, dn_submodel])
    file_store = DictSupplementaryFileContainer()  # empty, since no File objects

    return aas_ids, object_store, file_store


def product_to_aas_aasx(product: 'Product') -> BytesIO:
    aas_ids, object_store, file_store = product_to_aas(product)

    bytes_io = BytesIO()
    with AASXWriter(bytes_io) as writer:
        writer.write_aas(
            aas_ids=aas_ids,
            object_store=object_store,
            file_store=file_store
        )

    # rewind the buffer so the caller can read from the start
    bytes_io.seek(0)
    return bytes_io

def product_to_aas_xml(product: 'Product') -> BytesIO:
    aas_ids, object_store, file_store = product_to_aas(product)

    bytes_io = BytesIO()
    write_aas_xml_file(bytes_io, object_store)

    # rewind the buffer so the caller can read from the start
    bytes_io.seek(0)
    return bytes_io

def product_to_aas_json(product: 'Product') -> BytesIO:
    aas_ids, object_store, file_store = product_to_aas(product)

    bytes_io = BytesIO()
    write_aas_json_file(bytes_io, object_store)

    # rewind the buffer so the caller can read from the start
    bytes_io.seek(0)
    return bytes_io
