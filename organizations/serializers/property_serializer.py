from rest_framework import serializers
from organizations.models.property import Property, Amenity
from organizations.serializers.turf_serializer import TurfCategorySerializer


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ["id", "name"]


class PropertySerializer(serializers.ModelSerializer):
    turf_category = TurfCategorySerializer(required=True)
    amenity = AmenitySerializer(many=True)

    class Meta:
        model = Property
        fields = [
            "id",
            "name",
            "city",
            "state",
            "latitude",
            "longitude",
            "is_available",
            "rent",
            "owner",
            "turf_category",
            "amenity",
        ]
