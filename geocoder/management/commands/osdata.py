import os
import subprocess
import tempfile
import zipfile
import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class OSLoader(BaseCommand):
    product_url = settings.DEFAULT_URLS.get('osproducts')

    def __init__(self, **kwargs):
        BaseCommand.__init__(self)
        self.stdout.write(self.style.NOTICE('Downloading product metadata'))
        self.product = kwargs.get('product')
        self.format = kwargs.get('format')
        self.filename = None

        if self.format != 'GeoPackage':
            raise CommandError('Only GeoPackage support at present')

        try:
            product_details = None
            os_products = requests.get(self.product_url).json()
            product_list = []
            for product in os_products:
                product_list.append(product['id'])
                if product['id'] == self.product:
                    self.stdout.write(self.style.NOTICE(f'Found Product {self.product}'))
                    product_details = requests.get(product['url']).json()
                    break

            if product_details is None:
                raise CommandError(f'{self.product} Not found {product_list}')

            format_list = requests.get(product_details["downloadsUrl"]).json()
            for formats in format_list:
                if formats["format"] == self.format:
                    self.stdout.write(self.style.NOTICE(f'Found Format {formats["format"]}'))
                    self.downloadURL = formats['url']
                    self.osfilename = formats['fileName']
        except Exception as Error:
            raise CommandError(str(Error))

    def handle(self, *args, **options):
        pass

    def download(self, **kwargs):
        if self.downloadURL is None:
            raise CommandError('Download url not set please check product/url')

        os_data = requests.get(self.downloadURL, stream=True)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            for chunk in os_data.iter_content(chunk_size=kwargs.get('chunk_size', 8192)):
                f.write(chunk)

            f.flush()

        self.filename = f.name
        self.stdout.write(self.style.NOTICE(f'Downloaded to  {self.filename}'))

        # OS data is always zipped up so need to unzip
        with zipfile.ZipFile(self.filename, 'r') as zip_ref:
            temp_extract_folder = tempfile.mkdtemp()
            zip_ref.extractall(temp_extract_folder)

        self.stdout.write(self.style.NOTICE(f'Unzipped to  {self.filename}'))

        if self.format == 'GeoPackage':
            return self.geopackage(temp_extract_folder)

    def geopackage(self, temp_extract_folder):

        gpkg_file = None
        for root, dirs, files in os.walk(temp_extract_folder):
            for file in files:
                if file.endswith('.gpkg'):
                    gpkg_file = os.path.join(root, file)
                    break

        if gpkg_file:
            self.stdout.write(self.style.SUCCESS(f'Found geopackage file: {gpkg_file}'))
            self.filename = gpkg_file
            return {'filename': gpkg_file}
        else:
            self.stdout.write(self.style.ERROR(f'No geopackage file found in the downloaded ZIP file.'))
            return {}

    def ogr_import(self, **kwargs):

        sql_add = kwargs.get('sql','')

        if not self.filename:
            raise CommandError('filename not set have you downloaded data')

        db_settings = settings.DATABASES['default']

        if db_settings['ENGINE'] != 'django.contrib.gis.db.backends.postgis':
            raise CommandError("This function only supports the PostGIS database backend")

        schema = settings.SCHEMA
        if not schema:
            self.stdout.write(self.style.WARNING('SCHEMA variable not set in settings.py will write to public schema'))

        model_name = kwargs.get('model_name')

        if not model_name:
            raise CommandError('Missing model_name parameter')

        ogr2ogr_command = [
            'ogr2ogr',
            '-f', 'PostgreSQL',
            'PG:host={host} user={user} port= {port} dbname={dbname} password={password}'.format(
                host=db_settings['HOST'],
                user=db_settings['USER'],
                port=db_settings['PORT'],
                dbname=db_settings['NAME'],
                password=db_settings['PASSWORD']
            ),
            self.filename,
            '-nln', f"{schema}.{model_name}",
            '-append',
            '-update',
            '-sql', f"SELECT {sql_add} id AS ogc_fid, * FROM {kwargs.get('layer_name')}",
            '-lco', f"GEOMETRY_NAME={kwargs.get('geometry_name', 'geom')}",
            '--config', 'OGR_TRUNCATE', 'YES',
            '--config', 'PG_USE_COPY', 'YES',
            '-s_srs', kwargs.get('s_srs', 'EPSG:27700'),
            '-t_srs', kwargs.get('t_srs', 'EPSG:4326')
        ]

        self.stdout.write(self.style.NOTICE(" ".join(ogr2ogr_command[4:])))

        layer = kwargs.get('layers')
        if layer:
            ogr2ogr_command.extend([layer])

        result = subprocess.run(ogr2ogr_command, capture_output=True, text=True)

        if result.returncode != 0:
            raise CommandError(f"Error running ogr2ogr: {result.stderr}")
        else:
            self.stdout.write(self.style.SUCCESS(f"Data uploaded to  {schema}.{model_name}"))

        return {'result': result}


