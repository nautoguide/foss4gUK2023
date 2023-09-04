from django.contrib.gis.db import models


class MySpatialTable(models.Model):
    name = models.TextField()
    geometry = models.PointField(srid=4326)