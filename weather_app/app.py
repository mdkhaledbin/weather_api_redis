from fastapi import FastAPI, HTTPException, Depends
import redis.asyncio as redis
import os
import yaml
from dotenv import load_dotenv
import requests
import json

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter


from city_time import get_city_time
from hourly_weather import get_weather_for_hour
from response_model import WeatherResponse, ErrorResponse, HelthCheckResponse

r: redis.Redis | None = None  # global variable

# Load environment variables from .env file
load_dotenv()

# Retrieve API_KEY and BASE_URL from environment variables
try:
    API_KEY = os.environ['API_KEY']
    BASE_URL = os.environ['BASE_URL']
    print("API_KEY & BASE_URL loaded successfully from environment variables.")
except KeyError:    
    raise KeyError(error="API_KEY not found in environment variables. Please set it in the .env file.")

# Load configuration from YAML file
try:
    config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    # config_file = open(config_path, 'r') // error for not using yaml.safe_load as here open returns a file object not a dict
    # config = config_file.read()
    print(f"Loaded configuration from {config_file.name}")
except Exception as e:
    raise Exception(error=f"Error loading configuration: {e}")


app = FastAPI()

@app.on_event("startup")
async def startup():
    global r
    try:
        r = redis.from_url(
            f"redis://{config['server']['redis']['host']}:{config['server']['redis']['port']}/{config['server']['redis']['db']}",
            encoding="utf-8",
            decode_responses=True
        )
        # Initialize limiter with async Redis
        await FastAPILimiter.init(r)
        # Ping Redis (must await)
        await r.ping()
        print("Connected to Redis successfully")
    except Exception as e:
        raise Exception(error=f"Error connecting to Redis: {e}")

app.title = "Weather API"
app.version = "1.0.0"
app.description = "API for fetching weather data"

@app.get("/")
async def read_root():
    return HelthCheckResponse(status="ok", message="Welcome to the Weather API")

# Example of making a request to the weather API
@app.get("/weather/{location}", dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def get_weather(location: str):
    global r
    
    # First, get the current hour in the specified location
    try:
        city_time = await get_city_time(location)
        print(f"City time for {location}: {city_time}")
    except HTTPException as e:
        print(f"Could not fetch city time for {location}: {e.detail}")
        return ErrorResponse(error=f"Could not fetch city time for {location}: {e.detail}")

    # Check Redis cache first
    weather = await r.get(location)
    if weather:
        print(f"Cache hit for location: {location}")
        weather_json = json.loads(weather)
        hourly_weather = get_weather_for_hour(weather_json, city_time['hour'])
        return WeatherResponse(location=location, weather=hourly_weather, source="cache")

    # If not in cache, fetch from weather API
    params = {
        'unitGroup': 'metric',
        'key': API_KEY,
        'contentType': 'json'
    }
    url = f"{BASE_URL}{location}/today"
    print(f"Requesting weather data from URL: {url} with params: {params}")
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            response_data = response.json()
            await r.set(location,  json.dumps(response_data), ex=86400)  # Cache for 12 hours
            print(f"Cache miss for location: {location}. Fetched and cached new data.")
            
            hourly_weather = get_weather_for_hour(response_data, city_time['hour'])
            return WeatherResponse(location=location, weather=hourly_weather, source="api")
        else:
            return ErrorResponse(error="Failed to fetch weather data")
    except Exception as e:
        return ErrorResponse(error=f"An error occurred: {e}")