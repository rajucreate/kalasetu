from django.urls import path
from .views import login_view, logout_view, register_view, artisan_profile, add_story

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("artisan/<int:pk>/", artisan_profile, name="artisan_profile"),
    path("artisan/story/add/", add_story, name="add_story"),
]