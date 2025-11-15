# Helper function to extract weather for a specific hour
def get_weather_for_hour(weather_data: dict, hour: int):
    """
    Extract weather information for a specific hour from the weather JSON.
    
    :param weather_data: The full weather JSON (dict)
    :param hour: Integer hour (0-23)
    :return: Dict containing weather info for that hour, or None if not found
    """
    try:
        # Get today's hours array
        today_hours = weather_data["days"][0]["hours"]  # assuming you want today's weather

        # Find the hour matching the input
        for h in today_hours:
            hour_in_data = int(h["datetime"].split(":")[0])
            if hour_in_data == hour:
                return h

        # If hour not found
        return {"error": f"No data available for hour {hour}"}
    
    except (KeyError, IndexError) as e:
        return {"error": f"Invalid weather data format: {e}"}
    