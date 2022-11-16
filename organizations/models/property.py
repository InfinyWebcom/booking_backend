from email.policy import default
from django.db import models
from organizations.models.turf_category import TurfCategory
from accounts.models import User

# from accounts.models import User
# Create your models here.


class Amenity(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["name"]


class Property(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)
    city = models.CharField(max_length=256, null=True, blank=True)
    state = models.CharField(max_length=256, null=True, blank=True)
    # image = models.ImageField(
    #     upload_to="organizations/static/imgs",
    #     height_field=None,
    #     width_field=None,
    #     max_length=100,
    # )
    latitude = models.FloatField(null=False, blank=False)
    longitude = models.FloatField(null=False, blank=False)
    is_available = models.BooleanField(default=True)
    rent = models.FloatField(null=True, blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="property_owners", default=""
    )
    turf_category = models.ForeignKey(
        TurfCategory,
        on_delete=models.CASCADE,
        related_name="properties",
    )
    amenity = models.ManyToManyField(Amenity, related_name="property_amenities")

    def __str__(self):
        return f"{self.name}"


class Images(models.Model):
    image = models.CharField(max_length=255, blank=True, default="")
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="property_images", default=""
    )

    def __str__(self):
        return self.image

    class Meta:
        ordering = ["image"]
