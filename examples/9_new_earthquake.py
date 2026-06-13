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

# Set API key for ipgeolocation.io service
# Required for: astronomy data, local timezone queries
# To use: Get a free API key from https://ipgeolocation.io/
try:
    client.set_api_key("ipgeolocation", secrets.IPGEOLOCATION_API_KEY)
    print("✓ API key set for ipgeolocation.io")
except Exception as e:
    print(f"⚠ Warning: Could not set API key: {e}")

try:
    # --- NEW EARTHQUAKE DETECTION (First Call) ---
    print("\nChecking for new earthquakes (magnitude 4.0+) [First call]:")
    new_eq_params = {
        "minmagnitude": 4.0,
        "orderby": "time",
        "limit": 10
    }
    result = client.get_new_earthquake(new_eq_params)
    if result is None:
        print("  ✓ Earthquake tracking initialized")
        print("    (First call stores baseline, returns None)")
    else:
        print(f"  ✓ New earthquakes detected: {len(result.get('features', []))} found")

    # Wait a minute before checking again (in real use, this would be much longer, e.g. hourly/daily)
    print("\nWaiting 60 seconds before checking for new earthquakes again...")
    time.sleep(60)

    # --- CHECKING AGAIN (Would typically be called later) ---
    print("\nChecking for new earthquakes again [Subsequent call]:")
    result = client.get_new_earthquake(new_eq_params)
    if result is None:
        print("  ℹ No new earthquakes since last check")
        print("    (Most likely - earthquakes don't occur constantly)")
    else:
        print(f"  ✓ NEW earthquakes detected: {len(result.get('features', []))} found")
        print("    (A more recent earthquake has occurred!)")

except Exception as e:
    print(f"✗ Error fetching earthquake data: {e}")

print("")
print("Done!")