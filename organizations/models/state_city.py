from django.db import models


class State(models.Model):
    name = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class City(models.Model):
    name = models.CharField(max_length=256, blank=True)
    latitude = models.FloatField(default=20.5937)
    longitude = models.FloatField(default=78.9629)
    state = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        related_name="cities",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
