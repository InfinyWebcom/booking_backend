from django.urls import path
from accounts.views import (
    sign_up,
    sign_in,
    sign_out,
    Users,
    password_reset,
    set_reset_password,
    set_password_generated_link,
)

urlpatterns = [
    path("sign-up", sign_up, name="sign-up"),
    path("sign-in", sign_in, name="sign-in"),
    path("sign-out", sign_out, name="sign-out"),
    path("password-reset", password_reset, name="password-reset"),
    path(
        "set-reset-password/<int:temp_code>/<str:email_id>",
        set_reset_password,
        name="set-reset-password",
    ),
    path(
        "set-password-generated-link/<int:temp_code>/<str:email_id>",
        set_password_generated_link,
        name="set-password-generated-link",
    ),
    path("users", Users.as_view(), name="users"),
]
