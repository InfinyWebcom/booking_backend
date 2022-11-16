from django.urls import path
from accounts.views import (
    sign_up,
    sign_in,
    sign_out,
    Users,
    password_reset,
    set_reset_password,
    render_test,
)

urlpatterns = [
    path("sign-up", sign_up, name="sign-up"),
    path("sign-in", sign_in, name="sign-in"),
    path("sign-out", sign_out, name="sign-out"),
    path("password-reset", password_reset, name="password-reset"),
    path("set-reset-password", set_reset_password, name="set-reset-password"),
    path("render-test", render_test, name="render-test"),
    path("users", Users.as_view(), name="users"),
]
