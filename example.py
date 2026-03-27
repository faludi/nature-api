import nature_api
import secrets
import time

# The nature api is a library for connecting to realtime weather and natural events data, using open-meteo and other sources.
# see the "example responses" directory for parameter options and example responses.

version = "0.1.1"
DEBUG_MODE = False

print(f"Starting Nature API client v{version} ...")

ssid = secrets.WIFI_SSID
password = secrets.WIFI_PASSWORD

# # Initialize the Nature API client
client = nature_api.Client(ssid, password, default_refresh=300,status_led_pin="LED", debug_mode=DEBUG_MODE)

# Connect to Wi-Fi
client.connect_wifi()
print('Connected to Wi-Fi')

# Sync time using NTP
if (client.sync_time()):
    print('Time synced successfully')
    print(f"DateTime: {time.gmtime()[0]}-{time.gmtime()[1]:02}-{time.gmtime()[2]:02} {time.gmtime()[3]:02}:{time.gmtime()[4]:02}:{time.gmtime()[5]:02} UTC  ")
else:
    print('Time sync failed, using unsynced time')

# Set the location for weather data (will be converted to latitude and longitude)
address_regular = "3 Sheridan Square, New York, NY"
address_cold = "Nuuk, Greenland"
address_hot = "Death Valley, California"
address_parents = "Sun City West, Arizona"

# Set the physical location (will be converted to latitude and longitude)
client.set_location(address_parents)
print(f"Location set to: {client.get_address()}")

# Set the timezone based on the location (using timeapi.io API)
try:
    client.set_timezone_from_location()
    print(f"Timezone set with UTC offset: {client.utc_offset} seconds")
except Exception as e:
    print(f"Error setting timezone: {e}")

# Set the API key for ipgeolocation.io (required for astronomy data)
client.set_api_key("ipgeolocation", secrets.IPGEOLOCATION_API_KEY)

# Fetch some natural phenomena data at the specified location
try:
    cloud_cover = client.get_forecast("current", "cloud_cover")
    print(f"Cloud cover at {client.get_address()} is: {cloud_cover}%")

    moon_illumination = client.get_astronomy("astronomy", "moon_illumination_percentage")
    print(f"Moon illumination at {client.get_address()} is: {moon_illumination}%")

    # wind_speed = client.get_forecast("current", "wind_speed_10m")
    # print(f"Wind speed at {client.get_address()} is: {wind_speed} km/h")

    # temps = client.get_forecast("hourly", "temperature_2m")
    # print(f"Hourly temperatures at {address_regular} are:", end=" ")
    # for temp in temps:
    #     print(f"{temp}°C", end=" ")
    # print(" ")  # New line after printing temperatures

    # temps = client.get_forecast("current", "temperature_2m")
    # print(f"Current temperatures at {address_regular} is: {temps} °C")
    # client.set_location(address_cold)
    # print(f"Location set to: {address_cold}")
    # temps = client.get_forecast("current", "temperature_2m")
    # print(f"Current temperatures at {address_cold} is: {temps} °C")
    # client.set_location(address_hot)
    # print(f"Location set to: {address_hot}")
    # temps = client.get_forecast("current", "temperature_2m")
    # print(f"Current temperatures at {address_hot} is: {temps} °C")
except Exception as e:
    print(f"Error fetching weather data: {e}")



