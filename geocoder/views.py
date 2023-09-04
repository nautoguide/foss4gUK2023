from django.shortcuts import redirect
from django.views.generic import TemplateView


# Create your views here.

class LocationSearchView(TemplateView):
    template_name = 'location_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = 'location'
        return context


def reverse_geocoder(request, lon, lat):
    url = f'/location/?ordering=geom__{lat}__{lon}&limit=1'
    return redirect(url)


def reverse_type_geocoder(request, type, lon, lat):
    type = type.replace(' ', '__')
    url = f'/location/?ordering=geom__{lat}__{lon}&limit=1&local_type__terms={type}'
    return redirect(url)


def geocoder(request, search_term):
    url = f'/location/?search=name1:{search_term}'
    return redirect(url)
