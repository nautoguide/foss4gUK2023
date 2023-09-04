import re

from elasticsearch_dsl.query import MultiMatch, Wildcard
from geocoder.documents import OpenNamesDocument
from geocoder.serializers import OpenNamesSerializer

"""
Find a postcode in a string, will return the matched full postcode if found or the original search string

"""


def postcode_finder(searchtext):
    matches = []
    # Full postcode match
    full_match = re.compile(
        r'([A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2})',
        re.IGNORECASE)

    # Basic search looking from anything from an outwards onwards
    partial_match = re.compile(
        r'.*([A-Z]{1,2}[0-9]).*',
        re.IGNORECASE
    )

    postcode_found = bool(partial_match.match(searchtext))

    if postcode_found:
        matches = full_match.search(searchtext)

    return postcode_found, matches.group(1).replace(' ', '').upper() if matches else searchtext


"""
Construct a location search query, is postcode aware so can use this to prioritise the search
"""


def location_search_query(searchtext, postcode_priority=True, address_priority=True):
    # Postcodes treated differently
    if postcode_priority:
        postcode_found, postcode = postcode_finder(searchtext)
        if postcode_found:
            return Wildcard(postcode=f'{postcode}*')

    # Standard location search
    search_fields = ['name1^5', 'addressline']
    # Prioritise the address search if 3 or more words
    if len(searchtext.split()) > 2 and address_priority:
        search_fields = ['name1', 'addressline^2']

    return MultiMatch(query=searchtext, fields=search_fields, type='phrase')


"""
Run a location search and return serialized data
"""


def location_search(searchtext, **kwargs):
    page = kwargs.get('page', 0)
    page_size = kwargs.get('page_size', 20)
    query = location_search_query(searchtext, kwargs.get('postcode_priority', True),
                                  kwargs.get('address_priority', True))

    search = OpenNamesDocument.search().query(query)[page:page_size]
    results = search.execute()
    pages = round(results.hits.total.value / page_size)
    data = OpenNamesSerializer(results, many=True).data
    return data, pages


"""
Make geojson from a location structure
"""


def geojson_from_location(location, icon='point'):
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "properties": {
                    "icon": icon
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(location.get('lon')), float(location.get('lat'))]
                }
            }
        ]
    }


def geojson_from_items(items):
    geojson = {"type": "FeatureCollection", "features": []}

    for item in items:
        location = item.get('location')
        if location:
            geojson['features'].append({"properties": {"icon": "point"},
                                        "geometry": {"type": "Point",
                                                     "coordinates": [
                                                         location.get('lon'), location.get('lat')]}})

    return geojson
