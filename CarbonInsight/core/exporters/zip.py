import zipfile
from io import BytesIO
from typing import TYPE_CHECKING

from core.importers.aas_validators import validate_aas_aasx, validate_aas_xml, validate_aas_json

if TYPE_CHECKING:
    from core.models import Product


def product_to_zip(product: 'Product') -> BytesIO:
    # delay import to avoid circular dependency
    from core.resources.emission_resources import (
        TransportEmissionResource,
        ProductionEnergyEmissionResource,
        UserEnergyEmissionResource,
    )
    from core.models import TransportEmission, UserEnergyEmission, ProductionEnergyEmission

    zip_bytes = BytesIO()
    with zipfile.ZipFile(zip_bytes, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        # Add AAS representations
        aas_aasx_file = product.export_to_aas_aasx()
        validate_aas_aasx(aas_aasx_file)
        zf.writestr(f'{product.name}_aas.aasx', aas_aasx_file.getvalue())
        aas_json_file = product.export_to_aas_json()
        validate_aas_json(aas_json_file)
        zf.writestr(f'{product.name}_aas.json', aas_json_file.getvalue())
        aas_xml_file = product.export_to_aas_xml()
        validate_aas_xml(aas_xml_file)
        zf.writestr(f'{product.name}_aas.xml', aas_xml_file.getvalue())

        # Add SCSN representations
        zf.writestr(f'{product.name}_scsn_full.xml', product.export_to_scsn_full_xml().getvalue())
        zf.writestr(f'{product.name}_scsn_pcf.xml', product.export_to_scsn_pcf_xml().getvalue())

        # Add CSV representation of emissions
        transport_emissions = TransportEmissionResource().export(
            queryset=TransportEmission.objects.filter(parent_product=product)).csv.encode("utf-8")
        zf.writestr(f'{product.name}_transport_emissions.csv', transport_emissions)
        user_energy_emissions = UserEnergyEmissionResource().export(
            queryset=UserEnergyEmission.objects.filter(parent_product=product)).csv.encode("utf-8")
        zf.writestr(f'{product.name}_user_energy_emissions.csv', user_energy_emissions)
        production_energy_emissions = ProductionEnergyEmissionResource().export(
            queryset=ProductionEnergyEmission.objects.filter(parent_product=product)).csv.encode("utf-8")
        zf.writestr(f'{product.name}_production_energy_emissions.csv', production_energy_emissions)

    # Rewind the buffer so it’s ready for reading
    zip_bytes.seek(0)
    return zip_bytes