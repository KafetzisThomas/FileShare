from django.urls import path
from . import views

app_name = "transfer"
urlpatterns = [
    path("", views.index, name="index"),
]
