from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Coupon(models.Model):
    title = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    discount = models.FloatField()
    used_customers = models.ManyToManyField('customer.Customer', related_name='used_coupons', blank=True)
    expire = models.DateTimeField()
    limit = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def is_valid(self, customer):
        if timezone.localtime() > self.expire:
            return [False, _('This coupon has expried!')]
        elif self.used_customers.count() >= self.limit:
            return [False, _('This coupon has already reached limit!')]
        elif self.used_customers.contains(customer):
            return [False, _('You already used this coupon!')]
        else:
            return [True, _('Coupon succesfully aplied!')]
        
        
COUNTRIES = [
    ('azerbaijan', 'Azerbaijan'),
    ('turkey', 'Turkey'),
    ('georgia', 'Georgia'),
    ('russia', 'Russia'),
]
class Order(models.Model):
    customer = models.ForeignKey('customer.Customer', on_delete=models.SET_NULL, null=True)
    coupon_code = models.CharField(max_length=20, null=True, blank=True)
    coupon_discount = models.IntegerField(default=0)
    accepted = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    mobile = models.CharField(max_length=50)
    country = models.CharField(max_length=50, choices=COUNTRIES)
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    
    
class OrderedProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=50)
    count = models.IntegerField()
    price = models.FloatField()
    size = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)