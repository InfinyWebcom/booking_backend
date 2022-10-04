from email.mime import image
from organizations.views.state_city import amenities
from rest_framework.views import APIView
from rest_framework.response import Response as DjangoRestResponse
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from organizations.models.property import Amenity, Property
from organizations.models.turf_category import TurfCategory
from accounts.models import Role, User
from organizations.serializers.property_serializer import (
    PropertySerializer,
    AmenitySerializer,
)
import requests
import base64
import os
import boto3
from organizations.common.aws_client import s3_client, s3_resource
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
import base64
from django.core.files.base import ContentFile
import uuid


# make sure there is no data: image / jpeg; base64 in the string that returns
def get_as_base64(content_b64):

    content_type_list = [
        "data:image/png;base64,",
        "data:image/jpg;base64,",
        "data:image/jpeg;base64,",
    ]
    extension = ["png", "jpg", "jpeg"]
    print("length of images", len(content_b64))
    unified_base64 = []
    unified_ext = []
    for img in content_b64:
        print(img)
        for data, ext in zip(content_type_list, extension):
            if not img.find(data) and img.find(ext):
                im2 = img.replace(data, "")
                unified_ext.append(ext)
        unified_base64.append(im2)

    return unified_base64, unified_ext


def upload_img_s3_bucket(images):

    bucket_name = "turf-booking-2022"
    url_list = []
    unified_base64, unified_ext = get_as_base64(content_b64=images)

    count = 0
    for img, ext in zip(unified_base64, unified_ext):
        # if you want to upload the file to folder use 'Folder Name/FileName.jpeg'
        # where the file will be uploaded,
        file_name_with_extention = f"images_vip/img{count}.{ext}"
        obj = s3_resource.Object(bucket_name, file_name_with_extention)
        obj.put(Body=base64.b64decode(img))
        # get bucket location
        location = s3_client.get_bucket_location(Bucket=bucket_name)[
            "LocationConstraint"
        ]

        object_url = f"https://{bucket_name}.s3.{location}.amazonaws.com/{file_name_with_extention}"
        count += 1
        print(object_url)
        url_list.append(object_url)

    return url_list


class Properties(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Return a list of all users.
        """
        # names = [property.name for property in Property.objects.all()]
        # return DjangoRestResponse(names)

        try:
            if (
                request.GET.get("property_id") != None
                and request.GET.get("property_id") != ""
            ):
                property_id = request.GET.get("property_id")
                property_qs = Property.objects.all().filter(pk=property_id)
                property_instance = Property.objects.get(pk=property_id)
                amenity_obj = property_instance.amenity.all()

                print(f"DEBUG:amenities {amenity_obj}")

            else:

                property_qs = Property.objects.all()

            serializer = PropertySerializer(property_qs, many=True)
            return DjangoRestResponse(
                {
                    "status": "Success",
                    "properties": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Property.DoesNotExist:
            return DjangoRestResponse(
                {
                    "status": "Success",
                    "message": f"Property object does not exists",
                },
                status=status.HTTP_200_OK,
            )

    # 2. Create
    def post(self, request, *args, **kwargs):
        url_list = []
        if request.user.role.name == "Owner" or request.user.role.name == "Admin":
            name = request.data["name"]
            city = request.data["city"]
            state = request.data["state"]
            images = request.data["images"]
            url_list = upload_img_s3_bucket(images=images)
            print(f"list of unified_base64 img : {url_list}")
            latitude = request.data["latitude"]
            longitude = request.data["longitude"]
            is_available = request.data["is_available"]
            rent = request.data["rent"]
            amenities_list = request.data["amenities"]
            for amenity in amenities_list:
                print(amenity)
            print(amenities_list, type(amenities_list))

            try:
                turf_category = request.data[
                    "turf_category"
                ]  # i/p should be:Cricket/Football/Volleyball
                print(turf_category)
                turf_category_obj = TurfCategory.objects.get(name=turf_category)
            except TurfCategory.DoesNotExist:
                return DjangoRestResponse(
                    {
                        "status": "Success",
                        "message": f"Please provide proper input(Cricket/Football/Volleyball) or object does not exists",
                    },
                    status=status.HTTP_200_OK,
                )

            user_obj = User.objects.get(pk=request.user.id)

            property_object, created = Property.objects.get_or_create(
                name=name,
                city=city,
                state=state,
                latitude=latitude,
                longitude=longitude,
                is_available=is_available,
                rent=rent,
                owner=user_obj,
                turf_category=turf_category_obj,
            )

            if created == True:
                for data in amenities_list:
                    amenity_instance = Amenity.objects.get(name=data)
                    property_object.amenity.add(amenity_instance)

                return DjangoRestResponse(
                    {"status": "Success", "message": "Property Added Successfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return DjangoRestResponse(
                    {"status": "Error", "message": "Property already present."},
                    status=status.HTTP_200_OK,
                )
            """
            return DjangoRestResponse(
                {"status": "comming", "message": "ok"},
                status=status.HTTP_200_OK,
            )
            """
        else:
            return DjangoRestResponse(
                {
                    "status": "Error",
                    "message": "User role cannot be add property",
                },
                status=status.HTTP_200_OK,
            )

    def delete(self, request):
        if request.user.role.name == "Owner" or request.user.role.name == "Admin":
            property_id = request.GET.get("property_id")
            print(type(property_id))
            property_id_list = property_id.split(",")
            print(property_id_list)
            print(type(property_id_list))
            try:
                if (
                    request.GET.get("property_id") != None
                    and request.GET.get("property_id") != ""
                ):
                    property_id = request.GET.get("property_id")
                    for property_id in property_id_list:
                        property_instance = Property.objects.get(
                            pk=property_id
                        ).delete()
                    return DjangoRestResponse(
                        {
                            "status": "Success",
                            "message": "Property deleted successfully",
                        },
                        status=status.HTTP_200_OK,
                    )
            except Property.DoesNotExist:

                return DjangoRestResponse(
                    {
                        "status": "Error",
                        "message": "Property not found",
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            return DjangoRestResponse(
                {
                    "status": "Error",
                    "message": "User role cannot be delete property details",
                },
                status=status.HTTP_200_OK,
            )

    def patch(self, request):
        if request.user.role.name == "Owner" or request.user.role.name == "Admin":
            property_id = request.data["property_id"]
            try:
                property_obj = Property.objects.get(id=property_id)
                serializer = PropertySerializer(
                    property_obj, data=request.data, partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return DjangoRestResponse(
                    {
                        "status": "Success",
                        "Users": serializer.data,
                        "message": "Property edit successfully",
                    },
                    status=status.HTTP_202_ACCEPTED,
                )
            except Property.DoesNotExist:
                return DjangoRestResponse(
                    {
                        "status": "Error",
                        "message": "Property does not found",
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )
        else:
            print("Debug", request.auth)
            return DjangoRestResponse(
                {
                    "status": "Error",
                    "message": "User role cannot be edit property details",
                },
                status=status.HTTP_200_OK,
            )
