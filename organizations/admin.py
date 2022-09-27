from django.contrib import admin
from organizations.models.property import Property, Amenity
from organizations.models.turf_category import TurfCategory
from organizations.models.booking import Booking
from organizations.models.transactions import Transaction
from organizations.models.state_city import City, State

# Register your models here.
admin.site.register(
    [TurfCategory, Property, Booking, Transaction, City, State, Amenity]
)
