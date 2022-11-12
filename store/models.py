from django.db import models
from django.urls import reverse

from category.models import Category

# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        # url: str = f"/store/{self.category.slug}/{self.slug}"
        url: str = reverse('product_detail_page', args=[self.category.slug, self.slug])
        print(f"The url for {self.product_name} is {url}")
        return url

    def __str__(self):
        return self.product_name
