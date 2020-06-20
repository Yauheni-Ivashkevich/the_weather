import requests
from django.shortcuts import render
from .models import City
from .forms import CityForm

def index(request):
    appid = '8232076cfb0c3a0a28e2c3f26d07da6d'
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}units=metric&appid=' + appid

    cities = City.objects.all()
    weather_data = []

    if request.method == "POST":
        form = CityForm(request.POST)
        form.save()


    for city in cities:
        city_weather = requests.get(url.format(city.name)).json()
        weather = {
            'city': city.name,
            'temp': city_weather["list"][0]["main"]["temp"],
            'description': city_weather["list"][0]["weather"][0]["description"],
            'icon': city_weather["list"][0]["weather"][0]["icon"],
        }
        weather_data.append(weather)

    context = {'weather_data': weather_data, 'form': CityForm}
    return render(request, 'weather/index.html', context)
