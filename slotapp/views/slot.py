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
        "Saturday": [
            {"start_time": "00:00", "end_time": "13:00", "slot_duration": 120},
            {"start_time": "15:00", "end_time": "18:00", "slot_duration": 60},
        ],
        "Sunday": [{"start_time": "9:00", "end_time": "18:00", "slot_duration": 120}],
        "Tuesday": [
            {"start_time": "10:00", "end_time": "13:00", "slot_duration": 120},
            {"start_time": "15:00", "end_time": "19:00", "slot_duration": 60},
        ],
    }

    now = datetime.now()
    # monday = now - timedelta(days=now.weekday())
    # date_required = monday.date()
    date_required = now.date()
    # weekely schedule monday to sunday
    week_days = 5
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


def transform_slot_data(date, day):
    day_list = []
    slot_qs = Slot.objects.all().filter(date=date)
    slot_qs = slot_qs.values_list(
        "date", "start_time", "end_time", "is_available", "booking"
    )

    for data in slot_qs:
        if data[0] == date:
            obj = {
                "date": data[0].strftime("%m/%d/%Y"),
                "start_time": data[1].strftime("%X"),
                "end_time": data[2].strftime("%X"),
                "is_available": data[3],
                "booking": data[4],
            }
            day_list.append(obj)
            # print(data[0], data[1], data[2], data[3])

    return day_list


class SlotList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        slot = {}
        try:
            if (
                request.GET.get("property_id") != None
                and request.GET.get("property_id") != ""
            ):
                property_id = request.GET.get("property_id")
                slot_qs = Slot.objects.all().filter(property=property_id)

            else:
                # slot_qs = Slot.objects.all()
                slot_qs = Slot.objects.order_by("date").distinct("date")
                date = slot_qs.values_list("date")

                for i in date:

                    day_list = transform_slot_data(date=i[0], day=i[0].strftime("%A"))
                    slot[i[0].strftime("%A")] = day_list

            print(slot)
            # serializer = SlotSerializer(slot_qs, many=True)
            return DjangoRestResponse(
                {"success": "Success", "Slot": slot},
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

                ##for specific property owner can make slots
                try:

                    property_id = request.data["property_id"]
                    property_instance = Property.objects.get(pk=property_id)
                    print(f"DEBUG : {property_instance.id}")
                    slots(property_obj=property_instance)

                except Property.DoesNotExist:
                    return DjangoRestResponse(
                        {
                            "status": "Success",
                            "message": f"Property object does not exists",
                        },
                        status=status.HTTP_200_OK,
                    )

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
