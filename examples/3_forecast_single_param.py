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


# Set location by address (uses Nominatim/OpenStreetMap to geocode)
# The address is converted to latitude/longitude automatically
address = "350 Fifth Avenue, New York, NY"
print(f"Setting location to: {address}")
client.set_location(address)
print(f"✓ Location set to: {client.get_address()}")

location = client.get_location()
if location:
    print(f"  Latitude:  {location['latitude']}")
    print(f"  Longitude: {location['longitude']}")

try:
    # --- CURRENT CONDITIONS (Single Parameter) ---
    print("\nCurrent temperature (single parameter):")
    temp = client.get_forecast("current", "temperature_2m")
    print(f"  Temperature: {temp}°C")

except Exception as e:
    print(f"✗ Error fetching forecast data: {e}")


print("")
print("Done!")