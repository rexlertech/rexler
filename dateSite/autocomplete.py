from dal import autocomplete
from .models.catalog import Occupation, Country


class OccupationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Occupation.objects.none()

        qs = Occupation.objects.filter(ocuactive=True)

        if self.q:
            qs = qs.filter(ocudescription__istartswith=self.q)

        return qs


class CountryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Country.objects.none()

        qs = Country.objects.filter(couactive=True)

        if self.q:
            qs = qs.filter(couname__istartswith=self.q)

        return qs
