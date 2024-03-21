from django.contrib import admin
from .models import Category, Region, News, Author

# Register your models here.
admin.site.register(Category)
admin.site.register(Author)
admin.site.register(Region)
admin.site.register(News)
