from django.contrib import admin

# Register your models here.
from .models import Elevator, Floor, Building

admin.site.register(Elevator)
admin.site.register(Floor)
admin.site.register(Building)