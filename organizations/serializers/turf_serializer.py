from rest_framework import serializers
from organizations.models.turf_category import TurfCategory


class TurfCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TurfCategory
        fields = [
            "id",
            "name",
        ]
