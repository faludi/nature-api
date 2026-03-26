import nature_api
import secrets

# The nature api is a library for connecting to realtime weather and natural events data, using open-meteo and other sources.

# Valid "current" parameters include:
# temperature_2m
# relative_humidity_2m
# apparent_temperature
# is_day
# wind_speed_10m
# wind_direction_10m
# wind_gusts_10m
# precipitation
# rain
# showers
# snowfall
# weather_code
# cloud_cover
# pressure_msl
# surface_pressure

version = "0.1.0"

print(f"Starting Nature API client v{version} ...")

ssid = secrets.WIFI_SSID
password = secrets.WIFI_PASSWORD

# # Initialize the Nature API client
client = nature_api.Client(ssid, password, default_refresh=300,status_led_pin="LED", debug_mode=False)

# Connect to Wi-Fi
client.connect_wifi()
print('Connected to Wi-Fi')

# Set the location for weather data (will be converted to latitude and longitude)
address = "3 Sheridan Square, New York, NY"

# Set the location for weather data (will be converted to latitude and longitude)
client.set_location(address)
print(f"Location set to: {address}")

# Fetch the current wind speed at the specified location
try:
    wind_speed = client.get("current", "wind_speed_10m")
    print(f"Wind speed at {address} is: {wind_speed} km/h")
    temps = client.get("hourly", "temperature_2m")
    print(f"Hourly temperatures at {address} is: {temps} °C")
except Exception as e:
    print(f"Error fetching weather data: {e}")



