from django.shortcuts import render
from django.urls import reverse

def robots(request):
    site_map_url = request.build_absolute_uri(reverse('django.contrib.sitemaps.views.sitemap'))
    return render(request, 'robots.txt', {'site_map_url': site_map_url}, content_type='text/plain')