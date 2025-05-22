import logging
from typing import Optional, TYPE_CHECKING

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django_countries.fields import CountryField

from .emission_trace import EmissionTrace, EmissionTraceMentionClass, EmissionTraceMention, EmissionTraceChild
from .lifecycle_stage import LifecycleStage
from .pcf_calculation_method import PcfCalculationMethod
from .product_sharing_request import ProductSharingRequest, ProductSharingRequestStatus
from .reference_impact_unit import ReferenceImpactUnit
from ..exporters.aas import product_to_aas_aasx, product_to_aas_json, product_to_aas_xml
from ..exporters.scsn import product_to_scsn_full_xml, product_to_scsn_pcf_xml

if TYPE_CHECKING:
    from .company import Company
    from .user import User

logger = logging.getLogger(__name__)

class Product(models.Model):
    name = models.CharField(max_length=255)
    supplier = models.ForeignKey(
        "Company",
        on_delete=models.CASCADE,
        related_name="products",
    )
    description = models.TextField()
    manufacturer_name = models.CharField(max_length=255)
    manufacturer_country = CountryField()
    manufacturer_city = models.CharField(max_length=255)
    manufacturer_street = models.CharField(max_length=255)
    manufacturer_zip_code = models.CharField(max_length=255)
    year_of_construction = models.IntegerField(
        validators=[MinValueValidator(1900)],
    )
    family = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    reference_impact_unit = models.CharField(
        max_length=255,
        choices=ReferenceImpactUnit.choices,
        default=ReferenceImpactUnit.PIECE,
    )
    pcf_calculation_method = models.CharField(
        max_length=255,
        choices=PcfCalculationMethod.choices,
        default=PcfCalculationMethod.ISO_14040_ISO_14044,
    )
    # is_public describes whether the product is listed on the public catalogue
    is_public = models.BooleanField(default=True)

    def request(self, requester: "Company", user: "User") -> "ProductSharingRequest":
        # Block requests to your own company
        if requester == self.supplier:
            raise ValueError("You cannot request access to your own product.")
        # Block requests to private products
        if not self.is_public:
            raise ValueError("You cannot request access to a private product.")
        return ProductSharingRequest.objects.get_or_create(
            product=self,
            requester=requester,
        )

    def get_emission_trace(self) -> EmissionTrace:
        root = EmissionTrace(
            label=f"Product: {self.name}",
            methodology=f"Sum up all the product-level emissions and its line items' emissions.",
            reference_impact_unit=ReferenceImpactUnit(self.reference_impact_unit),
            related_object=self,
            pcf_calculation_method=PcfCalculationMethod(self.pcf_calculation_method),
        )
        # Add own emissions
        for emission_obj in self.emissions.all():
            emission_obj_real: "Emission" = emission_obj.get_real_instance()
            if emission_obj_real is None:
                logger.warning(f"Emission {emission_obj} has no content object.")
                continue
            emission_trace = emission_obj_real.get_emission_trace()
            root.children.add(EmissionTraceChild(
                emission_trace=emission_trace,
                quantity=emission_obj_real.quantity,
            ))

        # Add emissions from line items
        for line_item in self.line_items.all():
            # Check if the line item is shared and if the request is accepted
            if line_item.product_sharing_request_status is None:
                emission_trace = EmissionTrace(
                    label=f"Product: {line_item.line_item_product.name}",
                    reference_impact_unit=ReferenceImpactUnit.OTHER,
                    related_object=line_item.line_item_product,
                    pcf_calculation_method=PcfCalculationMethod(self.pcf_calculation_method)
                )
                emission_trace.mentions.append(EmissionTraceMention(
                    mention_class=EmissionTraceMentionClass.ERROR,
                    message="You have not requested access to this product's PCF data yet."
                ))

            elif line_item.product_sharing_request_status == ProductSharingRequestStatus.PENDING:
                emission_trace = EmissionTrace(
                    label=f"Product: {line_item.line_item_product.name}",
                    reference_impact_unit=ReferenceImpactUnit.OTHER,
                    related_object=line_item.line_item_product,
                    pcf_calculation_method=PcfCalculationMethod(self.pcf_calculation_method))
                emission_trace.mentions.append(EmissionTraceMention(
                    mention_class=EmissionTraceMentionClass.ERROR,
                    message=f"{line_item.product_sharing_request.supplier.name} "
                            f"has not accepted your PCF data sharing request yet."
                ))

            elif line_item.product_sharing_request_status == ProductSharingRequestStatus.REJECTED:
                emission_trace = EmissionTrace(
                    label=f"Product: {line_item.line_item_product.name}",
                    reference_impact_unit=ReferenceImpactUnit.OTHER,
                    related_object=line_item.line_item_product,
                    pcf_calculation_method=PcfCalculationMethod(self.pcf_calculation_method)
                )
                emission_trace.mentions.append(EmissionTraceMention(
                    mention_class=EmissionTraceMentionClass.ERROR,
                    message=f"{line_item.product_sharing_request.supplier.name} "
                            f"has rejected your PCF data sharing request."
                ))

            else:
                # Get the line item's emissions
                emission_trace = line_item.line_item_product.get_emission_trace()
                # Hide the children
                emission_trace.children.clear()
                emission_trace.mentions.append(
                    EmissionTraceMention(
                        mention_class=EmissionTraceMentionClass.INFORMATION,
                        message=f"Further emission trace details are hidden to protect "
                                f"{line_item.line_item_product.supplier.name}'s confidentiality."
                    )
                )

            # Add the line item to the root
            root.children.add(EmissionTraceChild(
                emission_trace=emission_trace,
                quantity=line_item.quantity
            ))

        root.sum_up()

        # Check if there are any EmissionOverrideFactors
        # If so, replace the emission trace with the overridden values
        if self.override_factors.exists():
            root.emissions_subtotal.clear()
            root.methodology = "User-provided values"
            root.mentions.append(EmissionTraceMention(
                mention_class=EmissionTraceMentionClass.WARNING,
                message="Emission factors are overridden by user-provided values"
            ))
            for factor in self.override_factors.all():
                root.emissions_subtotal[LifecycleStage(factor.lifecycle_stage)] = factor.co_2_emission_factor

        return root
    get_emission_trace.short_description = "Emissions trace"


    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["name"]

    export_to_aas_aasx = product_to_aas_aasx
    export_to_aas_xml = product_to_aas_xml
    export_to_aas_json = product_to_aas_json
    export_to_scsn_full_xml = product_to_scsn_full_xml
    export_to_scsn_pcf_xml = product_to_scsn_pcf_xml

    def __str__(self):
        return self.name

class ProductEmissionOverrideFactor(models.Model):
    emission = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="override_factors",
    )
    lifecycle_stage = models.CharField(
        max_length=255,
        choices=LifecycleStage.choices,
        default=LifecycleStage.OTHER,
    )
    co_2_emission_factor = models.FloatField()