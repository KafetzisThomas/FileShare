"""Defines URL patterns for fileshare"""

from django.urls import path
from . import views

app_name = "fileshare"
urlpatterns = [
    path("", views.index, name="index"),
]
