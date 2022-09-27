from django.db import models
from accounts.models import User
from organizations.models.booking import Booking as BookingDetails

# Create your models here.
class Transaction(models.Model):
    rent_amount = models.FloatField(null=True, blank=False)
    transaction_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transaction_user",
    )
    booking = models.ForeignKey(
        BookingDetails,
        on_delete=models.CASCADE,
        related_name="transaction_booking",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.id}"
