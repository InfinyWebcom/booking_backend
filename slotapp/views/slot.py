from rest_framework.views import APIView
from rest_framework.response import Response as DjangoRestResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import NotFound
from datetime import datetime, timedelta
from slotapp.models.slot import Slot
from organizations.models.property import Property
from slotapp.serializers.slot_serializer import SlotSerializer

# Create your views here.


def get_daily_slots(start, end, slot, date):
    # combine start time to respective day
    dt = datetime.combine(date, datetime.strptime(start, "%H:%M").time())
    slots = [dt]
    while dt.time() < datetime.strptime(end, "%H:%M").time():
        dt = dt + timedelta(minutes=slot)
        slots.append(dt)

    return slots


def make_slot(value, date_required, property_obj):

    for i in range(len(value)):
        # print(date_required,date_required.strftime("%A"))
        val = int(value[i]["slot_duration"] / 60)
        slot = get_daily_slots(
            start=value[i]["start_time"],
            end=value[i]["end_time"],
            slot=value[i]["slot_duration"],
            date=date_required,
        )

        for data in range(len(slot) - val):
            slot_object, slot_created = Slot.objects.get_or_create(
                date=date_required,
                start_time=slot[data].time(),
                end_time=slot[data + 1].time(),
                property=property_obj,
            )
            # print(slot[data].time(), slot[data + 1].time())


## To make slots to same owner for their all property
def slots(property_obj):
    print("making slot for : ", property_obj)
    property_object = property_obj
    days = {
        "Monday": [
            {"start_time": "00:00", "end_time": "13:00", "slot_duration": 120},
            {"start_time": "15:00", "end_time": "18:00", "slot_duration": 60},
        ],
        "Wednesday": [
            {"start_time": "9:00", "end_time": "18:00", "slot_duration": 120}
        ],
        "Friday": [
            {"start_time": "10:00", "end_time": "13:00", "slot_duration": 120},
            {"start_time": "15:00", "end_time": "19:00", "slot_duration": 60},
        ],
    }

    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    date_required = monday.date()
    # weekely schedule monday to sunday
    week_days = 7
    x = 0

    for day in range(week_days):
        print(date_required, date_required.strftime("%A"))
        # date_required = date_required + timedelta(days=1)
        for key, value in days.items():

            if date_required.strftime("%A") == key:
                make_slot(
                    value=value,
                    date_required=date_required,
                    property_obj=property_object,
                )

        date_required = date_required + timedelta(days=1)


class SlotList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:

            # slot_id = request.GET.get("slot_id")
            # slot_qs = Slot.objects.all().filter(slot_id)

            slot_qs = Slot.objects.all()
            serializer = SlotSerializer(slot_qs, many=True)
            return DjangoRestResponse(
                {"success": "Success", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Slot.DoesNotExist:
            return DjangoRestResponse(
                {
                    "status": "Success",
                    "message": f"selected slot does not exists",
                },
                status=status.HTTP_200_OK,
            )

    def post(self, request, *args, **kwargs):
        print(request.user)
        if request.user is None:
            raise NotFound
        else:
            if request.user.role.name == "Owner" or request.user.role.name == "Admin":
                print("====================", request.user)
                ##for specific property owner can make slots
                try:
                    request.data["property_id"]
                    property_id = request.GET.get("property_id")
                    property_instance = Property.objects.get(pk=property_id)
                    slots(property_obj=property_instance)
                    print(f"DEBUG : {property_instance}")
                except Property.DoesNotExist:
                    return DjangoRestResponse(
                        {
                            "status": "Success",
                            "message": f"Property object does not exists",
                        },
                        status=status.HTTP_200_OK,
                    )
                ##for multiple property owner can make same slots
                """
                property_obj_qs = Property.objects.filter(owner=request.user)
                print(property_obj_qs)
                print("count", property_obj_qs.count())
                for property_obj in property_obj_qs:
                    print(type(property_obj))
                    slots(property_obj=property_obj)
                    print("==========================end for loop")
                """
                return DjangoRestResponse(
                    {
                        "success": "Success",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return DjangoRestResponse(
                    {
                        "status": "Error",
                        "message": "User role cannot be make slot",
                    },
                    status=status.HTTP_200_OK,
                )
