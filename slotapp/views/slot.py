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
    print("get daily slot=============getdailyslot")
    print("start======================end", start, end, date)
    dt = datetime.combine(date, datetime.strptime(start, "%H:%M").time())
    slots = [dt]
    while dt.time() < datetime.strptime(end, "%H:%M").time():
        dt = dt + timedelta(minutes=slot)
        slots.append(dt)

    return slots


def make_slot(value, date_required, property_obj):
    # print("coming here==================================")

    for i in range(len(value)):
        print(date_required, date_required.strftime("%A"))
        slot_duration = int(value[i]["slot_duration"])
        val = int((slot_duration) / 60)

        # logic
        # convert time string to datetime
        start1 = datetime.strptime(
            value[i]["start_time"], "%H:%M"
        )  # value[i]["start_time"]
        print("Start time:", start1.time())
        end1 = datetime.strptime(value[i]["end_time"], "%H:%M")  # value[i]["end_time"]

        print("End time:", end1.time())
        slot_duration1 = int((slot_duration) / 60)

        # get difference
        delta = end1 - start1
        str_delta = str(delta)
        total_hrs = datetime.strptime(str_delta, "%H:%M:%S")
        left_hrs = total_hrs.hour % slot_duration1
        print("################left_hrs", left_hrs)
        # conversion
        if left_hrs == 0:
            slot = get_daily_slots(
                start=value[i]["start_time"],
                end=value[i]["end_time"],
                slot=slot_duration,
                date=date_required,
            )
        else:
            # reduce by remainder
            updated_end_time = end1.hour - left_hrs
            updated_end_time_fmt = f"{updated_end_time}:00"
            slot = get_daily_slots(
                start=value[i]["start_time"],
                end=updated_end_time_fmt,
                slot=slot_duration,
                date=date_required,
            )
            # print("+++++++++++++", updated_end_time_fmt)
            # print("else executed")

        # print(
        #     "--------------------------------------------->",
        #     start1,
        #     d,
        #     slot_duration1,
        # )
        print(f"Debug:Slots{type(slot)}")
        print("????????????????TIME??????????????????????")
        for data in range(len(slot) - 1):
            print(slot[data].time(), slot[data + 1].time())
            slot_object, slot_created = Slot.objects.get_or_create(
                date=date_required,
                start_time=slot[data].time(),
                end_time=slot[data + 1].time(),
                property=property_obj,
            )
            # for data in range(len(slot) - val):
            # for sl in slot:
            #     print(sl)
            # slot_object, slot_created = Slot.objects.get_or_create(
            #     date=date_required,
            #     start_time=slot[data].time(),
            #     end_time=slot[data + 1].time(),
            #     property=property_obj,
            # )
        # print(slot[data].time(), slot[data + 1].time())
        print("????????????????TIME??????????????????????")
    print("==================finish=================", date_required.strftime("%A"))


## To make slots to same owner for their all property
def slots(property_obj, days):
    print("making slot for : ", property_obj)
    property_object = property_obj
    # days = {
    #     "Saturday": [
    #         {"start_time": "00:00", "end_time": "13:00", "slot_duration": "120"},
    #         {"start_time": "15:00", "end_time": "18:00", "slot_duration": "60"},
    #     ],
    #     "Sunday": [{"start_time": "9:00", "end_time": "18:00", "slot_duration": "120"}],
    #     "Tuesday": [
    #         {"start_time": "10:00", "end_time": "13:00", "slot_duration": "120"},
    #         {"start_time": "15:00", "end_time": "19:00", "slot_duration": "60"},
    #     ],
    # }

    now = datetime.now()
    # monday = now - timedelta(days=now.weekday())
    # date_required = monday.date()
    date_required = now.date()
    # weekely schedule monday to sunday
    week_days = 7
    x = 0

    for day in range(week_days):
        # print(date_required, date_required.strftime("%A"))
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
        "date", "start_time", "end_time", "is_available", "property", "booking", "id"
    )
    print(slot_qs)
    for data in slot_qs:
        if data[0] == date:
            obj = {
                "date": data[0].strftime("%m/%d/%Y"),
                "start_time": data[1].strftime("%X"),
                "end_time": data[2].strftime("%X"),
                "is_available": data[3],
                "property": data[4],
                "booking_id": data[5],
                "slot_id": data[6],
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
                # slot_qs = Slot.objects.all().filter(property=property_id)

                # else:
                # slot_qs = Slot.objects.all()
                slot_qs = (
                    Slot.objects.all()
                    .filter(property=property_id)
                    .order_by("date")
                    .distinct("date")
                )
                date = slot_qs.values_list("date")

                for i in date:

                    day_list = transform_slot_data(date=i[0], day=i[0].strftime("%A"))
                    slot[i[0].strftime("%A")] = day_list

            print(slot)
            # serializer = SlotSerializer(slot_qs, many=True)
            return DjangoRestResponse(
                {"success": "Success", "slot": slot},
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
                    days = request.data
                    # print(("=====================", days))
                    # print(("=====================", type(days)))
                    property_id = request.data["property_id"]
                    property_instance = Property.objects.get(pk=property_id)
                    print(f"DEBUG : {property_instance.id}")
                    slots(property_obj=property_instance, days=days)

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
