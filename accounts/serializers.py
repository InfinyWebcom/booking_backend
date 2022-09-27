from rest_framework import serializers
from accounts.models import User, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):

    role = RoleSerializer(required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "contact",
            "email",
            "email_token",
            "password",
            "booking_status",
            "role",
            "is_signup",
            "is_signin",
            "last_login_time",
            "last_logout_time",
        ]
