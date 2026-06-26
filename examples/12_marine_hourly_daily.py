import nature_api
import secrets
import time

print(f"Using Nature API library version: {nature_api.__version__}")

# Retrieve Wi-Fi credentials from secrets file
ssid = secrets.WIFI_SSID
password = secrets.WIFI_PASSWORD

# Initialize the Nature API client
# Parameters:
#   - ssid: Wi-Fi network name
#   - password: Wi-Fi password
#   - status_led_pin: optional pin for status LED (set to None if not using)
#   - debug_mode: enables verbose output for debugging
client = nature_api.Client(
    ssid,
    password,
)

# Connect to Wi-Fi with retry attempts
# Automatically resets device if max_attempts is exceeded
print("Connecting to Wi-Fi...")
client.connect_wifi()
print("✓ Connected to Wi-Fi")

# Synchronize system time with NTP (Network Time Protocol)
# This is required for accurate timestamp handling
print("Syncing time with NTP...")
if client.sync_time():
    print("✓ Time synced successfully")
    current_time = time.gmtime()
    time_str = f"{current_time[0]}-{current_time[1]:02d}-{current_time[2]:02d} {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d} UTC"
    print(f"  Current time: {time_str}")
else:
    print("⚠ Time sync failed, using device time")

# Set location by coordinates (no address lookups in the ocean, so we use lat/lon directly)
# The coordinates are for the end of Coney Island's Steeplechase Pier, Brooklyn, New York, USA
latitude = 40.569560
longitude = -73.983300
client.set_coordinates(latitude, longitude)

location = client.get_location()
if location:
    print(f"  Latitude:  {location['latitude']}")
    print(f"  Longitude: {location['longitude']}")

## Set timezone based on the coordinates
client.set_timezone_from_location()

try:
    # --- HOURLY FORECAST (Next 24 hours) ---
    print("\nHourly forecast (next 24 hours):")
    hourly_temps = client.get_marine("hourly", "sea_level_height_msl")
    print(f"  Hourly sea level heights: {hourly_temps}")

    # --- DAILY FORECAST (7 days) ---
    print("\nDaily forecast (7 days):")
    daily_temps = client.get_marine("daily", "wave_height_max", forecast_days=7)
    print(f"  Daily wave height max: {daily_temps}")

except Exception as e:
    print(f"✗ Error fetching marine data: {e}")


print("")
print("Done!")