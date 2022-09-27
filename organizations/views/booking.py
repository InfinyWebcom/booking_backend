from rest_framework.views import APIView
from rest_framework.response import Response as DjangoRestResponse
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from organizations.models.property import Property

from organizations.models.transactions import Transaction
from organizations.models.booking import Booking as BookingDetails
from organizations.serializers.booking_serializer import BookingSerializer
from accounts.models import User

from rest_framework.exceptions import ParseError
from slotapp.models.slot import Slot


class Booking(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Return a list of all booking.
        """
        booking_qs = BookingDetails.objects.all()
        serializer = BookingSerializer(booking_qs, many=True)
        return DjangoRestResponse(
            {"success": "Success", "booking": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        if request.user.role.name == "User" or request.user.role.name == "Admin":

            user_instance = request.user

            print(f"{user_instance}")
            # step 1: user will see the all available property into dbs
            # step 2: user will select property as per his choice
            # step 3: once he are done with this process we will get property_id,property_rent
            property_id = request.data["property_id"]
            property_obj = Property.objects.get(pk=property_id)

            # step 4: here user can see all available slot as per property_id
            available_slot_as_per_given_property_id = Slot.objects.filter(
                property=property_obj
            )

            # step 5: now user will select  available slot at the movement as per his choice (slot2,slot2 for selected using property_id)

            for available_slot in available_slot_as_per_given_property_id:
                if available_slot.is_available == True:
                    print("avilable slots", available_slot)
                else:
                    print("not available u can select available slots", available_slot)

            slot_id_list = request.data["slot_id"]
            print(f"Selected slot id list{slot_id_list}")

            # step 6 :he will select payment option
            payment_mode = request.data["payment_mode"]
            # step 7 :calculating rent/hrs
            total_amount = property_obj.rent * len(slot_id_list)
            print("Total amount : ", total_amount)

            paying_amt = request.data["payment_amt"]
            print("Paying amount : ", paying_amt)
            print(property_obj, "for this property")

            if payment_mode == "ONLINE":
                user_obj = User.objects.get(email=request.user)
                print("wallet", user_obj.wallet)
                if user_obj.wallet != 0 and user_obj.wallet > total_amount:
                    balance_amount = user_obj.wallet - total_amount
                    user_obj.wallet = balance_amount
                    user_obj.save()
                    print("after paying online wallet", user_obj.wallet)
                elif user_obj.wallet != 0 and user_obj.wallet < total_amount:
                    return DjangoRestResponse(
                        {
                            "status": "success",
                            "message": " wallet doen't have enough amount to pay",
                        },
                        status=status.HTTP_200_OK,
                    )

            bookingDetails_tuple, created = BookingDetails.objects.get_or_create(
                payment_mode=payment_mode,
                user=user_instance,
                isBooked=True,
                booking_amount=total_amount,
            )
            if created == True:

                # step 9 : make an entry in slot table as False
                for slot_id in slot_id_list:
                    selected_slot_id = Slot.objects.get(pk=slot_id)
                    selected_slot_id.is_available = False
                    selected_slot_id.booking = bookingDetails_tuple
                    selected_slot_id.save()

            elif (request.data["cancel"]) == "cancel":

                for slot_id in slot_id_list:
                    selected_slot_id = Slot.objects.get(pk=slot_id)
                    selected_slot_id.is_available = True
                    selected_slot_id.save()

                bookingDetails_tuple.isBooked = False
                bookingDetails_tuple.save()
                return DjangoRestResponse(
                    {
                        "status": "sucess",
                        "message": "booking cancelled ",
                    },
                    status=status.HTTP_201_CREATED,
                )

            if bookingDetails_tuple.isBooked == True:
                Transaction.objects.get_or_create(
                    rent_amount=total_amount,
                    transaction_status=True,
                    user=user_instance,
                    booking=bookingDetails_tuple,
                )
                return DjangoRestResponse(
                    {
                        "status": "sucess",
                        "message": "Transaction done successfully",
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return DjangoRestResponse(
                    {
                        "status": "error",
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            print("Debug", request.auth)
            return DjangoRestResponse(
                {
                    "status": "Error",
                    "message": " Role cannot be booked turf",
                },
                status=status.HTTP_200_OK,
            )
