from django.test import TestCase
from django.contrib.gis.geos import Point
from geocoder.models import Opennames

class OpennamesTest(TestCase):

    def setUp(self):
        self.openname_1 = Opennames.objects.create(
            ogc_fid='fid1',
            name1='Name1',
            geom=Point(5, 23)
            # Other fields can be added here...
        )
        self.openname_2 = Opennames.objects.create(
            ogc_fid='fid2',
            name1='Name2',
            geom=Point(15, 45)
            # Other fields can be added here...
        )

    def test_create_openname(self):
        self.assertIsNotNone(self.openname_1.id)
        self.assertEqual(self.openname_1.ogc_fid, 'fid1')
        self.assertEqual(self.openname_1.name1, 'Name1')

    def test_retrieve_openname(self):
        retrieved_openname = Opennames.objects.get(id=self.openname_1.id)
        self.assertEqual(retrieved_openname.ogc_fid, 'fid1')
        self.assertEqual(retrieved_openname.name1, 'Name1')

    def test_update_openname(self):
        self.openname_1.name1 = 'UpdatedName1'
        self.openname_1.save()
        updated_openname = Opennames.objects.get(id=self.openname_1.id)
        self.assertEqual(updated_openname.name1, 'UpdatedName1')

    def test_delete_openname(self):
        openname_id = self.openname_1.id
        self.openname_1.delete()
        with self.assertRaises(Opennames.DoesNotExist):
            Opennames.objects.get(id=openname_id)

    def test_index_filter(self):
        # Testing the index with condition local_type='Postcode'
        openname_with_postcode = Opennames.objects.create(
            ogc_fid='fid3',
            name1='Name3',
            local_type='Postcode',
            geom=Point(10, 20)
        )
        result = Opennames.objects.filter(local_type='Postcode')
        self.assertIn(openname_with_postcode, result)

