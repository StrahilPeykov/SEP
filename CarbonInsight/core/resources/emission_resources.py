from typing import Optional, Union, Dict, Any

from django.db.models import QuerySet
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from rapidfuzz import fuzz, process

from core.models import Emission, TransportEmission, TransportEmissionReference, UserEnergyEmission, \
    ProductionEnergyEmission, ProductionEnergyEmissionReference, UserEnergyEmissionReference


def lookup_pk(queryset: QuerySet, raw_name:str, name_attr:str='name', pk_attr:str='pk', cutoff:int=75)->Optional[int]:
    """
    Fuzzy‐match raw_name against the `name_attr` of objects in `queryset`,
     returning the corresponding `pk_attr`, or None if no match ≥ cutoff.

    Args:
        queryset: QuerySet of objects to search through
        raw_name: The raw name input to match against
        name_attr: The attribute name to use for matching names
        pk_attr: The attribute name to return as the primary key
        cutoff: The minimum score for a fuzzy match to be considered valid
    Returns:
        The primary key of the matched object, or None if no match is found
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
    """
    Class that connects a user input to the actual Emission models, corrects user typo's to ensure sound database.
    """

    def __init__(
            self,
            model:Union[
                 type[UserEnergyEmissionReference],
                 type[ProductionEnergyEmissionReference],
                 type[TransportEmissionReference]
            ],
            name_attr:str='name',
            cutoff:int=75
        ):
        """
        __init__ override that initializes FuzzyFKWidget instance.

        Args:
            model: The model class for which this widget is used to look up references on.
            name_attr: The attribute name to use for matching names.
            cutoff: The minimum score for a fuzzy match to be considered valid.
        """

        super().__init__(model, field=name_attr)
        self.name_attr = name_attr
        self.cutoff = cutoff

    def clean(self, value:str, row:Optional[Dict[str, Any]]=None, *args, **kwargs):
        """
        Cleans and validates the input value by matching it to a model instance.

        Args:
            value: The value to be cleaned, typically a string representing the name of the reference.
            row: Optional; a dictionary representing the current row of data being processed.
        """

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
    """
    Facilitates import and export of Emission objects.
    """
    class Meta:
        model = Emission
        exclude = ('id', 'emission_ptr', 'polymorphic_ctype', 'parent_product', 'line_items')
        import_id_fields = () # Always create a new instance

    def before_save_instance(self, instance: Emission, row: Optional[Dict[str, Any]], **kwargs):
        """
        Hook that runs before saving a model instance.

        Args:
            instance: Emission instance
            row: The data row being processed.
        """

        product = kwargs.get('product')
        if product:
            instance.parent_product = product
        super().before_save_instance(instance, row, **kwargs)

class TransportEmissionResource(EmissionResource):
    """
    Facilitates import and export of TransportEmission objects.
    """

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
        model = TransportEmission
        exclude = EmissionResource.Meta.exclude
        import_id_fields = EmissionResource.Meta.import_id_fields

class UserEnergyEmissionResource(EmissionResource):
    """
    Facilitates import and export of UserEnergyEmission objects.
    """

    reference = fields.Field(
        column_name='reference',
        attribute='reference',
        widget=FuzzyFKWidget(
            UserEnergyEmissionReference,
            name_attr='name',
            cutoff=20
        ),
    )

    class Meta:
        model = UserEnergyEmission
        exclude = EmissionResource.Meta.exclude
        import_id_fields = EmissionResource.Meta.import_id_fields

class ProductionEnergyEmissionResource(EmissionResource):
    """
    Facilitates import and export of ProductionEnergyEmission objects.
    """

    reference = fields.Field(
        column_name='reference',
        attribute='reference',
        widget=FuzzyFKWidget(
            ProductionEnergyEmissionReference,
            name_attr='name',
            cutoff=20
        ),
    )

    class Meta:
        model = ProductionEnergyEmission
        exclude = EmissionResource.Meta.exclude
        import_id_fields = EmissionResource.Meta.import_id_fields