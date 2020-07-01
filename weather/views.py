import json
from datetime import datetime

import pytz
import requests
from django.views.generic import FormView

from .forms import CityForm
from .models import City


class WeatherView(FormView):
    form_class = CityForm
    success_url = 'weather/index.html'
    template_name = 'weather/index.html'
    appid = '8232076cfb0c3a0a28e2c3f26d07da6d'
    default_city = "Minsk"

    def form_valid(self, form):
        print(">>> form_valid")
        city_name = form.cleaned_data["name"]
        self.save_city(city_name)
        self.collect_weather(city_name)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        print(">>> get_context_data")
        ctx = super().get_context_data(**kwargs)
        ctx["weather"] = self.get_weather()
        return ctx

    def get_weather(self):
        city = self.get_city()
        weather = self.get_weather_from_db(city)
        if not weather:
            weather = self.get_weather_from_api(city)
            if weather:
                self.save_weather(city, weather)
        return weather

    def get_city(self) -> str:
        city = self.request.session.get('city')
        return city or self.default_city

    def save_city(self, city: str) -> None:
        if not city:
            return

        self.request.session['city'] = city

    def get_weather_from_api(self, city_name: str) -> dict:
        print(">>> get_weather_from_api")
        url = \
            f'http://api.openweathermap.org' \
            f'/data' \
            f'/2.5' \
            f'/weather' \
            f'?q={city_name}' \
            f'&units=metric' \
            f'&appid={self.appid}'

        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"ERROR: no weather for {city_name}: {resp}")
            return {}

        payload = resp.json()

        try:
            weather = payload["weather"][0]

            return {
                "icon": weather["icon"],
                "city": city_name,
                "temp": payload["main"]["temp"],
                "description": weather["description"],
            }
        except (KeyError, IndexError):
            import traceback
            traceback.print_exc()

            return {}

    @staticmethod
    def get_weather_from_db(city_name: str) -> dict:
        print(">>> get_weather_from_db")
        if not city_name:
            return {}

        city = City.objects.filter(name=city_name).first()
        if not city:
            print(f"WARNING: no city {city_name} in database")
            return {}

        # if not city.last_sync:
        #     print(f"WARNING: city {city_name} was not synchronized")
        #     return {}

        atm = datetime.utcnow().replace(tzinfo=pytz.UTC)
        lsy = city.last_sync
        delta = (atm - lsy)
        if delta.total_seconds() >= 60 * 60:
            print(f"WARNING: city {city_name} weather is expired")
            return {}

        raw_weather = city.weather
        if not raw_weather:
            print(f"WARNING: city {city_name} has no weather in database")
            return {}

        weather = json.loads(city.weather)
        return weather

    @staticmethod
    def save_weather(city_name: str, weather: dict) -> None:
        print(">>> save_weather")
        if not all([city_name, weather]):
            return
        weather_text = json.dumps(weather)
        city, _created = City.objects.get_or_create(name=city_name)
        city.weather = weather_text
        city.last_sync = datetime.now()
        city.save()

    def collect_weather(self, city: str) -> None:
        print(">>> collect_weather")
        weather = self.get_weather_from_api(city)
        if not weather:
            return
        self.save_weather(city, weather)

# import requests
# from django.shortcuts import render
# from .models import City
# from .forms import CityForm
#
# def index(request):
#     appid = '8232076cfb0c3a0a28e2c3f26d07da6d'
#     url = 'http://api.openweathermap.org/data/2.5/weather?q={}units=metric&appid=' + appid
#
#     cities = City.objects.all()
#     weather_data = []
#
#     if request.method == "POST":
#         form = CityForm(request.POST)
#         form.save()
#
#
#     for city in cities:
#         city_weather = requests.get(url.format(city.name)).json()
#         weather = {
#             'city': city.name,
#             'temp': city_weather["list"][0]["main"]["temp"],
#             'description': city_weather["list"][0]["weather"][0]["description"],
#             'icon': city_weather["list"][0]["weather"][0]["icon"],
#         }
#         weather_data.append(weather)
#
#     context = {'weather_data': weather_data, 'form': CityForm}
#     return render(request, 'weather/index.html', context)