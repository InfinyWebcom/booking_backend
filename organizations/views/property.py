from organizations.views.state_city import amenities
from rest_framework.views import APIView
from rest_framework.response import Response as DjangoRestResponse
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from organizations.models.property import Amenity, Property, Images
from organizations.models.turf_category import TurfCategory
from accounts.models import Role, User
from organizations.serializers.property_serializer import (
    PropertySerializer,
    ImageSerializer,
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
from datetime import datetime

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


def upload_img_s3_bucket(images, property_id):

    bucket_name = "turf-booking-2022"
    url_list = []
    unified_base64, unified_ext = get_as_base64(content_b64=images)
    dt = datetime.now()
    HH = int(dt.strftime("%H"))
    MM = int(dt.strftime("%M"))
    SS = int(dt.strftime("%S"))
    img_datettime = f"{dt.year}{dt.month}{dt.day}{HH}{MM}{SS}"
    count = 0
    for img, ext in zip(unified_base64, unified_ext):
        # if you want to upload the file to folder use 'Folder Name/FileName.jpeg'
        # where the file will be uploaded,
        file_name_with_extention = (
            f"images_vip/property_id-{property_id}/IMG-{count}-{img_datettime}.{ext}"
        )
        obj = s3_resource.Object(bucket_name, file_name_with_extention)
        obj.put(Body=base64.b64decode(img))

        # Grant public read access to S3 objects
        """
            This function adds ACL policy for object in S3 bucket.
            :return: None
        """
        object_key = file_name_with_extention
        response = s3_client.put_object_acl(
            ACL="public-read", Bucket=bucket_name, Key=object_key
        )
        print("permission ==================================", response)

        # get bucket location
        location = s3_client.get_bucket_location(Bucket=bucket_name)[
            "LocationConstraint"
        ]

        object_url = f"https://{bucket_name}.s3.{location}.amazonaws.com/{file_name_with_extention}"
        count += 1
        print(object_url)
        url_list.append(object_url)

    return url_list


def delete_all_images_from_s3_folder(property_id):
    """
    This function deletes all images in a folder from S3 bucket
    :return: None
    """
    bucket_name = "turf-booking-2022"
    file_name = f"images_vip/property_id-{property_id}/"
    # First we list all files in folder
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=file_name)
    image_files_in_folder = response["Contents"]

    files_to_delete = []
    # We will create Key array to pass to delete_objects function
    for image in image_files_in_folder:
        files_to_delete.append({"Key": image["Key"]})
    print("++++++++image++++++++++++")
    for file in files_to_delete:
        print(file)
    print("++++++++image++++++++++++")
    # This will delete all files in a folder
    response = s3_client.delete_objects(
        Bucket=bucket_name, Delete={"Objects": files_to_delete}
    )
    # print(
    #     f"Debug:========image deleteing from aws for propertyid-{property_id}-{response}"
    # )


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

                # property_instance = Property.objects.get(pk=property_id)
                # amenity_obj = property_instance.amenity.all()

                # print(f"DEBUG:amenities {amenity_obj}")
                images_qs = Images.objects.all().filter(property=property_id)
                print(f"DEBUG:images {images_qs}")
            else:

                property_qs = Property.objects.all()
                images_qs = Images.objects.all()

            serializer = PropertySerializer(property_qs, many=True)
            ImgSerializer = ImageSerializer(images_qs, many=True)
            return DjangoRestResponse(
                {
                    "status": "Success",
                    "properties": serializer.data,
                    "properties_image": ImgSerializer.data,
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
            url_list = upload_img_s3_bucket(
                images=images, property_id=property_object.id
            )
            print(f"list of unified_base64 img : {url_list}")
            if created == True:
                for data in amenities_list:
                    amenity_instance = Amenity.objects.get(name=data)
                    property_object.amenity.add(amenity_instance)
                for url in url_list:
                    Img_obj = Images.objects.create(image=url, property=property_object)
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
            try:
                if (
                    request.GET.get("property_id") != None
                    and request.GET.get("property_id") != ""
                ):
                    property_id = request.GET.get("property_id")
                    print(type(property_id))
                    property_id_list = property_id.split(",")
                    print(property_id_list)
                    print(type(property_id_list))
                    for prop_id in property_id_list:
                        property_instance = Property.objects.get(pk=prop_id).delete()

                    delete_all_images_from_s3_folder(property_id=property_id)

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

            try:
                data_to_be_updated = request.data
                print(data_to_be_updated)
                property_object = Property.objects.get(
                    pk=data_to_be_updated["property_id"]
                )
                print(f"DEBUG:Property Object : {property_object}")
                try:
                    turf_category_instance = TurfCategory.objects.get(
                        name=data_to_be_updated["turf_category"]
                    )
                    print(
                        f"DEBUG Turf Category Instance :{type(turf_category_instance)}"
                    )
                except TurfCategory.DoesNotExist:
                    return DjangoRestResponse(
                        {
                            "status": "Success",
                            "message": f"Please provide proper input(Cricket/Football/Volleyball) or object does not exists",
                        },
                        status=status.HTTP_200_OK,
                    )

                property_instance = Property.objects.filter(
                    pk=data_to_be_updated["property_id"]
                ).update(
                    name=data_to_be_updated["name"],
                    city=data_to_be_updated["city"],
                    state=data_to_be_updated["state"],
                    latitude=data_to_be_updated["latitude"],
                    longitude=data_to_be_updated["longitude"],
                    is_available=data_to_be_updated["is_available"],
                    rent=data_to_be_updated["rent"],
                    turf_category=turf_category_instance,
                )
                print("=================>", property_instance)
                for data in data_to_be_updated["amenities"]:
                    amenity_instance = Amenity.objects.get(name=data)
                    amenity_instance.property_amenities.all()
                    print(f"DEBUG : Amenities Instance {amenity_instance}")

                return DjangoRestResponse(
                    {
                        "status": "Success",
                        # "Users": serializer.data,
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
