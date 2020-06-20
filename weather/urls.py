from django.urls import path

from .views import WeatherView
from weather.apps import WeatherConfig

app_name = WeatherConfig.label

urlpatterns = [
    path('', WeatherView.as_view(), name="weather"),  #the path for our weather view
]
