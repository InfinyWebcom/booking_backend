from pyexpat import model
from rest_framework import serializers
from organizations.models.property import Property, Amenity, Images
from organizations.serializers.turf_serializer import TurfCategorySerializer


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ["id", "name"]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ["id", "property", "image"]


class PropertySerializer(serializers.ModelSerializer):
    turf_category = TurfCategorySerializer(required=True)
    amenity = AmenitySerializer(many=True)
    # images = ImageSerializer(many=True)

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


# class PropertyImageSerializer(serializers.ModelSerializer):
#     property_data = PropertySerializer(required=True, many=True)

#     class Meta:
#         model = Images
#         fields = ["id", "image", "property_data"]
