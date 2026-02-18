from django.shortcuts import render
import requests
from django.conf import settings
import datetime


def index(request):
    city_weather = None
    forecast_days = []
    error = None

    if request.method == "POST":
        city_name = request.POST.get("city")

        if not city_name:
            error = "من فضلك أدخل اسم المدينة"
            return render(request, "weatherapi.html", {
                "error": error
            })

        api_url = "https://api.weatherapi.com/v1/forecast.json"

        params = {
            "key": settings.WEATHER_API_KEY,
            "q": city_name,
            "days": 3,
            "aqi": "yes",
            "lang": "ar"
        }

        try:
            response = requests.get(api_url, params=params, timeout=10)
            data = response.json()
        except requests.RequestException:
            error = "حدث خطأ أثناء الاتصال بخدمة الطقس"
            return render(request, "weatherapi.html", {"error": error})

        # 🔴 لو فيه خطأ من الـ API
        if data.get("error"):
            error = data["error"]["message"]
            return render(request, "weatherapi.html", {
                "error": error
            })

        location = data.get("location", {})
        current = data.get("current", {})
        forecast = data.get("forecast", {}).get("forecastday", [])

        if not current:
            error = "لا توجد بيانات حالية لهذه المدينة"
            return render(request, "weatherapi.html", {"error": error})

        # -------------------
        # بيانات الطقس الحالي
        # -------------------
        city_weather = {
            # 📍 الموقع
            "city": location.get("name"),
            "region": location.get("region"),
            "country": location.get("country"),
            "localtime": location.get("localtime"),

            # 🌡️ الحرارة
            "temp_c": current.get("temp_c"),
            "feelslike_c": current.get("feelslike_c"),
            "text": current.get("condition", {}).get("text"),
            "icon": current.get("condition", {}).get("icon"),

            # 🌬️ الرياح (أضفتهم لك هنا)
            "wind_kph": current.get("wind_kph"),
            "wind_mph": current.get("wind_mph"),
            "wind_dir": current.get("wind_dir"),
            "wind_degree": current.get("wind_degree"),
            "gust_kph": current.get("gust_kph"),

            # 💧 الرطوبة والسحب
            "humidity": current.get("humidity"),
            "cloud": current.get("cloud"),

            # 🌧️ أمطار وضغط
            "precip_mm": current.get("precip_mm"),
            "pressure_mb": current.get("pressure_mb"),

            # 🔆 إضافي
            "vis_km": current.get("vis_km"),
            "uv": current.get("uv"),
            "last_updated": current.get("last_updated"),
        }

        # -------------------
        # جودة الهواء
        # -------------------
        air_quality = current.get("air_quality")

        if air_quality:
            index = air_quality.get("us-epa-index")
            city_weather["aqi_description"] = get_aqi_description(index)
            city_weather["pm2_5"] = air_quality.get("pm2_5")
            city_weather["pm10"] = air_quality.get("pm10")
            city_weather["co"] = air_quality.get("co")
            city_weather["no2"] = air_quality.get("no2")
            city_weather["o3"] = air_quality.get("o3")
        else:
            city_weather["aqi_description"] = "لا توجد بيانات جودة الهواء"

        # -------------------
        # التوقعات القادمة
        # -------------------
        forecast_days = forecast

        arabic_days = {
            "Monday": "الاثنين",
            "Tuesday": "الثلاثاء",
            "Wednesday": "الأربعاء",
            "Thursday": "الخميس",
            "Friday": "الجمعة",
            "Saturday": "السبت",
            "Sunday": "الأحد",
        }

        for day in forecast_days:
            date_obj = datetime.datetime.strptime(day["date"], "%Y-%m-%d")
            english_day = date_obj.strftime("%A")
            day["day_name"] = arabic_days.get(english_day, english_day)

    return render(request, "weatherapi.html", {
        "city_weather": city_weather,
        "forecast_days": forecast_days,
        "error": error
    })


# -------------------
# وصف جودة الهواء
# -------------------
def get_aqi_description(i):
    descriptions = {
        1: "الهواء نقي تمامًا 🌿",
        2: "جودة الهواء جيدة 👍",
        3: "جودة الهواء متوسطة 😐",
        4: "غير صحي للحساسين ⚠️",
        5: "غير صحي للجميع 😷",
        6: "الهواء خطير جدًا 🚨"
    }
    return descriptions.get(i, "لا توجد بيانات")
