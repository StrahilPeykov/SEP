"""
This module handles the conversion of internal product data into SCSN-compliant
XML formats for sharing carbon footprint information.
"""

from datetime import datetime
from io import BytesIO
from typing import TYPE_CHECKING

import lxml
from django.urls import reverse
from lxml import etree

from CarbonInsight.settings import BASE_URL

if TYPE_CHECKING:
    from core.models import Product

def product_to_scsn_xml_tree(product: 'Product', include_filler_data:bool = True) -> etree.Element:
    """
    Constructs an in-memory XML tree for a given product based on the SCSN UBL standard.

    Args:
        product (Product): The Product instance to serialize.
        include_filler_data (bool): Flag to include placeholder party and document data.
    """
    nsmap = {
        None: "urn:scsn:names:specification:ubl:schema:xsd:Measurement",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsd": "http://www.w3.org/2001/XMLSchema",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    }
    measurement = lxml.etree.Element("Measurement", nsmap = nsmap)

    id = etree.SubElement(measurement, f"{{{nsmap['cbc']}}}ID")
    id.text = str(product.id)

    issue_date = etree.SubElement(measurement, f"{{{nsmap['cbc']}}}IssueDate")
    issue_date.text = datetime.now().date().isoformat()

    if include_filler_data:
        # TODO: We are populating buyer and seller with the same data to craft a semantically correct XML.
        #  This is not correct as the buyer and seller are different parties, but CarbonInsight does not
        #  have this information. Sara Manders said we can use placeholders for this as users will just extract
        #  the PCF data from the XML and not use our own XML in its entirety.
        buyer_customer_party = etree.SubElement(measurement, f"{{{nsmap['cac']}}}BuyerCustomerParty")
        party = etree.SubElement(buyer_customer_party, f"{{{nsmap['cac']}}}Party")
        party_identification = etree.SubElement(party, f"{{{nsmap['cac']}}}PartyIdentification")
        party_identification_id = etree.SubElement(party_identification, f"{{{nsmap['cbc']}}}ID")
        party_identification_id.set("schemeID", "NL:KVK")
        party_identification_id.text = product.supplier.business_registration_number

        party_name = etree.SubElement(party, f"{{{nsmap['cac']}}}PartyName")
        party_name_name = etree.SubElement(party_name, f"{{{nsmap['cbc']}}}Name")
        party_name_name.text = product.supplier.name

        seller_supplier_party = etree.SubElement(measurement, f"{{{nsmap['cac']}}}SellerSupplierParty")
        party = etree.SubElement(seller_supplier_party, f"{{{nsmap['cac']}}}Party")
        party_identification = etree.SubElement(party, f"{{{nsmap['cac']}}}PartyIdentification")
        party_identification_id = etree.SubElement(party_identification, f"{{{nsmap['cbc']}}}ID")
        party_identification_id.set("schemeID", "NL:KVK")
        party_identification_id.text = product.supplier.business_registration_number

        party_name = etree.SubElement(party, f"{{{nsmap['cac']}}}PartyName")
        party_name_name = etree.SubElement(party_name, f"{{{nsmap['cbc']}}}Name")
        party_name_name.text = product.supplier.name

        document = etree.SubElement(measurement, "Document")
        id = etree.SubElement(document, f"{{{nsmap['cbc']}}}ID")
        id.text = str(product.id)

        for line_item in product.line_items.all():
            order_line_reference = etree.SubElement(document, f"{{{nsmap['cac']}}}OrderLineReference")
            line_id = etree.SubElement(order_line_reference, f"{{{nsmap['cbc']}}}LineID")
            line_id.text = str(line_item.id)
            order_reference = etree.SubElement(order_line_reference, f"{{{nsmap['cac']}}}OrderReference")
            id = etree.SubElement(order_reference, f"{{{nsmap['cbc']}}}ID")
            id.text = "PLACEHOLDER"

        attachment = etree.SubElement(document, f"{{{nsmap['cac']}}}Attachment")
        external_reference = etree.SubElement(attachment, f"{{{nsmap['cac']}}}ExternalReference")

        document_type = etree.SubElement(external_reference, f"{{{nsmap['cbc']}}}FormatCode")
        document_type.text = "PCF"

    product_carbon_footprint = etree.SubElement(measurement, f"{{{nsmap['cac']}}}ProductCarbonFootprint")
    updated = etree.SubElement(product_carbon_footprint, f"{{{nsmap['cac']}}}Updated")
    updated.text = datetime.now().isoformat()
    status = etree.SubElement(product_carbon_footprint, f"{{{nsmap['cac']}}}Status")
    status.text = "Active"  # Can be Active or Deprecated
    product_description = etree.SubElement(product_carbon_footprint, f"{{{nsmap['cac']}}}ProductDescription")
    product_description.text = product.description

    for product_id in [product.id, product.sku]:
        product_id_element = etree.SubElement(product_carbon_footprint, f"{{{nsmap['cac']}}}ProductIds")
        product_id_element.text = str(product_id)

    # TODO: Product category CPC (Central Product Classification)?

    emission_trace = product.get_emission_trace()

    comment = etree.SubElement(product_carbon_footprint, f"{{{nsmap['cac']}}}Comment")
    comment.text = emission_trace.label
    if emission_trace.methodology is not None:
        comment.text += " - " + emission_trace.methodology

    carbon_footprint = etree.SubElement(product_carbon_footprint, f"{{{nsmap['cac']}}}CarbonFootprint")

    declared_unit = etree.SubElement(carbon_footprint, f"{{{nsmap['cac']}}}DeclaredUnit")
    declared_unit.text = emission_trace.reference_impact_unit.get_aas_value()

    unitary_product_amount = etree.SubElement(carbon_footprint, f"{{{nsmap['cac']}}}UnitaryProductAmount")
    unitary_product_amount.text = str(1)

    pcf_excluding_biogenic = etree.SubElement(carbon_footprint, f"{{{nsmap['cac']}}}PCFexcludingBiogenic")
    pcf_excluding_biogenic.text = str(emission_trace.total_non_biogenic)

    product_carbon_footprint_calculation = etree.SubElement(product_carbon_footprint, f"{{{nsmap['cac']}}}ProductCarbonFootprintCalculation")

    pcf_calculation_method = etree.SubElement(product_carbon_footprint_calculation, f"{{{nsmap['cac']}}}PCFCalculationMethod")
    pcf_calculation_method.text = emission_trace.pcf_calculation_method.get_aas_value()

    for life_cycle_stage in emission_trace.emissions_subtotal:
        # TODO: The SCSN standard allows for just a singular lifecycle stage.
        #  This is wrong as a process or subproduct can have more than one lifecycle stage.
        pcf_life_cycle_phase = etree.SubElement(product_carbon_footprint_calculation, f"{{{nsmap['cac']}}}PCFLifeCyclePhase")
        pcf_life_cycle_phase.text = life_cycle_stage.get_aas_value()

    bill_of_materials = etree.SubElement(product_carbon_footprint_calculation, f"{{{nsmap['cac']}}}BillOfMaterials")
    for emission_trace_child in emission_trace.children:
        etc, qty = emission_trace_child.emission_trace, emission_trace_child.quantity

        from core.models import Product  # Done here to avoid circular import
        if isinstance(etc.related_object, Product):
            bom_reference = etree.SubElement(bill_of_materials, f"{{{nsmap['cac']}}}BOMReference")
            id = etree.SubElement(bom_reference, f"{{{nsmap['cbc']}}}ID")
            id.text = str(etc.related_object.id)
            version = etree.SubElement(bom_reference, f"{{{nsmap['cbc']}}}VersionID")
            version.text = "v1.0"
            external_reference = etree.SubElement(bom_reference, f"{{{nsmap['cac']}}}ExternalReference")
            uri = etree.SubElement(external_reference, f"{{{nsmap['cbc']}}}URI")
            uri.text = "PLACEHOLDER"  # TODO: Remove placeholder
            file_name = etree.SubElement(external_reference, f"{{{nsmap['cbc']}}}FileName")
            file_name.text = "PLACEHOLDER"  # TODO: Remove placeholder
            description = etree.SubElement(external_reference, f"{{{nsmap['cbc']}}}Description")
            description.text = etc.label
            pcf_excluding_biogenic = etree.SubElement(bom_reference, f"{{{nsmap['cac']}}}PCFexcludingBiogenic")
            pcf_excluding_biogenic.text = str(etc.total_non_biogenic)
        else:
            pcf_process = etree.SubElement(product_carbon_footprint_calculation, f"{{{nsmap['cac']}}}PCFProcess")
            boundary_process_description = etree.SubElement(pcf_process, f"{{{nsmap['cac']}}}BoundaryProcessDescription")
            boundary_process_description.text = etc.label
            if etc.methodology is not None:
                boundary_process_description.text += " - " + etc.methodology
            pcf_excluding_biogenic = etree.SubElement(pcf_process, f"{{{nsmap['cac']}}}PCFexcludingBiogenic")
            pcf_excluding_biogenic.text = str(etc.total_non_biogenic)
            pcf_calculation_method = etree.SubElement(pcf_process, f"{{{nsmap['cac']}}}PCFCalculationMethod")
            pcf_calculation_method.text = etc.pcf_calculation_method.get_aas_value()
            explanatory_statement = etree.SubElement(pcf_process, f"{{{nsmap['cac']}}}ExplanatoryStatement")
            explanatory_statement.text = etc.methodology
            # TODO: Make allocation rules description stick to the code lists from SCSN?
            allocation_rules_description = etree.SubElement(pcf_process, f"{{{nsmap['cac']}}}AllocationRulesDescription")
            allocation_rules_description.text = f"Allocation based on {etc.reference_impact_unit.value}"

    return measurement

def product_to_scsn_pcf_xml(product: 'Product') -> BytesIO:
    """
    Generates a minimal XML file containing only the core Product Carbon Footprint (PCF) data.

    Args:
        product (Product): The Product instance for which to generate the PCF XML.
    """
    tree = product_to_scsn_xml_tree(product, include_filler_data=False)

    bytes_io = BytesIO()
    bytes_io.write(etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding="UTF-8"))
    bytes_io.seek(0)
    return bytes_io

def product_to_scsn_full_xml(product: 'Product') -> BytesIO:
    """
    Generates the complete SCSN XML file for a product, including placeholder party and document data.

    Args:
        product (Product): The Product instance for which to generate the full XML.
    """
    tree = product_to_scsn_xml_tree(product, include_filler_data=True)

    bytes_io = BytesIO()
    bytes_io.write(etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding="UTF-8"))
    bytes_io.seek(0)
    return bytes_io