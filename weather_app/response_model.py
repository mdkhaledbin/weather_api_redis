from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator

class WeatherDetail(BaseModel):
    # Make most fields optional because API/cache responses may omit some keys
    datetime: Optional[Any] = None
    datetimeEpoch: Optional[Any] = None
    temp: Optional[Any] = None
    feelslike: Optional[Any] = None
    humidity: Optional[Any] = None
    dew: Optional[Any] = None
    precip: Optional[Any] = None
    precipprob: Optional[Any] = None
    snow: Optional[Any] = None
    snowdepth: Optional[Any] = None
    preciptype: Optional[List[Any]] = None
    windgust: Optional[Any] = None
    windspeed: Optional[Any] = None
    winddir: Optional[Any] = None
    pressure: Optional[Any] = None
    visibility: Optional[Any] = None
    cloudcover: Optional[Any] = None
    solarradiation: Optional[Any] = None
    solarenergy: Optional[Any] = None
    uvindex: Optional[Any] = None
    severerisk: Optional[Any] = None
    conditions: Optional[Any] = None
    icon: Optional[Any] = None
    # Use Field(default_factory=list) to avoid mutable default list gotchas
    stations: List[Any] = Field(default_factory=list)
    source: Optional[Any] = None
    sunrise: Optional[Any] = None
    sunriseEpoch: Optional[Any] = None
    sunset: Optional[Any] = None
    sunsetEpoch: Optional[Any] = None
    moonphase: Optional[Any] = None

    # Accept incoming null for stations and coerce to empty list
    @field_validator('stations', mode='before')
    @classmethod
    def _fill_stations(cls, v):
        if v is None:
            return []
        return v
class WeatherResponse(BaseModel):
    location: Any
    weather: WeatherDetail
    source: str
    
class ErrorResponse(BaseModel):
    error: str

class HelthCheckResponse(BaseModel):
    status: str 
    message: str
    