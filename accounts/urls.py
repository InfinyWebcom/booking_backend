from django.urls import path
from accounts.views import sign_up, sign_in, sign_out, Users

urlpatterns = [
    path("sign-up", sign_up, name="sign-up"),
    path("sign-in", sign_in, name="sign-in"),
    path("sign-out", sign_out, name="sign-out"),
    path("users", Users.as_view(), name="users"),
]
