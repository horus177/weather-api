from django.shortcuts import render
import requests
from django.conf import settings


def index(request):
    city_weather = {}
    error = None

    if request.method == 'POST':
        city_name = request.POST.get('city')

        api_url = 'https://api.weatherapi.com/v1/current.json'
        params = {
            "q": city_name,
            "key": settings.WEATHER_API_KEY,
            "aqi": "yes",
            "lang": "ar"
        }

        response = requests.get(api_url, params=params)
        data = response.json()

        # ✅ لو في خطأ من الـ API (مدينة مش موجودة)
        if "error" in data:
            error = "❌ المدينة غير موجودة، تأكد من الكتابة بشكل صحيح"
        else:
            city_weather = {
                # 📍 بيانات الموقع
                'city': data["location"]["name"],
                'region': data["location"]["region"],
                'country': data["location"]["country"],
                'lat': data["location"]["lat"],
                'lon': data["location"]["lon"],
                'tz_id': data["location"]["tz_id"],
                'localtime': data["location"]["localtime"],

                # 🌡️ بيانات الطقس
                'temp_c': data["current"]["temp_c"],
                'temp_f': data["current"]["temp_f"],
                'feelslike_c': data["current"]["feelslike_c"],
                'feelslike_f': data["current"]["feelslike_f"],

                # 🌥️ حالة الطقس
                'text': data["current"]["condition"]["text"],
                'icon': data["current"]["condition"]["icon"],
                'code': data["current"]["condition"]["code"],

                # 💧 الرطوبة والسحب
                'humidity': data["current"]["humidity"],
                'cloud': data["current"]["cloud"],

                # 🌧️ الأمطار والضغط
                'precip_mm': data["current"]["precip_mm"],
                'pressure_mb': data["current"]["pressure_mb"],

                # 👁️ الرؤية و UV
                'vis_km': data["current"]["vis_km"],
                'uv': data["current"]["uv"],

                # 🕒 آخر تحديث
                'last_updated': data["current"]["last_updated"],

                # 🌫️ جودة الهواء
                'co': data["current"]["air_quality"]["co"],
                'no2': data["current"]["air_quality"]["no2"],
                'o3': data["current"]["air_quality"]["o3"],
                'pm2_5': data["current"]["air_quality"]["pm2_5"],
                'pm10': data["current"]["air_quality"]["pm10"],
            }

            # مؤشر جودة الهواء
            aqi = data["current"]["air_quality"]
            index = aqi["us-epa-index"]
            city_weather["aqi_description"] = get_aqi_description(index)

    return render(request, 'weatherapi.html', {
        'city_weather': city_weather,
        'error': error
    })


def get_aqi_description(i):
    descriptions = {
        1: "الهواء نقي تمامًا ومناسب لكل الناس بدون أي مخاطر 🌿",
        2: "جودة الهواء جيدة ولا توجد مخاطر تُذكر على الصحة 👍",
        3: "جودة الهواء متوسطة، يُفضل تقليل المجهود الخارجي لمرضى الحساسية 😐",
        4: "الهواء غير صحي للحساسين ومرضى الصدر، يُفضل تقليل الخروج ⚠️",
        5: "الهواء غير صحي للجميع، يُنصح بالبقاء في أماكن مغلقة 😷",
        6: "الهواء خطير جدًا على الصحة، تجنب الخروج تمامًا 🚫"
    }
    return descriptions.get(i, "لا توجد بيانات متاحة")
