import requests
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime
from fastapi import HTTPException


# @app.get("/time/{city_name}")
async def get_city_time(city_name: str):
    # Try geopy + timezonefinder first
    try:
        geolocator = Nominatim(user_agent="time_app")
        location = geolocator.geocode(city_name, timeout=10)
        if not location:
            raise ValueError(f"City '{city_name}' not found")
        
        tz_name = TimezoneFinder().timezone_at(lat=location.latitude, lng=location.longitude)
        if not tz_name:
            raise ValueError(f"Could not determine timezone for '{city_name}'")
        
        tz = pytz.timezone(tz_name)
        city_hour = datetime.now(tz).hour 
        return {"city": city_name, "hour": city_hour}
    
    except Exception as e:
        # Fallback: WorldTimeAPI
        try:
            response = requests.get(f"http://worldtimeapi.org/api/timezone/{city_name}")
            response.raise_for_status()
            data = response.json()
            # extract hour from datetime string
            datetime_str = data.get("datetime")
            if datetime_str:
                city_hour = int(datetime_str[11:13])
                return {"city": city_name, "hour": city_hour}
            
        except Exception:
            raise HTTPException(status_code=404, detail=f"Could not retrieve time for '{city_name}'")