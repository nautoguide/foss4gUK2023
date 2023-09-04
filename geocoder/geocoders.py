import pyproj

from django.contrib.gis.geos import Point
from geocoder.models import Opennames


class OpennamesGeocoder:
    @staticmethod
    def geocode(postcode):
        try:
            # Query the OpenName model using the provided postcode and local_type constraint
            postcode = postcode.replace(' ', '')
            formatted_postcode = " ".join([postcode[:-3], postcode[-3:]]).upper()
            result = Opennames.objects.get(name1=formatted_postcode, local_type='Postcode')

            # Return the coordinates as a tuple
            return result.geom

        except Opennames.DoesNotExist:

            # If no matching result is found, return None
            return None


class GridRefGeocoder:

    @staticmethod
    def geocode(gridref, crs='EPSG:4326'):
        try:
            # Convert UK grid reference to easting and northing coordinates
            letters = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'
            easting = 0
            northing = 0
            gridref = gridref.upper()
            for i in range(len(gridref)):
                if gridref[i] in letters:
                    easting = easting * 26 + letters.index(gridref[i]) + 1
                    northing = northing * 26 + letters.index(gridref[i + 1]) + 1
                    break
            easting += int(gridref[i + 2:i + 5]) * 100
            northing += int(gridref[i + 5:i + 8]) * 100

            # Create a GeoDjango point geometry object
            point = Point(easting, northing, srid=27700)
            point.transform(crs)

            return point
        except Exception as e:
            return None


class CoordinateGeocoder:

    @staticmethod
    def geocode(x, y, in_crs='EPSG:4326', out_crs='EPSG:4326'):
        # need a numeric code for CRS to set point srid
        in_crs_code = pyproj.CRS(in_crs).to_epsg()

        # Convert strings to floats
        try:
            x = float(x)
            y = float(y)
        except ValueError:
            return None

        # Create a GeoDjango point geometry in the output CRS
        point = Point(x, y, srid=in_crs)
        point.srid = in_crs_code
        point.transform(out_crs)

        return point


def geocoder(item):
    point = None
    lat = item.get('latitude')
    lon = item.get('longitude')
    if lat and lon:
        point = CoordinateGeocoder.geocode(lon, lat)
    elif item.get('gridref'):
        point = GridRefGeocoder.geocode(item.get('gridref'))
    elif item.get('locationpostcode'):
        point = OpennamesGeocoder.geocode(item.get('locationpostcode'))

    return point


def point_to_grid_ref(location):
    easting = location.x
    northing = location.y

    grid_letters = [
        ['SV', 'SW', 'SX', 'SY', 'SZ', 'TV', 'TW'],
        ['SQ', 'SR', 'SS', 'ST', 'SU', 'TQ', 'TR'],
        ['SL', 'SM', 'SN', 'SO', 'SP', 'TL', 'TM'],
        ['SF', 'SG', 'SH', 'SJ', 'SK', 'TF', 'TG'],
        ['SA', 'SB', 'SC', 'SD', 'SE', 'TA', 'TB'],
        ['OV', 'OW', 'OX', 'OY', 'OZ', 'OV', 'OW'],
        ['OQ', 'OR', 'OS', 'OT', 'OU', 'OQ', 'OR'],
    ]

    # Calculate the grid indices
    x_idx = int(easting // 100000)
    y_idx = int(northing // 100000)

    # Calculate the 100km grid letters
    try:
        grid_ref = grid_letters[y_idx][x_idx]
    except IndexError:
        # Not a UK location
        return None

    # Calculate the remaining easting and northing within the 100km grid cell
    easting_remainder = int(easting % 100000)
    northing_remainder = int(northing % 100000)

    # Calculate the 1km grid digits
    grid_ref += f"{easting_remainder // 100:02}{northing_remainder // 100:02}"

    # Truncate the grid reference to 8 characters
    grid_ref = grid_ref[:8]

    return grid_ref


def reverse_geocoder_latlon(lon, lat, local_type=('Postcode',)):
    # we use raw SQL to ensure the <-> operator for speed
    nearest = Opennames.objects.raw(
        f'SELECT id,name1 from {Opennames._meta.db_table} WHERE local_type in %s ORDER BY geom <-> ST_SetSRID(ST_MakePoint(%s, %s),4326) LIMIT 1',
        [local_type, lon, lat])
    item = next(iter(nearest), None)

    return item.name1 if item else ''
