import logging

from django_unicorn.components import UnicornView
from geocoder.utils import location_search


class LocationSearchView(UnicornView):
    search_results = []
    searchtext = ''
    paginator = None
    page = 0
    page_size = 20
    pages = None
    url = None
    selected = None
    hasMap = True

    def updated_searchtext(self, searchtext):
        if len(self.searchtext) > 2:
            self.search()

    def clear_results(self):
        logging.info("CLEARING RESULTS")
        self.search_results = []

    def clear_search(self):
        self.searchtext = ''

    def focus(self, id):
        self.selected = id

        if self.hasMap:
            self.call("set_selected", id)
            self.clear_results()

    def search(self):
        if self.searchtext:
            self.pages, self.search_results = location_search(self.searchtext,
                                                              page=self.page,
                                                              page_size=self.page_size)
            if self.hasMap:
                self.call("reload_map", {"type": "FeatureCollection", "features": self.search_results})
        else:
            self.clear_results()

    def set_page(self, page_number):
        self.page = min(page_number, self.pages)
        self.search()

    def previous_page(self):
        self.page = max(self.page - 1, 1)
        self.search()

    def next_page(self):
        if self.page < self.pages:
            self.page += 1

        self.search()
