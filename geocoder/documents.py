from django.conf import settings
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from geocoder.models import Opennames


@registry.register_document
class OpenNamesDocument(Document):
    model_name = fields.KeywordField()
    geom = fields.GeoPointField()
    postcode = fields.TextField()
    addressline = fields.TextField()

    # We are filtering on specific values so use a KeywordField
    local_type = fields.KeywordField(attr='local_type')

    settings = settings.ELASTICSEARCH_SETTINGS

    class Index:
        name = settings.GEOCODER_INDEX

    class Django:
        model = Opennames
        queryset = Opennames.objects.all()
        fields = Opennames.fields_to_index()

    """
    Override the prepare method and remove all null fields
    """

    def prepare(self, instance):
        prepared_data = super(OpenNamesDocument, self).prepare(instance)

        # List of fields to check and default to empty string if None
        fields_to_check = Opennames.fields_to_index()

        for field in fields_to_check:
            if prepared_data.get(field) is None:
                prepared_data[field] = ''

        return prepared_data
    @staticmethod
    def prepare_model_name(instance):
        return instance.__class__.__name__

    @staticmethod
    def prepare_geom(instance):
        if instance.geom:
            return {'lat': instance.geom.y, 'lon': instance.geom.x}

        return None

    # This removes spaces from postcodes to support better matching
    @staticmethod
    def prepare_postcode(instance):
        name1_value = instance.name1
        postcode_value = ''
        if instance.local_type == 'Postcode':
            postcode_value = name1_value.replace(' ', '')
        return postcode_value

    @staticmethod
    def prepare_addressline(instance):
        addressline_value = ''
        if instance.local_type in ['Section Of Named Road', 'Named Road']:
            addressline_value = f'{instance.name1} {instance.populated_place if instance.populated_place else ""} {instance.postcode_district if instance.postcode_district else ""} {instance.district_borough if instance.district_borough else ""} {instance.county_unitary if instance.county_unitary else ""}'

        return addressline_value

    class Meta(object):
        queryset_pagination = 50
