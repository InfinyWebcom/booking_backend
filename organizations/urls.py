from django.urls import path

from organizations.views.property import Properties
from organizations.views.booking import Booking, cancel_booking
from organizations.views.categories import Categories
from organizations.views.state_city import state, city, city_by_state, amenities
from organizations.views.dashboard import get_statistics

urlpatterns = [
    path("properties", Properties.as_view(), name="properties"),
    path("booking", Booking.as_view(), name="booking"),
    path("cancel-booking", cancel_booking, name="cancel-booking"),
    path("turf-categories", Categories.as_view(), name="turf-categories"),
    path("state", state, name="state"),
    path("city", city, name="city"),
    path("amenities", amenities, name="amenities"),
    path("city-by-state", city_by_state, name="city-by-state"),
    path("get-statistics", get_statistics, name="get-statistics"),
]
