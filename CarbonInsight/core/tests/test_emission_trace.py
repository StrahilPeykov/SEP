from typing import Union
from rest_framework.test import APITestCase
from core.models import CompanyMembership, Product, ProductBoMLineItem, User, MaterialEmissionReference, \
    MaterialEmissionReferenceFactor, MaterialEmission, TransportEmissionReference, TransportEmissionReferenceFactor, \
    TransportEmission, EmissionBoMLink, emission_trace, ProductionEnergyEmissionReference, UserEnergyEmissionReference, \
    ProductionEnergyEmission, UserEnergyEmission, ProductionEnergyEmissionReferenceFactor, \
    UserEnergyEmissionReferenceFactor, ProductSharingRequest, ProductSharingRequestStatus, EmissionOverrideFactor
from core.models.company import Company
from core.models.emission_trace import EmissionTrace, EmissionTraceMentionClass
from core.models.lifecycle_stage import LifecycleStage
from core.models.product import ProductEmissionOverrideFactor


class EmissionTraceTestCase(APITestCase):
    def setUp(self):
        admin_user = User.objects.create_user(username="admin@example.com", email="admin@example.com",
                                              password="1234567890")
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        apple_user_1 = User.objects.create_user(username="apple1@apple.com", email="apple1@apple.com",
                                                password="1234567890")
        apple_user_2 = User.objects.create_user(username="apple2@apple.com", email="apple2@apple.com",
                                                password="1234567890")
        samsung_user_1 = User.objects.create_user(username="samsung1@samsung.com", email="samsung1@samsung.com",
                                                  password="1234567890")
        corning_user_1 = User.objects.create_user(username="corning1@corning.com", email="corning1@corning.com",
                                                  password="1234567890")
        tsmc_user_1 = User.objects.create_user(username="tsmc1@tsmc.com", email="tsmc1@tsmc.com", password="1234567890")

        # Create test companies
        apple = Company.objects.create(
            name="Apple Inc.",
            vat_number="TEST123456",
            business_registration_number="REG123456"
        )
        samsung = Company.objects.create(
            name="Samsung Electronics",
            vat_number="TEST654321",
            business_registration_number="REG654321"
        )
        corning = Company.objects.create(
            name="Corning Inc.",
            vat_number="TEST789012",
            business_registration_number="REG789012"
        )
        tsmc = Company.objects.create(
            name="Taiwan Semiconductor Manufacturing Company",
            vat_number="TEST345678",
            business_registration_number="REG345678"
        )

        # Create company memberships
        CompanyMembership.objects.create(user=admin_user, company=apple)
        CompanyMembership.objects.create(user=admin_user, company=samsung)
        CompanyMembership.objects.create(user=admin_user, company=corning)
        CompanyMembership.objects.create(user=admin_user, company=tsmc)
        CompanyMembership.objects.create(user=apple_user_1, company=apple)
        CompanyMembership.objects.create(user=apple_user_2, company=apple)
        CompanyMembership.objects.create(user=samsung_user_1, company=samsung)
        CompanyMembership.objects.create(user=corning_user_1, company=corning)
        CompanyMembership.objects.create(user=tsmc_user_1, company=tsmc)

        # Add raw materials
        glass_material = MaterialEmissionReference.objects.create(common_name="Glass")
        MaterialEmissionReferenceFactor.objects.create(
            emission_reference=glass_material,
            lifecycle_stage=LifecycleStage.A1,
            co_2_emission_factor=0.5,
        )
        self.silicon_material = MaterialEmissionReference.objects.create(common_name="Silicon")
        MaterialEmissionReferenceFactor.objects.create(
            emission_reference=self.silicon_material,
            lifecycle_stage=LifecycleStage.A2,
            co_2_emission_factor=0.3,
        )
        MaterialEmissionReferenceFactor.objects.create(
            emission_reference=self.silicon_material,
            lifecycle_stage=LifecycleStage.A1,
            co_2_emission_factor=0.2,
        )

        # Add products to companies
        self.processor = Product.objects.create(
            name="A14 processor",
            description="Main processor used in iPhones",
            supplier=tsmc,
            year_of_construction = 2025
        )
        self.processor2 = Product.objects.create(
            name="A16 processor",
            description="ARM processor",
            supplier=tsmc,
            year_of_construction=2025
        )
        self.pins= Product.objects.create(
            name="Pins",
            description="Pins",
            supplier=samsung,
            year_of_construction=2025
        )
        self.casing = Product.objects.create(
            name="Casing",
            description="Casing",
            supplier=apple,
            year_of_construction=2025
        )
        fake_product = Product.objects.create(
            name="Fake Product",
            description="Product that only has overrides",
            supplier=tsmc,
            year_of_construction=2025
        )
        self.fake_material_emission = MaterialEmission.objects.create(
            parent_product=fake_product,
            weight=0.5,
            reference=self.silicon_material,
        )
        self.processor_material_emission = MaterialEmission.objects.create(
            parent_product=self.processor,
            weight=0.5,
            reference=self.silicon_material,
        )
        processor_material_emission2 = MaterialEmission.objects.create(
            parent_product=self.processor,
            weight=0.5,
            reference=glass_material,
        )
        self.processor_material_emission3 = MaterialEmission.objects.create(
            parent_product=self.processor2,
            weight=0.5,
            reference=self.silicon_material,
        )
        self.pins_material_emission = MaterialEmission.objects.create(
            parent_product=self.pins,
            weight=0.5,
            reference=self.silicon_material,
        )
        self.casing_material_emission = MaterialEmission.objects.create(
            parent_product=self.casing,
            weight=0.5,
            reference=self.silicon_material,
        )
        camera = Product.objects.create(
            name="Camera module",
            description="Camera module used in various phones",
            supplier=samsung,
            year_of_construction=2025
        )
        camera_material_emission = MaterialEmission.objects.create(
            parent_product=camera,
            weight=0.2,
            reference=glass_material,
        )
        display = Product.objects.create(
            name="Display",
            description="Display used in various phones",
            supplier=samsung,
            year_of_construction=2025
        )
        display_self_estimated_pollution = MaterialEmission.objects.create(
            parent_product=display,
            weight=0.3,
            reference=glass_material,
        )
        self.iphone = Product.objects.create(
            name="iPhone 17",
            description="Latest iPhone model",
            supplier=apple,
            year_of_construction=2025
        )
        iphone_line_processor = ProductBoMLineItem.objects.create(
            parent_product=self.iphone,
            line_item_product=self.processor,
            quantity=1
        )
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

        self.transport_air = TransportEmissionReference.objects.create(common_name="Air transport")
        TransportEmissionReferenceFactor.objects.create(
            emission_reference=self.transport_air,
            lifecycle_stage=LifecycleStage.A3,
            co_2_emission_factor=0.2,
        )
        TransportEmissionReferenceFactor.objects.create(
            emission_reference=self.transport_air,
            lifecycle_stage=LifecycleStage.A4,
            co_2_emission_factor=0.3,
        )
        transport_road = TransportEmissionReference.objects.create(common_name="Road transport")
        TransportEmissionReferenceFactor.objects.create(
            emission_reference=transport_road,
            lifecycle_stage=LifecycleStage.A3,
            co_2_emission_factor=0.05,
        )
        self.iphone_line_processor_transport = TransportEmission.objects.create(
            parent_product=self.iphone,
            distance=2000,
            weight=0.5,
            reference=self.transport_air
        )
        self.arm_processor_transport = TransportEmission.objects.create(
            parent_product=self.processor2,
            distance=2000,
            weight=0.3,
            reference=self.transport_air
        )
        self.fake_transport_emission = TransportEmission.objects.create(
            parent_product=fake_product,
            distance=2000,
            weight=0.3,
            reference=self.transport_air
        )
        EmissionBoMLink.objects.create(
            emission=self.iphone_line_processor_transport,
            line_item=iphone_line_processor,
        )
        iphone_line_camera = ProductBoMLineItem.objects.create(
            parent_product=self.iphone,
            line_item_product=camera,
            quantity=3
        )
        iphone_line_camera_transport = TransportEmission.objects.create(
            parent_product=self.iphone,
            distance=500,
            weight=0.2,
            reference=transport_road,
        )
        EmissionBoMLink.objects.create(
            emission=iphone_line_camera_transport,
            line_item=iphone_line_camera,
        )
        iphone_line_display = ProductBoMLineItem.objects.create(
            parent_product=self.iphone,
            line_item_product=display,
            quantity=1
        )
        iphone_line_display_transport = TransportEmission.objects.create(
            parent_product=self.iphone,
            distance=800,
            weight=0.3,
            reference=transport_road,
        )
        EmissionBoMLink.objects.create(
            emission=iphone_line_display_transport,
            line_item=iphone_line_display,
        )
        self.assembly_line_reference = ProductionEnergyEmissionReference.objects.create(common_name="Assembly line")
        ProductionEnergyEmissionReferenceFactor.objects.create(
            emission_reference=self.assembly_line_reference,
            lifecycle_stage=LifecycleStage.A3,
            co_2_emission_factor=0.4,
        )
        self.iphone_assembly_emission = ProductionEnergyEmission.objects.create(
            parent_product=self.iphone,
            energy_consumption=2000,
            reference=self.assembly_line_reference,
        )
        self.arm_processor_assembly_emission = ProductionEnergyEmission.objects.create(
            parent_product=self.processor2,
            energy_consumption=2000,
            reference=self.assembly_line_reference,
        )
        self.fake_production_energy_emission = ProductionEnergyEmission.objects.create(
            parent_product=fake_product,
            energy_consumption=2000,
            reference=self.assembly_line_reference,
        )
        self.update_processor = UserEnergyEmissionReference.objects.create(common_name="Update processor")
        UserEnergyEmissionReferenceFactor.objects.create(
            emission_reference=self.update_processor,
            lifecycle_stage=LifecycleStage.A5,
            co_2_emission_factor=0.2,
        )
        self.arm_processor_update_emission = UserEnergyEmission.objects.create(
            parent_product=self.processor2,
            energy_consumption=500,
            reference=self.update_processor,
        )
        self.charging_phone = UserEnergyEmissionReference.objects.create(common_name="Charging phone")
        UserEnergyEmissionReferenceFactor.objects.create(
            emission_reference=self.charging_phone,
            lifecycle_stage=LifecycleStage.A5,
            co_2_emission_factor=0.2,
        )
        self.iphone_charging_emission = UserEnergyEmission.objects.create(
            parent_product=self.iphone,
            energy_consumption=500,
            reference=self.charging_phone
        )
        self.fake_user_energy_emission = UserEnergyEmission.objects.create(
            parent_product=fake_product,
            energy_consumption=500,
            reference=self.charging_phone
        )

        EmissionOverrideFactor.objects.create(
            emission=self.arm_processor_assembly_emission,
            lifecycle_stage=LifecycleStage.A5,
            co_2_emission_factor=3000,
        )
        EmissionOverrideFactor.objects.create(
            emission=self.arm_processor_transport,
            lifecycle_stage=LifecycleStage.A3,
            co_2_emission_factor=3000,
        )
        ProductEmissionOverrideFactor.objects.create(
            emission=self.pins,
            lifecycle_stage=LifecycleStage.A1,
            co_2_emission_factor=300,
        )

        #Overrides for fake_product
        EmissionOverrideFactor.objects.create(
            emission=self.fake_material_emission,
            lifecycle_stage=LifecycleStage.A1,
            co_2_emission_factor=9999
        )
        EmissionOverrideFactor.objects.create(
            emission=self.fake_transport_emission,
            lifecycle_stage=LifecycleStage.A3,
            co_2_emission_factor=69
        )
        EmissionOverrideFactor.objects.create(
            emission=self.fake_production_energy_emission,
            lifecycle_stage=LifecycleStage.A3,
            co_2_emission_factor=420
        )
        EmissionOverrideFactor.objects.create(
            emission=self.fake_production_energy_emission,
            lifecycle_stage=LifecycleStage.A4,
            co_2_emission_factor=420
        )
        EmissionOverrideFactor.objects.create(
            emission=self.fake_user_energy_emission,
            lifecycle_stage=LifecycleStage.A5,
            co_2_emission_factor=21
        )

        ProductSharingRequest.objects.create(
            product = camera,
            requester = apple,
            status = ProductSharingRequestStatus.ACCEPTED
        )
        ProductSharingRequest.objects.create(
            product=self.processor,
            requester=apple,
            status=ProductSharingRequestStatus.REJECTED
        )
        ProductSharingRequest.objects.create(
            product=self.pins,
            requester=tsmc,
            status=ProductSharingRequestStatus.ACCEPTED
        )
        ProductSharingRequest.objects.create(
            product=self.casing,
            requester=tsmc,
            status=ProductSharingRequestStatus.REJECTED
        )


    def _check_emission_reference_trace(
            self,
            trace:EmissionTrace,
            reference:Union[
                MaterialEmissionReference,
                TransportEmissionReference,
                ProductionEnergyEmissionReference,
                UserEnergyEmissionReference
            ]
    ):
        """
        List the lifecycle stages and the co2 factor of material emission reference and check if method returns correct
        stages and values
        """
        emission_subtotal = {}
        for factor in reference.reference_factors.all():
            emission_subtotal[factor.lifecycle_stage] = factor.co_2_emission_factor
        self.assertEqual(len(emission_subtotal), len(trace.emissions_subtotal))
        for lifecycle_stage in emission_subtotal:
            self.assertEqual(emission_subtotal[lifecycle_stage], trace.emissions_subtotal[lifecycle_stage])

    def _check_emission_trace(
            self,
            trace: EmissionTrace
    ):
        """
                List the lifecycle stages and the emissions of material emission and check if method returns correct stages
                and values
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

        emission_subtotal_overriden = {}
        for override in emission.override_factors.all():
            if override.lifecycle_stage in emission_subtotal_overriden:
                emission_subtotal_overriden[override.lifecycle_stage] = (
                        emission_subtotal_overriden[override.lifecycle_stage]+
                        override.co_2_emission_factor)
            else:
                emission_subtotal_overriden[override.lifecycle_stage] = override.co_2_emission_factor

        self.assertEqual(len(emission_subtotal_overriden), len(trace.emissions_subtotal))
        for lifecycle_stage in emission_subtotal_overriden:
            self.assertEqual(emission_subtotal_overriden[lifecycle_stage],
                             trace.emissions_subtotal[lifecycle_stage])

        self.assertEqual(
            trace.mentions[0].mention_class,
            EmissionTraceMentionClass.WARNING
        )

    def _check_product_emission_trace(
            self,
            trace: EmissionTrace
    ):
        """
                List the lifecycle stages and the emissions of material emission and check if method returns correct stages
                and values
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

    def test_materia_emission_reference_get_emission_trace(self):
        reference = self.silicon_material
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = reference.get_emission_trace()
        self._check_emission_reference_trace(returned_trace, reference)


    def test_materia_emission_get_emission_trace(self):
        emission = self.processor_material_emission
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = emission.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, MaterialEmission)
        # Check if the quantity is returned correctly
        for child in returned_trace.children:
            self.assertEqual(emission.weight, child.quantity)
        self._check_emission_trace(returned_trace)

    def test_materia_emission_get_emission_trace_override(self):
        emission = self.fake_material_emission
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = emission.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, MaterialEmission)

        self._check_emission_trace_overriden(emission, returned_trace)

    def test_transport_emission_reference_get_emission_trace(self):
        reference = self.transport_air
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = reference.get_emission_trace()
        self._check_emission_reference_trace(returned_trace, reference)

    def test_transport_emission_get_emission_trace(self):
        emission = self.iphone_line_processor_transport
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = emission.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, TransportEmission)
        quantity = emission.weight * emission.distance
        for child in returned_trace.children:
            self.assertEqual(quantity, child.quantity)
        self._check_emission_trace(returned_trace)

    def test_transport_emission_get_emission_trace_override(self):
        emission = self.fake_transport_emission
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = emission.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, TransportEmission)
        self._check_emission_trace_overriden(emission, returned_trace)

    def test_production_energy_emission_reference_get_emission_traces(self):
        reference = self.assembly_line_reference
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = reference.get_emission_trace()
        self._check_emission_reference_trace(returned_trace, reference)

    def test_production_energy_emission_get_emission_traces(self):
        emission = self.iphone_assembly_emission
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = emission.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, ProductionEnergyEmission)
        for child in returned_trace.children:
            self.assertEqual(emission.energy_consumption, child.quantity)
        self._check_emission_trace(returned_trace)

    def test_production_energy_emission_get_emission_trace_override(self):
        emission = self.fake_production_energy_emission
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = emission.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, ProductionEnergyEmission)

        self._check_emission_trace_overriden(emission, returned_trace)

    def test_user_energy_emission_reference_get_emission_traces(self):
        reference = self.charging_phone
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = reference.get_emission_trace()
        self._check_emission_reference_trace(returned_trace, reference)

    def test_user_energy_emission_get_emission_traces(self):
        emission = self.iphone_charging_emission
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = emission.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, UserEnergyEmission)
        for child in returned_trace.children:
            self.assertEqual(emission.energy_consumption, child.quantity)
        self._check_emission_trace(returned_trace)

    def test_user_energy_emission_get_emission_trace_override(self):
        emission = self.fake_user_energy_emission
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = emission.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, UserEnergyEmission)

        self._check_emission_trace_overriden(emission, returned_trace)

    def test_product_get_emission_no_sub_product(self):
        product = self.processor
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = product.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, Product)
        #Pass quantity as 1 since the method only needs to sum up the sub-totals of children without multiplication
        self._check_product_emission_trace(returned_trace)

    def test_product_get_emission(self):
        product = self.iphone
        # Call for .get_emission_trace and check if the returned trace's item is correct
        returned_trace = product.get_emission_trace()
        self.assertIsInstance(returned_trace.related_object, Product)
        #Pass quantity as 1 since the method only needs to sum up the sub-totals of children without multiplication
        self._check_product_emission_trace(returned_trace)

    def test_product_get_emission_product_mention_class_checks(self):
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