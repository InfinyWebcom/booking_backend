from django.db import models
from accounts.models import User

# Create your models here.
class Booking(models.Model):
    PAYMENT_CHOICES = [
        ("NULL", "Null"),
        ("CASH", "CASH"),
        ("ONLINE", "ONLINE"),
    ]
    payment_mode = models.CharField(
        max_length=150, choices=PAYMENT_CHOICES, default="NULL"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="booking_user",
    )

    isBooked = models.BooleanField(default=False)
    booking_amount = models.FloatField(null=True, blank=True, default=0)
    pending_amount = models.FloatField(null=True, blank=True, default=0)

    def __str__(self):
        return f"{self.id}-{self.user}-{self.isBooked}"
