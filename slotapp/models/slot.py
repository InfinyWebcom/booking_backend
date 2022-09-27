from accounts.models import User
from organizations.models.property import Property
from organizations.models.booking import Booking as BookingDetails
from django.db import models

# Create your models here.
class Slot(models.Model):
    date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="slot_property",
        blank=True,
        null=True,
    )

    booking = models.ForeignKey(
        BookingDetails,
        on_delete=models.CASCADE,
        related_name="slot_booked",
        blank=True,
        null=True,
    )

    class meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.id}"
