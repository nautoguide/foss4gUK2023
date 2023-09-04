import uuid

from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from .documents import OpenNamesDocument


class OpenNamesSerializer(DocumentSerializer):
    class Meta:
        document = OpenNamesDocument
        fields = (
            'id',
            'name1',
            'name2',
            'local_type',
            'postcode_district',
            'populated_place',
            'district_borough',
            'county_unitary',
            'region',
            'country',
            'geom',
            'postcode',
            'addressline'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['score'] = instance.meta.score
        data['icon'] = 'point'
        data['id'] = uuid.uuid4()
        geojson = {
            "properties": data,
            "geometry": {
                "type": "Point",
                "coordinates": [data['geom']['lon'], data['geom']['lat']]
            }
        }

        return geojson
