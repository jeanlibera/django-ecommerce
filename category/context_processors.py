from .models import Category

def get_product_categories(request):
    product_categories = Category.objects.all()
    return dict(product_categories = product_categories)