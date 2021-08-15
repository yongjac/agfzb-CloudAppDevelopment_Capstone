from django.contrib import admin
# from .models import related models
from .models import CarModel, CarMake

# Register your models here.

# CarModelInline class
class CarMakeInline(admin.StackedInline):
    model = CarMake

# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    inlines = [CarMakeInline]

# CarMakeAdmin class with CarModelInline

# Register models here
admin.site.register(CarMake)
admin.site.register(CarModel, CarModelAdmin)
