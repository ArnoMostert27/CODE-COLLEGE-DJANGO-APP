from django.urls import path

from . import views

urlpatterns = [
    path("", views.deal_list, name="deal_list"),
    path("deals/<int:pk>/", views.deal_detail, name="deal_detail"),
]