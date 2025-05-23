from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from rapidfuzz import fuzz, process

from core.models import Product, Emission, TransportEmission, TransportEmissionReference, UserEnergyEmission, \
    ProductionEnergyEmission, MaterialEmission


def lookup_pk(queryset, raw_name, name_attr='name', pk_attr='pk', cutoff=75):
    """
    Fuzzy‐match raw_name against the `name_attr` of objects in `queryset`,
    returning the corresponding `pk_attr`, or None if no match ≥ cutoff.
    """
    # Build a map of normalized names → PKs
    reference = {}
    names = []
    for obj in queryset:
        name_val = getattr(obj, name_attr, '')
        key = name_val.lower().strip()
        reference[key] = getattr(obj, pk_attr)
        names.append(key)

    # Normalize input
    key = raw_name.lower().strip()

    # Exact match shortcut
    if key in reference:
        return reference[key]

    # Fuzzy‐match
    match = process.extractOne(key, names, scorer=fuzz.token_sort_ratio)
    if match:
        matched_name, score, _ = match
        if score >= cutoff:
            return reference[matched_name]

    return None

class FuzzyFKWidget(ForeignKeyWidget):
    def __init__(self, model, name_attr='name', cutoff=75):
        super().__init__(model, field=name_attr)
        self.name_attr = name_attr
        self.cutoff = cutoff

    def clean(self, value, row=None, *args, **kwargs):
        qs = self.model.objects.all()
        pk = lookup_pk(
            queryset=qs,
            raw_name=value,
            name_attr=self.name_attr,
            pk_attr='pk',
            cutoff=self.cutoff
        )
        if pk is None:
            raise ValueError(f"Couldn’t match '{value}' to any reference")
        return self.model.objects.get(pk=pk)

class EmissionResource(resources.ModelResource):
    reference = fields.Field(
        column_name='reference',
        attribute='reference',
        widget=FuzzyFKWidget(
            TransportEmissionReference,
            name_attr='name',
            cutoff=20
        ),
    )

    class Meta:
        model = Emission
        exclude = ('id', 'emission_ptr', 'polymorphic_ctype', 'parent_product', 'line_items')
        import_id_fields = () # Always create a new instance

    def before_save_instance(self, instance, row, **kwargs):
        product = kwargs.get('product')
        if product:
            instance.parent_product = product
        super().before_save_instance(instance, row, **kwargs)

class TransportEmissionResource(EmissionResource):
    class Meta:
        model = TransportEmission
        exclude = EmissionResource.Meta.exclude
        import_id_fields = EmissionResource.Meta.import_id_fields

class UserEnergyEmissionResource(EmissionResource):
    class Meta:
        model = UserEnergyEmission
        exclude = EmissionResource.Meta.exclude
        import_id_fields = EmissionResource.Meta.import_id_fields

class ProductionEnergyEmissionResource(EmissionResource):
    class Meta:
        model = ProductionEnergyEmission
        exclude = EmissionResource.Meta.exclude
        import_id_fields = EmissionResource.Meta.import_id_fields

class MaterialEmissionResource(EmissionResource):
    class Meta:
        model = MaterialEmission
        exclude = EmissionResource.Meta.exclude
        import_id_fields = EmissionResource.Meta.import_id_fields