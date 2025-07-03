import django_filters
from apps.products.models.category import Category
from apps.products.models.product import Product, STATUS_CHOICES


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    status = django_filters.ChoiceFilter(choices=STATUS_CHOICES)
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Product
        fields = ["name", "status", "category", "is_active", "min_price", "max_price"]
