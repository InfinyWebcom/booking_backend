from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response as DjangoRestResponse
from rest_framework import status, serializers
from accounts.models import Role, User
from rest_framework.authtoken.models import Token
from accounts.serializers import *
from datetime import datetime
from django.utils import timezone

from organizations.common.email import send_an_email
from django.core.mail import send_mail


def new_user(request):
    email = request.data["email"]
    password = request.data["password"]
    username = request.data["username"]

    first_name = request.data["first_name"]
    last_name = request.data["last_name"]
    contact = request.data["contact"]

    if User.objects.filter(email=email).exists():
        return DjangoRestResponse(
            {"status": "Error", "message": f"Email already exists"},
            status=status.HTTP_200_OK,
        )
    try:
        role_name = request.data[
            "role_name"
        ]  # i/p should be in this format : Owner/User/Admin
        role_obj = Role.objects.get(name=role_name)
    except Role.DoesNotExist:
        return DjangoRestResponse(
            {
                "status": "Success",
                "message": f"please provide proper input(User/Owner/Admin) or object does not exists",
            },
            status=status.HTTP_200_OK,
        )

    print(f"DEBUG: Role object: {(role_obj)}")
    new_user = User.objects.create_user(
        email,
        password,
        first_name=first_name,
        last_name=last_name,
        username=username,
        contact=contact,
        role=role_obj,
        is_signup=True,
    )
    print(f"DEBUG : Created user object {new_user}")

    # Defining The Message
    message = "Welcome to Turf"
    send_an_email(receiver_email=email, message=message)


class PostWelcomeEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class Users(APIView):
    """
    View to list all users in the system.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Return a list of all users.
        """
        # names = [user.name for user in User.objects.all()]
        # return DjangoRestResponse(names)
        if request.GET.get("user_role") != None and request.GET.get("user_role") != "":

            user_role = request.GET.get("user_role")
            user_role_id = Role.objects.get(name=user_role)
            user_obj = User.objects.all().filter(role_id=user_role_id)

        elif request.GET.get("user_id") != None and request.GET.get("user_id") != "":
            print("================coming")
            user_id = request.GET.get("user_id")
            # user_role_id = Role.objects.get(name=user_role)
            # user_obj = User.objects.all().filter(role_id=user_role_id)

            user_obj = User.objects.all().filter(id=user_id)
            print(user_obj)

        else:
            user_obj = User.objects.all()

        serializer = UserSerializer(user_obj, many=True)
        print("serializing==================>", serializer.data)
        return DjangoRestResponse(
            {
                "success": "Success",
                # "totalcount": (user_obj.count()),
                "users": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # 2. Create
    def post(self, request, *args, **kwargs):

        if request.user.role.name == "Admin":
            new_user(request=request)
            return DjangoRestResponse(
                {"status": "Success", "message": "User added Successfully"},
                status=status.HTTP_201_CREATED,
            )

        else:
            return DjangoRestResponse(
                {
                    "status": "Error",
                    "message": "Only admin can add user/owner in the system",
                },
                status=status.HTTP_200_OK,
            )

    def delete(self, request):
        try:
            if request.GET.get("user_id") != None and request.GET.get("user_id") != "":
                user_id = request.GET.get("user_id")
                print(type(user_id))
                user_id_list = user_id.split(",")
                print(user_id_list)
                print(type(user_id_list))
                for user_id in user_id_list:
                    user_instance = User.objects.get(pk=user_id).delete()
                return DjangoRestResponse(
                    {
                        "status": "Success",
                        "message": "User deleted successfully",
                    },
                    status=status.HTTP_200_OK,
                )
        except User.DoesNotExist:

            return DjangoRestResponse(
                {
                    "status": "Error",
                    "message": "User not found",
                },
                status=status.HTTP_200_OK,
            )

    def patch(self, request):
        user_id = request.data["user_id"]
        try:
            # if request.GET.get("user_id") != None and request.GET.get("user_id") != "":
            #     user_id = request.GET.get("user_id")
            # user_role_id = Role.objects.get(name=user_role)
            # user_obj = User.objects.all().filter(role_id=user_role_id)

            user_obj = User.objects.get(id=user_id)
            serializer = UserSerializer(user_obj, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return DjangoRestResponse(
                {
                    "status": "Success",
                    "users": serializer.data,
                    "message": "User edit successfully",
                },
                status=status.HTTP_202_ACCEPTED,
            )
        except User.DoesNotExist:
            return DjangoRestResponse(
                {
                    "status": "Error",
                    "message": "User not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["POST"])
def sign_up(request):
    new_user(request=request)
    return DjangoRestResponse(
        {"status": "Success", "message": "User added successfully"},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def sign_in(request):

    email = request.data["email"]
    password = request.data["password"]
    print(f"DEBUG: user object: {(email)}")

    try:
        user = User.objects.get(email=email)

        if user.check_password(password):
            user.is_signin = True
            user.last_login_time = timezone.now()
            user.save()
            token = Token.objects.get_or_create(user=user)
            print(token[1])
            return DjangoRestResponse(
                {
                    "status": "Success",
                    "message": "Successfully logged in",
                    "tokenkey": f"{token[0]}",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return DjangoRestResponse(
                {"status": "Error", "message": "Password is wrong"},
                status=status.HTTP_200_OK,
            )

    except User.DoesNotExist:

        return DjangoRestResponse(
            {
                "status": "Error",
                "message": f"user with login {email} does not exists",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return DjangoRestResponse(
            {"status": "Error", "message": f"{e}"},
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def sign_out(request):
    try:
        user = User.objects.get(id=request.user.id)
        request.user.auth_token.delete()
        user.is_signin = False
        user.last_logout_time = timezone.now()
        user.save()

    except (AttributeError, User.DoesNotExist):
        pass

    return DjangoRestResponse(
        {"status": "Success", "message": f"Successfully logged out."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def password_reset(request):

    user_email = request.data["user_email"]
    if User.objects.filter(email=user_email).exists():
        message = f"i have forgot your password http://192.168.29.248:8000/accounts/render-test"

        send_an_email(receiver_email=user_email, message=message)

        return DjangoRestResponse(
            {"status": "success", "message": f"Email already exists"},
            status=status.HTTP_200_OK,
        )
    else:
        return DjangoRestResponse(
            {"status": "Success", "message": f" {user_email} doesn't exist"},
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
def set_reset_password(request):
    user_email = request.data["user_email"]
    user_password = request.data["user_password"]
    user_object = User.objects.get(email=user_email)
    user_object.set_password(user_password)
    user_object.save()

    print(user_object)

    return DjangoRestResponse(
        {
            "status": "Success",
            "message": f" {user_email} Successfully password updated ",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def render_test(request):

    return render(
        request=request,
        template_name="password_reset.html",
        context={"password_reset_form": "password_reset_form"},
    )
