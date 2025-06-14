from collections import defaultdict, deque

from django.db import models
from django.db.models import Q, Sum, F
from django.db.models.functions import Coalesce


class Company(models.Model):
    """
    Model that represents a company.
    """

    name = models.CharField(max_length=255)
    vat_number = models.CharField(max_length=255, unique=True)
    business_registration_number = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(
        "User", through="CompanyMembership", related_name="companies"
    )
    is_reference = models.BooleanField(default=False)
    auto_approve_product_sharing_requests = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_reference"],
                condition=Q(is_reference=True),
                name="unique_reference_company"
            )
        ]

    def user_is_member(self, user) -> bool:
        """
        Checks if a user is a member of the company.

        Args:
            user: an object type User
        Returns:
            True if the user is a member of the company
        """

        return self.users.filter(id=user.id).exists()

    def __str__(self) -> str:
        """
        __str__ override that returns the name of the company object.

        Returns:
            Name of the company
        """
        return self.name

    @property
    def companies_using_count(self) -> int:
        """
        Number of *distinct* companies whose products' BoMs include at least one
        product supplied by this company.
        """
        return Company.objects.filter(
            products__used_in_line_items__line_item_product__supplier=self
        ).distinct().count()

    @property
    def products_using_count(self) -> int:
        """
        Number of *distinct* products that include a product supplied by this company in their BoM.
        """
        from .product_bom_line_item import ProductBoMLineItem

        return ProductBoMLineItem.objects \
            .filter(line_item_product__supplier=self) \
            .values('parent_product_id') \
            .distinct() \
            .count()

    @property
    def total_emissions_across_products(self) -> float:
        """
        Compute, for each product this company supplies, the TOTAL number of times
        it's used in ANY depth of any BoM (direct + indirect), then multiply by
        that product's emissions and sum all up.

        Avoids double-counting products supplied by this company in case Company A->B->A supply chains exist.
        """
        from .product import Product
        from .product_bom_line_item import ProductBoMLineItem
        # 1) Build child→[(parent, qty), …] adjacency in one DB hit
        rows = ProductBoMLineItem.objects.values(
            'quantity',
            child_id=F('line_item_product'),
            parent_id=F('parent_product'),
        )
        adj = defaultdict(list)
        for r in rows:
            adj[r['child_id']].append((r['parent_id'], r['quantity']))

        # 2) Build a map & set of the products this company supplies
        supplied_qs = self.products.all()
        supplied = {p.id: p for p in supplied_qs}
        supplied_ids = set(supplied)

        total_emissions = 0.0

        # 3) For each supplied product, BFS up—but skip parents you supply yourself
        for prod_id, prod in supplied.items():
            use_count = 0.0
            queue = deque([(prod_id, 1.0)])  # (node, cumulative_multiplier)

            while queue:
                node_id, mult = queue.popleft()
                for parent_id, qty in adj.get(node_id, []):
                    # ignore any parent that's also supplied by self
                    if parent_id in supplied_ids:
                        continue
                    contrib = mult * qty
                    use_count += contrib
                    queue.append((parent_id, contrib))

            # 4) Multiply by this product's emission total
            total_emissions += use_count * prod.get_emission_trace().total

        return total_emissions