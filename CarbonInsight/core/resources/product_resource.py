from typing import Optional, Dict, Any

from import_export import resources
from core.models import Product

class ProductResource(resources.ModelResource):
    """
    Facilitates import and export of Product objects.
    """


    class Meta:
        model = Product
        exclude = ('id', 'supplier')
        import_id_fields = ('name', 'manufacturer_name', 'sku')
        skip_unchanged = True
        report_skipped = False

    def before_save_instance(self, instance: Product, row: Optional[Dict[str, Any]], **kwargs):
        """
        Hook that runs before saving a model instance.

        Args:
            instance: Product instance
            row: The data row being processed.
        """

        supplier = kwargs.get('supplier')
        if supplier:
            instance.supplier = supplier
        super().before_save_instance(instance, row, **kwargs)