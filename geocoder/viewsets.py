import logging

from django_elasticsearch_dsl_drf.constants import LOOKUP_FILTER_GEO_DISTANCE, LOOKUP_QUERY_IN, LOOKUP_FILTER_TERM, \
    LOOKUP_FILTER_TERMS
from django_elasticsearch_dsl_drf.filter_backends import (
    CompoundSearchFilterBackend,
    IdsFilterBackend,
    FilteringFilterBackend,
    GeoSpatialFilteringFilterBackend,
    GeoSpatialOrderingFilterBackend
)
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination, LimitOffsetPagination
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet

from .documents import OpenNamesDocument
from .serializers import OpenNamesSerializer


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'


class OpenNamesViewSet(DocumentViewSet):
    filter_backends = [
        CompoundSearchFilterBackend,
        IdsFilterBackend,
        FilteringFilterBackend,
        GeoSpatialFilteringFilterBackend,
        GeoSpatialOrderingFilterBackend
    ]

    search_fields = ('name1', 'name2', 'postcode_district', 'populated_place', 'district_borough',
                     'county_unitary', 'region', 'postcode', )

    geo_spatial_filter_fields = {
        'geom': {
            'field': 'geom',
            'lookups': [
                LOOKUP_FILTER_GEO_DISTANCE,
            ]
        }
    }
    geo_spatial_ordering_fields = {
        'geom': {
            'field': 'geom'
        }
    }

    filter_fields = {
        'local_type': {
            'field': 'local_type',
            'lookups': [LOOKUP_QUERY_IN, LOOKUP_FILTER_TERM, LOOKUP_FILTER_TERMS]
        }
    }
    pagination_class = LimitOffsetPagination
    lookup_field = 'id'
    document = OpenNamesDocument
    serializer_class = OpenNamesSerializer
    model_name = 'Opennames'

    # If you need to debug the query sent to ES
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        logging.info(f"Generated GEOCODER queryset: {queryset.to_dict()}")
        return super().list(request, *args, **kwargs)
