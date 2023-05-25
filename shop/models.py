from django.db import models
from django.contrib.admin import display
from django.utils.html import format_html
from django.urls import reverse
from ckeditor.fields import RichTextField
from shared.urlutils import get_slug

# Create your models here.

class Size(models.Model):
    title = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.title

class Color(models.Model):
    title = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.title

class GeneralCategory(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title

class Category(models.Model):
    title = models.CharField(max_length=20)
    image = models.ImageField(upload_to='categories')
    general_category = models.ForeignKey(GeneralCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_categories')

    def __str__(self):
        return self.title

class Campaign(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    is_slide = models.BooleanField(default=False)
    image = models.ImageField(upload_to='campaigns')
    discount_percent = models.FloatField()

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.TextField(max_length=50)
    slug = models.CharField(max_length=100, blank=True)
    old_price = models.FloatField(null=True, blank=True)
    price = models.FloatField()
    featured = models.BooleanField(default=False)
    description = RichTextField()
    sizes = models.ManyToManyField(Size, related_name='products')
    colors = models.ManyToManyField(Color, related_name='products')
    categories = models.ManyToManyField(Category, related_name='products')
    campaigns = models.ManyToManyField(Campaign, related_name='products')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.slug = get_slug(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("shop:product-detail", kwargs={"pk": self.pk, "slug": self.slug})
    
    def get_avg_star(self):
        return self.reviews.aggregate(star_count_avg=models.Avg('star_count'))['star_count_avg']
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images')

    @display(description='Movcud Sekil')
    def image_tag(self):
        return format_html(f'<img width="200" src="{self.image.url}">')
    