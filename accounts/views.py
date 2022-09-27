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
import smtplib
import pytz
from django.conf import settings


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

        else:
            user_obj = User.objects.all()

        serializer = UserSerializer(user_obj, many=True)
        return DjangoRestResponse(
            {
                "success": "Success",
                "totalcount": (user_obj.count()),
                "users": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # 2. Create
    def post(self, request, *args, **kwargs):

        if request.user.role.name == "Admin":
            email = request.data["email"]
            if User.objects.filter(email=email).exists():
                return DjangoRestResponse(
                    {"status": "Error", "message": f"Email already exists"},
                    status=status.HTTP_200_OK,
                )
            password = request.data["password"]
            username = request.data["username"]

            first_name = request.data["first_name"]
            last_name = request.data["last_name"]
            contact = request.data["contact"]
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
            # print(f"DEBUG : Created user object {new_user}")
            try:
                smtp_gmail = settings.SMTP["EMAIL_HOST"]["SMTP_GMAIL"]
                smtp_port = settings.SMTP["EMAIL_PORT"]
                login_user = settings.LOGIN_USER
                login_pw = settings.LOGIN_PW

                # Create your SMTP session

                smtp = smtplib.SMTP(smtp_gmail, smtp_port)
                # Use TLS to add security
                smtp.starttls()
                # User Authentication
                smtp.login(login_user, login_pw)
                # Defining The Message
                message = "Welcome to Turf"

                # Sending the Email
                smtp.sendmail(login_user, email, message)

                # Terminating the session
                smtp.quit()
                print("Email sent successfully!")

            except Exception as e:
                print("Something went wrong....", e)

            return DjangoRestResponse(
                {"status": "Success", "message": "User added Successfully"},
                status=status.HTTP_201_CREATED,
            )

        else:
            return DjangoRestResponse(
                {
                    "status": "Error",
                    "message": "User/Owner role cannot be add property",
                },
                status=status.HTTP_200_OK,
            )

    def delete(self, request):
        userid_list = request.data["user_id"]
        try:
            for user_id in userid_list:
                user = User.objects.get(pk=user_id).delete()

                print(f"DEBUG: user id: {(user_id)}")
            return DjangoRestResponse(
                {
                    "status": "Sucess",
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
                status=status.HTTP_404_NOT_FOUND,
            )

    def patch(self, request):
        user_id = request.data["user_id"]
        try:
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
    if User.objects.filter(email=email).exists():
        return DjangoRestResponse(
            {"status": "Error", "message": f"Email already exists"},
            status=status.HTTP_200_OK,
        )
    email = request.data["email"]
    password = request.data["password"]
    username = request.data["username"]

    first_name = request.data["first_name"]
    last_name = request.data["last_name"]
    contact = request.data["contact"]

    try:
        role_name = request.data[
            "role_name"
        ]  # i/p should be in this format : Owner/User/Admin
        role_obj = Role.objects.get(name=role_name)
    except Role.DoesNotExist:
        return DjangoRestResponse(
            {
                "status": "Success",
                "message": f"Please provide proper input(User/Owner/Admin) or object does not exists",
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
