import django_filters
from .models import Post

class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """multiple numbers (ids=1,2,3)"""
    pass

class PostFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(field_name="id", lookup_expr="exact") # for single id
    ids = NumberInFilter(field_name="id", lookup_expr="in") # for multiple id's 
    author = django_filters.NumberFilter(field_name="author__id", lookup_expr="exact")# for author id
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")# for date range

    class Meta:
        model = Post
        fields = ["id", "ids", "author", "created_at"]
