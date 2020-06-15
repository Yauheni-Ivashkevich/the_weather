import requests
from django.shortcuts import render
from .models import City
from .forms import CityForm

def index(request):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=8232076cfb0c3a0a28e2c3f26d07da6d'

    if request.method == "POST":
        form = CityForm(request.POST)
        form.save()

    form = CityForm()

    cities = City.objects.all()

    weather_data = []

    for city in cities:
        city_weather = requests.get(url.format(city.name)).json()

        city_weather = {
            'city': city.name,
            'temperature': city_weather["main"]["temp"],
            'description': city_weather["weather"][0]["description"],
            'icon': city_weather["weather"][0]["icon"],
        }
        weather_data.append(city_weather)

    context = {'weather_data': weather_data, 'form': CityForm}
    return render(request, 'weather/index.html', context=context)
