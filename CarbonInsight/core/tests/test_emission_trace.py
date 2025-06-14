"""
Tests for the emission trace methods that calculate PCF and return subcomponents of a product
"""

from typing import Union

from rest_framework.test import APITestCase

from core.models import Product, ProductBoMLineItem, TransportEmissionReference, TransportEmission, \
    ProductionEnergyEmissionReference, UserEnergyEmissionReference, \
    ProductionEnergyEmission, UserEnergyEmission, ProductSharingRequest, ProductSharingRequestStatus, \
    EmissionOverrideFactor
from core.models.emission_trace import EmissionTrace, EmissionTraceMentionClass
from core.models.lifecycle_stage import LifecycleStage
from core.models.product import ProductEmissionOverrideFactor
from core.tests.setup_functions import tech_companies_setup


class EmissionTraceTestCase(APITestCase):
    def setUp(self):
        tech_companies_setup(self)

        # remove from initial setup
        self.iphone_iphone_line_processor_transport_override.delete()

        #Add additional porducts
        self.processor2 = Product.objects.create(
            name="A16 processor",
            description="ARM processor",
            supplier=self.tsmc,
            year_of_construction=2025
        )
        self.pins= Product.objects.create(
            name="Pins",
            description="Pins",
            supplier=self.samsung,
            year_of_construction=2025
        )
        self.casing = Product.objects.create(
            name="Casing",
            description="Casing",
            supplier=self.apple,
            year_of_construction=2025
        )

        #Add material references to products BoM
        self.processor_material_reference3 = ProductBoMLineItem.objects.create(
            parent_product=self.processor2,
            quantity=0.5,
            line_item_product=self.silicon_material,
        )
        self.pins_material_reference = ProductBoMLineItem.objects.create(
            parent_product=self.pins,
            quantity=0.5,
            line_item_product=self.silicon_material,
        )
        self.casing_material_reference = ProductBoMLineItem.objects.create(
            parent_product=self.casing,
            quantity=0.5,
            line_item_product=self.silicon_material,
        )

        # Add additional BoM items
        processor2_base = ProductBoMLineItem.objects.create(
            parent_product=self.processor2,
            line_item_product=self.processor,
            quantity=2
        )
        processor2_pins = ProductBoMLineItem.objects.create(
            parent_product=self.processor2,
            line_item_product=self.pins,
            quantity=64
        )
        processor2_casing = ProductBoMLineItem.objects.create(
            parent_product=self.processor2,
            line_item_product=self.casing,
            quantity=3
        )

        # Add additional BoM item transport emissions
        self.arm_processor_transport = TransportEmission.objects.create(
            parent_product=self.processor2,
            distance=2000,
            weight=0.3,
            reference=self.transport_air
        )

        # Add additional production energy emissions to products
        self.arm_processor_assembly_emission = ProductionEnergyEmission.objects.create(
            parent_product=self.processor2,
            energy_consumption=2000,
            reference=self.assembly_line_reference,
        )

        # Add additional user energy emissions to products
        self.arm_processor_update_emission = UserEnergyEmission.objects.create(
            parent_product=self.processor2,
            energy_consumption=500,
            reference=self.update_processor,
        )

        # Add additional emission override factors
        EmissionOverrideFactor.objects.create(
            emission=self.arm_processor_assembly_emission,
            lifecycle_stage=LifecycleStage.A5,
            co_2_emission_factor_biogenic=3000,
        )
        EmissionOverrideFactor.objects.create(
            emission=self.arm_processor_transport,
            lifecycle_stage=LifecycleStage.A3,
            co_2_emission_factor_biogenic=3000,
        )
        ProductEmissionOverrideFactor.objects.create(
            product=self.pins,
            lifecycle_stage=LifecycleStage.A1,
            co_2_emission_factor_biogenic=300,
        )

        # Add additional product sharing requests
        ProductSharingRequest.objects.create(
            product=self.pins,
            requester=self.tsmc,
            status=ProductSharingRequestStatus.ACCEPTED
        )
        ProductSharingRequest.objects.create(
            product=self.casing,
            requester=self.tsmc,
            status=ProductSharingRequestStatus.REJECTED
        )


    def _check_emission_reference_trace(
            self,
            trace:EmissionTrace,
            reference:Union[
                TransportEmissionReference,
                ProductionEnergyEmissionReference,
                UserEnergyEmissionReference
            ]
    ):
        """
        List the lifecycle stages and the co2 factor of the emission references and check if method returns correct
         stages and values.

        Args:
            trace: emission trace object
            reference: emission reference type
        """
        emission_subtotal = {}
        for factor in reference.reference_factors.all():
            emission_subtotal[factor.lifecycle_stage] = factor.co_2_emission_factor_biogenic
        self.assertEqual(len(emission_subtotal), len(trace.emissions_subtotal))
        for lifecycle_stage in emission_subtotal:
            self.assertEqual(emission_subtotal[lifecycle_stage], trace.emissions_subtotal[lifecycle_stage].biogenic)

    def _check_emission_trace(
            self,
            trace: EmissionTrace
    ):
        """
        List the lifecycle stages and the emissions and check if method returns correct stages
         and values

        Args:
            trace: emission trace object
        """
        emission_subtotal_by_weight = {}
        for child in trace.children:
            for lifecycle_stage in child.emission_trace.emissions_subtotal:
                if lifecycle_stage in emission_subtotal_by_weight:
                    emission_subtotal_by_weight[lifecycle_stage] = (
                            emission_subtotal_by_weight[lifecycle_stage]
                            + child.emission_trace.emissions_subtotal[lifecycle_stage] * child.quantity)
                else:
                    emission_subtotal_by_weight[lifecycle_stage] = (
                            child.emission_trace.emissions_subtotal[lifecycle_stage] * child.quantity)

        self.assertEqual(len(emission_subtotal_by_weight), len(trace.emissions_subtotal))
        for lifecycle_stage in emission_subtotal_by_weight:
            self.assertEqual(emission_subtotal_by_weight[lifecycle_stage],
                             trace.emissions_subtotal[lifecycle_stage])

    def _check_emission_trace_overriden(self,emission,trace):
        """
        List the lifecycle stages and the emissions and check if method returns correct stages
         and values for the overriden trace emissions
        Args:
            emission: emission object
            trace: emission trace object
        """

        emission_subtotal_overriden = {}
        for override in emission.override_factors.all():
            if override.lifecycle_stage in emission_subtotal_overriden:
                emission_subtotal_overriden[override.lifecycle_stage] = (
                        emission_subtotal_overriden[override.lifecycle_stage]+
                        override.co_2_emission_factor_biogenic)
            else:
                emission_subtotal_overriden[override.lifecycle_stage] = override.co_2_emission_factor_biogenic

        self.assertEqual(len(emission_subtotal_overriden), len(trace.emissions_subtotal))
        for lifecycle_stage in emission_subtotal_overriden:
            self.assertEqual(emission_subtotal_overriden[lifecycle_stage],
                             trace.emissions_subtotal[lifecycle_stage].biogenic)

        self.assertEqual(
            trace.mentions[0].mention_class,
            EmissionTraceMentionClass.WARNING
        )

    def _check_product_emission_trace(
            self,
            trace: EmissionTrace
    ):
        """
        List the lifecycle stages and the emissions product and check if method returns correct stages
         and values

        Args:
            trace: emission trace object
        """
        emission_subtotal_by_weight = {}
        for child in trace.children:
            if "Product" in child.emission_trace.label:
                quantity = child.quantity
            else:
                quantity = 1
            for lifecycle_stage in child.emission_trace.emissions_subtotal:
                if lifecycle_stage in emission_subtotal_by_weight:
                    emission_subtotal_by_weight[lifecycle_stage] = (
                            emission_subtotal_by_weight[lifecycle_stage]
                            + child.emission_trace.emissions_subtotal[lifecycle_stage] * quantity)
                else:
                    emission_subtotal_by_weight[lifecycle_stage] = (
                            child.emission_trace.emissions_subtotal[lifecycle_stage] * quantity)

        self.assertEqual(len(emission_subtotal_by_weight), len(trace.emissions_subtotal))
        for lifecycle_stage in emission_subtotal_by_weight:
            self.assertEqual(emission_subtotal_by_weight[lifecycle_stage],
                             trace.emissions_subtotal[lifecycle_stage])

    def test_transport_emission_reference_get_emission_trace(self):
        """
        Test for emission trace method called on transport emission reference.
        """

        reference = self.transport_air
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = reference.get_emission_trace()
        self._check_emission_reference_trace(returned_trace, reference)

    def test_transport_emission_get_emission_trace(self):
        """
        Test for emission trace method called on transport emission.
        """

        emission = self.iphone_line_processor_transport
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = emission.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, TransportEmission)
        quantity = emission.weight * emission.distance
        for child in returned_trace.children:
            self.assertEqual(quantity, child.quantity)
        self._check_emission_trace(returned_trace)

    def test_transport_emission_get_emission_trace_override(self):
        """
        Test for emission trace method called on transport emission that has emission overide factor.
        """

        EmissionOverrideFactor.objects.create(
            emission=self.iphone_line_processor_transport,
            lifecycle_stage=LifecycleStage.A3,
            co_2_emission_factor_biogenic=69
        )
        emission = self.iphone_line_processor_transport
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = emission.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, TransportEmission)
        self._check_emission_trace_overriden(emission, returned_trace)

    def test_production_energy_emission_reference_get_emission_traces(self):
        """
        Test for emission trace method called on production energy emission reference.
        """

        reference = self.assembly_line_reference
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = reference.get_emission_trace()
        self._check_emission_reference_trace(returned_trace, reference)

    def test_production_energy_emission_get_emission_traces(self):
        """
        Test for emission trace method called on production energy emission.
        """

        emission = self.iphone_assembly_emission
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = emission.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, ProductionEnergyEmission)
        for child in returned_trace.children:
            self.assertEqual(emission.energy_consumption, child.quantity)
        self._check_emission_trace(returned_trace)

    def test_production_energy_emission_get_emission_trace_override(self):
        """
        Test for emission trace method called on production energy emission that has emission override factor.
        """

        EmissionOverrideFactor.objects.create(
            emission=self.iphone_assembly_emission,
            lifecycle_stage=LifecycleStage.A3,
            co_2_emission_factor_biogenic=420
        )
        emission = self.iphone_assembly_emission
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = emission.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, ProductionEnergyEmission)

        self._check_emission_trace_overriden(emission, returned_trace)

    def test_user_energy_emission_reference_get_emission_traces(self):
        """
        Test for emission trace method called on user energy emission reference.
        """

        reference = self.charging_phone
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = reference.get_emission_trace()
        self._check_emission_reference_trace(returned_trace, reference)

    def test_user_energy_emission_get_emission_traces(self):
        """
        Test for emission trace method called on user energy emission.
        """

        emission = self.iphone_charging_emission
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = emission.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, UserEnergyEmission)
        for child in returned_trace.children:
            self.assertEqual(emission.energy_consumption, child.quantity)
        self._check_emission_trace(returned_trace)

    def test_user_energy_emission_get_emission_trace_override(self):
        """
        Test for emission trace method called on user energy emission that has emission override factor.
        """

        EmissionOverrideFactor.objects.create(
            emission=self.iphone_charging_emission,
            lifecycle_stage=LifecycleStage.A5,
            co_2_emission_factor_biogenic=21
        )
        emission = self.iphone_charging_emission
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = emission.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, UserEnergyEmission)

        self._check_emission_trace_overriden(emission, returned_trace)

    def test_product_get_emission_no_sub_product(self):
        """
        Test for emission trace method called on a product that does not contain a sub product.
        """

        self.processor_material_reference.delete()
        self.processor_material_reference2.delete()

        product = self.processor
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = product.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, Product)
        #Pass quantity as 1 since the method only needs to sum up the sub-totals of children without multiplication
        self._check_product_emission_trace(returned_trace)

    def test_product_get_emission(self):
        """
        Test for emission trace method called on a product.
        """

        product = self.iphone
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = product.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, Product)
        #Pass quantity as 1 since the method only needs to sum up the sub-totals of children without multiplication
        self._check_product_emission_trace(returned_trace)

    def test_product_get_emission_product_mention_class_checks(self):
        """
        Test that checks if the emission trace method returns the correct mention classes.
        """

        product = self.processor2
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = product.get_emission_trace()

        for trace_child in returned_trace.children:
            if trace_child.emission_trace.related_object.__class__ == Product:
                if product.supplier == trace_child.emission_trace.related_object.supplier:
                    if len(trace_child.emission_trace.related_object.override_factors.all()) == 0:
                        self.assertEqual(
                            trace_child.emission_trace.mentions[0].mention_class,
                            EmissionTraceMentionClass.INFORMATION
                        )
                    else:
                        self.assertEqual(
                            trace_child.emission_trace.mentions[0].mention_class,
                            EmissionTraceMentionClass.WARNING
                        )
                elif ProductSharingRequest.objects.filter(
                        product = trace_child.emission_trace.related_object,
                        requester = product.supplier,
                        status = ProductSharingRequestStatus.ACCEPTED,
                ).exists():
                    if len(trace_child.emission_trace.related_object.override_factors.all()) == 0:
                        self.assertEqual(
                            trace_child.emission_trace.mentions[0].mention_class,
                            EmissionTraceMentionClass.INFORMATION
                        )
                    else:
                        self.assertEqual(
                            trace_child.emission_trace.mentions[0].mention_class,
                            EmissionTraceMentionClass.WARNING
                        )
                else:
                    if trace_child.emission_trace.related_object.supplier.is_reference == True:
                        self.assertEqual(
                            trace_child.emission_trace.mentions[0].mention_class,
                            EmissionTraceMentionClass.INFORMATION
                        )
                    else:
                        self.assertEqual(
                            trace_child.emission_trace.mentions[0].mention_class,
                            EmissionTraceMentionClass.ERROR
                        )
            else:
                if len(trace_child.emission_trace.related_object.override_factors.all()) == 0:
                    self.assertEqual(
                        trace_child.emission_trace.mentions,
                        []
                    )
                else:
                    self.assertEqual(
                        trace_child.emission_trace.mentions[0].mention_class,
                        EmissionTraceMentionClass.WARNING
                    )