from import_export import resources
from core.models import Product

class ProductResource(resources.ModelResource):

    class Meta:
        model = Product
        exclude = ('id', 'supplier')
        import_id_fields = ('name', 'manufacturer_name', 'sku')
        skip_unchanged = True
        report_skipped = False

    def before_save_instance(self, instance, row, **kwargs):
        supplier = kwargs.get('supplier')
        if supplier:
            instance.supplier = supplier
        super().before_save_instance(instance, row, **kwargs)