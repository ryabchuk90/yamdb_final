import django_filters
from .models import Title


class TitlesFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(
        field_name='genre__slug', lookup_expr='icontains')
    category = django_filters.CharFilter(
        field_name='category__slug', lookup_expr='icontains')
    year = django_filters.NumberFilter(
        field_name='year')
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ('genre', 'category', 'year', 'name')
