from django.contrib import admin
from accounts.models import User, Role

# # Register your models here.
admin.site.register([User, Role])
admin.site.site_header = "Booking Slots"
admin.site.index_title = "Welcome to Booking Slots Portal"
