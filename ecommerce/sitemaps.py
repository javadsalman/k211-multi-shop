from django.contrib import sitemaps
from django.urls import reverse
from shop.models import Product



class StaticViewSitemap(sitemaps.Sitemap):
    
    def items(self):
        return [
            'shop:home', 
            'shop:product-list', 
            'customer:contact', 
            'customer:login',
            'customer:register'
        ]

    def location(self, item):
        return reverse(item)
    
    priorities = {
        'shop:home': 0.9,
        'shop:product-list': 0.4,
        'customer:contact': 0.6,
        'customer:login': 0.5,
        'customer:register': 0.5,
    }
    def priority(self, item):
        return self.priorities[item]
    
    changefreqs = {
        'shop:home': 'daily',
        'shop:product-list': 'always',
        'customer:contact': 'monthly',
        'customer:login': 'yearly',
        'customer:register': 'yearly',
    }
    def changefreq(self, item):
        return self.changefreqs[item]


class ProductViewSitemap(sitemaps.Sitemap):
    priority = 0.8
    changefreq = 'daily'
    
    def items(self):
        return Product.objects.all()

    def lastmod(self, item):
        return item.updated