from urllib import request
from rest_framework.views import APIView
from rest_framework.response import Response as DjangoRestResponse
from rest_framework import authentication, permissions
from rest_framework import status
from rest_framework.decorators import (
    api_view,
)
from organizations.models.property import Property
from organizations.models.booking import Booking as BookingDetails
from accounts.models import User


@api_view(["GET"])
def get_statistics(request):
    print(BookingDetails.objects.all().count())

    return DjangoRestResponse(
        {
            "status": "Success",
            "totalproperties": f"{Property.objects.all().count()}",
            "totalowner": f"{User.objects.all().filter(role=2).count()}",
            "totaluser": f"{User.objects.all().filter(role=3).count()}",
            "totalbooking": f"{BookingDetails.objects.all().count()}",
        },
        status=status.HTTP_200_OK,
    )
