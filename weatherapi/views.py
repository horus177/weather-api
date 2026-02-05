from django.shortcuts import render
import requests
from django.conf import settings
# Create your views here.

def index(request):
    city_weather={}
    error=None
    

    if request.method=='POST':
        city_name=request.POST.get('city')
        api_url=f'https://api.weatherapi.com/v1/current.json?&q={city_name}&'
        url=api_url+city_name
        
        params = {"aqi": "yes","lang": "ar","key": settings.WEATHER_API_KEY,}
    
    
       # 👈 يخلي الوصف بالعربي


        respons=requests.get(url,params=params)
        data=respons.json()
        if respons.status_code==200:
            city_weather={
             #بيانات الموقع   
                'city':city_name,
                'region':data["location"]["region"],
                'country':data["location"]["country"],
                'lat':data["location"]["lat"],
                'lon':data["location"]["lon"],
                'tz_id':data["location"]["tz_id"],
                'localtime':data["location"]["localtime"],

                #بيانات الطقس
                'temp_c':data["current"]["temp_c"], #الحرارة بالسلسيوس
                'temp_f':data["current"]["temp_f"],         # الحرارة بالفهرنهايت
                'feelslike_c':data["current"]["feelslike_c"],    # الحرارة المحسوسة C
                'feelslike_f':data["current"]["feelslike_f"],    # الحرارة المحسوسة F
                
                #وصف حالة الطقس

                'text':data["current"]["condition"]["text"],   # وصف الحالة 
                'icon':data["current"]["condition"]["icon"],   # أيقونة الطقس
                'code':data["current"]["condition"]["code"],   # كود الحالة
                
                #الرطوبة و السحب

                'humidity':data["current"]["humidity"],       # نسبة الرطوبة %
                'cloud':data["current"]["cloud"],          # نسبة السحب %

                # الامطار و الضغط

                'precip_mm':data["current"]["precip_mm"],      # كمية الأمطار مم
                'pressure_mb':data["current"]["pressure_mb"],    # الضغط الجوي

                #الرئية و الاشعة البنفسجية
                'vis_km':data["current"]["vis_km"],         # مدى الرؤية كم
                'uv':data["current"]["uv"],             # مؤشر الأشعة فوق البنفسجية

                #وقت التحديث
                'last_updated':data["current"]["last_updated"],   # آخر تحديث للبيانات

                #جودة الهواء

                'co':data["current"]["air_quality"]["co"],# أول أكسيد الكربون
                'no2':data["current"]["air_quality"]["no2"],# ثاني أكسيد النيتروجين
                'o3':data["current"]["air_quality"]["o3"],# الأوزون
                'pm2_5':data["current"]["air_quality"]["pm2_5"], # جسيمات دقيقة خطيرة
                'pm10':data["current"]["air_quality"]["pm10"],# جسيمات غبار
                'us-epa-index':data["current"]["air_quality"]["us-epa-index"],# مؤشر جودة الهواء الأمريكي (الأهم)

                


            
            }
        aqi = data["current"]["air_quality"]
        index = aqi["us-epa-index"]
        city_weather["aqi_description"] = get_aqi_description(index)
    
        error='هذه المدينة غير موجودة'
    return render(request,'weatherapi.html',{'city_weather':city_weather,'error':error})        



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


