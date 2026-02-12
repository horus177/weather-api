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

        api_url = "https://api.weatherapi.com/v1/forecast.json"

        params = {
            "key": settings.WEATHER_API_KEY,
            "q": city_name,
            "days": 3,          # هنجيب 4 علشان نشيل اليوم الحالي
            "aqi": "yes",
            "lang": "ar"
        }

        response = requests.get(api_url, params=params)
        data = response.json()

        # 🔴 لو فيه error من الـ API
        if data.get("error"):
            error = data["error"]["message"]
            return render(request, "weatherapi.html", {
                "error": error,
                "city_weather": None,
                "forecast_days": []
            })

        # 🟢 هنا متأكدين إن البيانات سليمة
        location = data.get("location", {})
        current = data.get("current", {})
        forecast = data.get("forecast", {}).get("forecastday", [])

        if not current:
            error = "لا توجد بيانات حالية لهذه المدينة"
            return render(request, "weatherapi.html", {
                "error": error,
                "city_weather": None,
                "forecast_days": []
            })

        # -------------------
        # بيانات الطقس الحالي
        # -------------------
        city_weather = {
            "city": location.get("name"),
            "region": location.get("region"),
            "country": location.get("country"),
            "lat": location.get("lat"),
            "lon": location.get("lon"),
            "tz_id": location.get("tz_id"),
            "localtime": location.get("localtime"),

            "temp_c": current.get("temp_c"),
            "feelslike_c": current.get("feelslike_c"),
            "text": current.get("condition", {}).get("text"),
            "icon": current.get("condition", {}).get("icon"),
            "humidity": current.get("humidity"),
            "vis_km": current.get("vis_km"),
            "pressure_mb": current.get("pressure_mb"),
            "uv": current.get("uv"),
            "last_updated": current.get("last_updated"),
            "cloud": current.get("cloud"),
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
        # الثلاث أيام القادمة فقط (بدون اليوم الحالي)
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
# دالة وصف جودة الهواء
# -------------------
def get_aqi_description(i):
    descriptions = {
         1: "الهواء نقي تمامًا ومناسب لكل الناس بدون أي مخاطر 🌿",
        2: "جودة الهواء جيدة ولا توجد مخاطر تُذكر على الصحة 👍",
        3: "جودة الهواء متوسطة، يُفضل تقليل المجهود الخارجي لمرضى الحساسية 😐",
        4: "الهواء غير صحي للحساسين ومرضى الصدر، يُفضل تقليل الخروج ⚠️",
        5: "الهواء غير صحي للجميع، يُنصح بالبقاء في أماكن مغلقة 😷",
        6: "الهواء خطير جدًا على الصحة، تجنب الخروج تم"
    }    
    return descriptions.get(i, "لا توجد بيانات")
