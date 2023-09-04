from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import MySpatialTable

@admin.register(MySpatialTable)
class MySpatialTableAdmin(OSMGeoAdmin):
    list_display = ('name', 'geometry')
