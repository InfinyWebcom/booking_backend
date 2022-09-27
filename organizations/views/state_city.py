from rest_framework.views import APIView
from rest_framework.response import Response as DjangoRestResponse
from rest_framework import authentication, permissions
from rest_framework import status
from rest_framework.exceptions import ParseError
from organizations.models.state_city import City, State
from organizations.serializers.state_city_serializer import (
    CitySerializer,
    StateSerializer,
)
from organizations.models.property import Amenity
from organizations.serializers.property_serializer import AmenitySerializer
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)


@api_view(["GET"])
def state(request):
    # df = pd.read_json("organizations/static/json_data/in.json")
    # data_dict = df.to_dict("records")
    # print(type(data_dict))
    # for data in data_dict:
    #     print(type(data))
    #     print(data["state"])
    #     State.objects.get_or_create(name=data["state"])

    state_obj = State.objects.all()
    serializer = StateSerializer(state_obj, many=True)
    return DjangoRestResponse(
        {
            "status": "success",
            "totalcount": (state_obj.count()),
            "States": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def city(request):
    # df = pd.read_json("organizations/static/json_data/in.json")
    # data_dict = df.to_dict("records")
    # print(type(data_dict))
    # for data in data_dict:
    #     print(type(data))
    #     print(data["state"])
    #     state_obj = State.objects.get(name=data["state"])
    #     City.objects.get_or_create(
    #         name=data["city"],
    #         state=state_obj,
    #         latitude=data["lat"],
    #         longitude=data["lng"],
    #     )

    city_obj = City.objects.all()
    serializer = CitySerializer(city_obj, many=True)
    return DjangoRestResponse(
        {
            "status": "success",
            "totalcount": (city_obj.count()),
            "city": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def city_by_state(request):
    if request.GET.get("state_name") != None and request.GET.get("state_name") != "":
        state_name = request.GET.get("state_name")
        state_obj = State.objects.all().get(name=state_name)
        citybystate_obj = City.objects.all().filter(state=state_obj.id)
        serializer = CitySerializer(citybystate_obj, many=True)

        print(state_obj.id)
        return DjangoRestResponse(
            {
                "status": "success",
                "totalcount": (citybystate_obj.count()),
                "city": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
def amenities(request):

    amenity_obj = Amenity.objects.all()
    serializer = AmenitySerializer(amenity_obj, many=True)
    return DjangoRestResponse(
        {
            "status": "success",
            "totalcount": (amenity_obj.count()),
            "amenity": serializer.data,
        },
        status=status.HTTP_200_OK,
    )
