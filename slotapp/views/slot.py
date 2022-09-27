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


## To make slots to same owner for their all property
def make_slots(property_obj):
    print("making slot for : ", property_obj)
    # Some Dummy values
    # day time
    start_time = "6:00"
    end_time = "23:00"

    slot_time = 60
    days = 5
    x = 0

    # weekely schedule monday to friday
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    date_required = monday.date()
    for i in range(days):
        if i == 0:
            slot = get_daily_slots(
                start=start_time,
                end=end_time,
                slot=slot_time,
                date=date_required,
            )
        else:
            date_required = date_required + timedelta(days=1)
            slot = get_daily_slots(
                start=start_time,
                end=end_time,
                slot=slot_time,
                date=date_required,
            )

        for data in range(len(slot) - 1):
            x += 1
            slot_object, slot_created = Slot.objects.get_or_create(
                date=date_required,
                start_time=slot[data].time(),
                end_time=slot[data + 1].time(),
                property=property_obj,
            )
            # print(slot[data].time(), slot[data + 1].time())

    print(type(slot))
    print(len(slot))
    print(x)  # 17*5


class SlotList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:

            slot_id = request.GET.get("slot_id")
            slot_qs = Slot.objects.all().filter(slot_id)
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
                property_obj_qs = Property.objects.filter(owner=request.user)
                print(property_obj_qs)
                print("count", property_obj_qs.count())
                for property_obj in property_obj_qs:
                    print(type(property_obj))
                    make_slots(property_obj=property_obj)
                    print("==========================end for loop")
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
