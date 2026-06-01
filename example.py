"""
NATURE API - COMPREHENSIVE EXAMPLE
This file demonstrates all functionality of the nature_api library.
Each section includes comments explaining what it does and how to use it.
"""

import nature_api
import secrets
import time

# ============================================================================
# INITIALIZATION & SETUP
# ============================================================================

version = "1.0.0"
DEBUG_MODE = False  # Set to True to see debug output from the client

print(f"Starting Nature API client v{version} ...")
print(f"Using Nature API library version: {nature_api.__version__}")

# Retrieve Wi-Fi credentials from secrets file
ssid = secrets.WIFI_SSID
password = secrets.WIFI_PASSWORD

# Initialize the Nature API client
# Parameters:
#   - ssid: Wi-Fi network name
#   - password: Wi-Fi password
#   - default_refresh: default cache expiry in seconds (300 = 5 minutes)
#   - status_led_pin: optional pin for status LED (set to None if not using)
#   - debug_mode: enables verbose output for debugging
client = nature_api.Client(
    ssid,
    password,
    default_refresh=300,
    debug_mode=DEBUG_MODE
)

print("\n" + "="*70)
print("SECTION 1: CONNECTION & TIME SYNC")
print("="*70)

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

print("\n" + "="*70)
print("SECTION 2: API KEYS & CREDENTIALS")
print("="*70)

# Set API key for ipgeolocation.io service
# Required for: astronomy data, local timezone queries
# To use: Get a free API key from https://ipgeolocation.io/
try:
    client.set_api_key("ipgeolocation", secrets.IPGEOLOCATION_API_KEY)
    print("✓ API key set for ipgeolocation.io")
except Exception as e:
    print(f"⚠ Warning: Could not set API key: {e}")

print("\n" + "="*70)
print("SECTION 3: LOCATION MANAGEMENT")
print("="*70)

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

# Optional: Set timezone based on location
# Uses either ipgeolocation.io (if API key set) or timeapi.io
print("\nSetting timezone from location...")
try:
    client.set_timezone_from_location()
    offset_hours = client.get_remote_offset() / 60 / 60
    print(f"✓ Timezone set with UTC offset: {offset_hours:+.1f} hours")
except Exception as e:
    print(f"⚠ Could not set timezone: {e}")

print("\n" + "="*70)
print("SECTION 4: WEATHER FORECASTS (Open-Meteo)")
print("="*70)

# The get_forecast() method retrieves weather data from Open-Meteo API
# Parameters:
#   - category: "current", "hourly", "daily", "minutely_15"
#   - parameters: string (comma-separated) or list of parameter names
#   - forecast_days: number of days to forecast (default 1)
#   - expiry: cache duration in seconds (default 900)
#
# See example_responses/ directory for available parameters

try:
    # --- CURRENT CONDITIONS (Single Parameter) ---
    print("\n[4a] Current temperature (single parameter):")
    temp = client.get_forecast("current", "temperature_2m")
    print(f"  Temperature: {temp}°C")

    # --- CURRENT CONDITIONS (Multiple Parameters as String) ---
    print("\n[4b] Current conditions (multiple parameters as comma-separated string):")
    results = client.get_forecast("current", "temperature_2m,cloud_cover,wind_speed_10m")
    print(f"  Temperature: {results['temperature_2m']}°C")
    print(f"  Cloud cover: {results['cloud_cover']}%")
    print(f"  Wind speed:  {results['wind_speed_10m']} km/h")

    # --- CURRENT CONDITIONS (Multiple Parameters as List) ---
    print("\n[4c] Current conditions (multiple parameters as list):")
    results = client.get_forecast("current", ["temperature_2m", "wind_speed_10m", "relative_humidity_2m"])
    print(f"  Temperature: {results['temperature_2m']}°C")
    print(f"  Wind speed:  {results['wind_speed_10m']} km/h")
    print(f"  Humidity:    {results['relative_humidity_2m']}%")

    # --- HOURLY FORECAST (Next 24 hours) ---
    print("\n[4d] Hourly forecast (next 24 hours):")
    hourly_temps = client.get_forecast("hourly", "temperature_2m")
    print(f"  Hourly temperatures: {hourly_temps[:5]}...")  # Show first 5

    # --- DAILY FORECAST (7 days) ---
    print("\n[4e] Daily forecast (7 days):")
    daily_temps = client.get_forecast("daily", "temperature_2m", forecast_days=7)
    print(f"  Daily high temperatures: {daily_temps}")

    # --- CACHING DEMONSTRATION ---
    # Data is cached by default. Short expiry shows how cache works.
    print("\n[4f] Caching demonstration:")
    print("  First request (will fetch from API)...")
    results1 = client.get_forecast("current", "temperature_2m", expiry=60)
    time.sleep(0.5)
    print("  Second request (will use cache)...")
    results2 = client.get_forecast("current", "temperature_2m", expiry=60)
    if results1 == results2:
        print("  ✓ Cache working correctly (values identical)")

except Exception as e:
    print(f"✗ Error fetching forecast data: {e}")

print("\n" + "="*70)
print("SECTION 5: ASTRONOMY DATA (ipgeolocation.io)")
print("="*70)

# The get_astronomy() method retrieves astronomical data
# Parameters:
#   - category: "astronomy" (currently the only supported category)
#   - parameter: string (single parameter) or list of parameters
#   - expiry: cache duration in seconds
#
# Requires API key to be set (see Section 2)

try:
    # --- SINGLE ASTRONOMY PARAMETER ---
    print("\n[5a] Single astronomy parameter (moon illumination):")
    moon_illumination = client.get_astronomy("astronomy", "moon_illumination_percentage")
    print(f"  Moon illumination: {moon_illumination}%")

    # --- MULTIPLE ASTRONOMY PARAMETERS ---
    print("\n[5b] Multiple astronomy parameters:")
    params = ["moon_illumination_percentage", "sunrise", "sunset", "moonrise", "moonset"]
    results = client.get_astronomy("astronomy", params)
    print(f"  Sunrise:           {results['sunrise']}")
    print(f"  Sunset:            {results['sunset']}")
    print(f"  Moonrise:          {results['moonrise']}")
    print(f"  Moonset:           {results['moonset']}")
    print(f"  Moon illumination: {results['moon_illumination_percentage']}%")

except Exception as e:
    print(f"✗ Error fetching astronomy data: {e}")

print("\n" + "="*70)
print("SECTION 6: EARTHQUAKE QUERIES (USGS)")
print("="*70)

# The get_earthquakes() method queries USGS earthquake data
# Parameters are passed as a dictionary of USGS API query parameters
# See https://earthquake.usgs.gov/fdsnws/event/1/ for full parameter list
#
# Common parameters:
#   - minmagnitude: minimum magnitude to return
#   - maxmagnitude: maximum magnitude to return
#   - minlatitude, maxlatitude, minlongitude, maxlongitude: bounding box
#   - latitude, longitude, maxradiuskm: circular area search
#   - starttime, endtime: date range (YYYY-MM-DD)
#   - orderby: "time", "magnitude", or "relevance"
#   - limit: maximum number of results (default 20, max 20000)

try:
    # --- EARTHQUAKES BY MAGNITUDE ---
    print("\n[6a] Recent earthquakes magnitude 6.0+:")
    eq_params = {
        "minmagnitude": 6.0,
        "orderby": "time",
        "limit": 5
    }
    results = client.get_earthquakes(eq_params)
    features = results.get("features", [])
    print(f"  Found: {len(features)} earthquakes")
    for eq in features[:3]:  # Show first 3
        props = eq["properties"]
        mag = props.get("mag", "?")
        place = props.get("place", "Unknown")
        eq_time = time.gmtime(int(props["time"] / 1000))
        time_str = f"{eq_time[0]}-{eq_time[1]:02d}-{eq_time[2]:02d} {eq_time[3]:02d}:{eq_time[4]:02d} UTC"
        print(f"    • Magnitude {mag} at {time_str}: {place}")

    # --- EARTHQUAKES NEAR LOCATION ---
    print("\n[6b] Earthquakes within 500 km of current location:")
    location = client.get_location()
    if location:
        eq_params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "maxradiuskm": 500,
            "orderby": "time",
            "limit": 5
        }
        results = client.get_earthquakes(eq_params)
        features = results.get("features", [])
        print(f"  Found: {len(features)} earthquakes within 500 km")
        for eq in features[:3]:
            props = eq["properties"]
            mag = props.get("mag", "?")
            place = props.get("place", "Unknown")
            coords = eq["geometry"]["coordinates"]
            distance = "~" + str(int(props.get("distance", 0) / 1000)) + " km"
            print(f"    • Magnitude {mag}: {place} {distance}")

    # --- EARTHQUAKES BY DATE RANGE ---
    print("\n[6c] Earthquakes in the past 7 days (all magnitudes):")
    # MicroPython: use `time.time()` and `time.gmtime()` instead of `datetime` module
    now_ts = time.time()
    seven_days_ago_ts = now_ts - (7 * 24 * 60 * 60)
    now_struct = time.gmtime(now_ts)
    seven_struct = time.gmtime(seven_days_ago_ts)
    # Format YYYY-MM-DD for USGS API
    today_str = "{:04d}-{:02d}-{:02d}".format(now_struct[0], now_struct[1], now_struct[2])
    seven_days_ago = "{:04d}-{:02d}-{:02d}".format(seven_struct[0], seven_struct[1], seven_struct[2])
    eq_params = {
        "starttime": seven_days_ago,
        "endtime": today_str,
        "orderby": "magnitude",
        "limit": 10
    }
    results = client.get_earthquakes(eq_params)
    features = results.get("features", [])
    print(f"  Found: {len(features)} earthquakes in past 7 days")

except Exception as e:
    print(f"✗ Error fetching earthquake data: {e}")

print("\n" + "="*70)
print("SECTION 7: DETECTING NEW EARTHQUAKES (Change Tracking)")
print("="*70)

# The get_new_earthquake() method tracks earthquake changes
# It stores the ID of the newest earthquake matching query parameters
# and only returns data when a NEW (more recent) earthquake is detected.
#
# Behavior:
#   - First call: Stores current newest earthquake ID, returns None
#   - Subsequent calls: Returns None if no change, returns data if newer quake found
#   - Call repeatedly to check for updates (e.g., in a loop or scheduler)

try:
    # --- NEW EARTHQUAKE DETECTION (First Call) ---
    print("\n[7a] Checking for new earthquakes (magnitude 4.0+) [First call]:")
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

    # --- CHECKING AGAIN (Would typically be called later) ---
    print("\n[7b] Checking for new earthquakes again [Subsequent call]:")
    result = client.get_new_earthquake(new_eq_params)
    if result is None:
        print("  ℹ No new earthquakes since last check")
        print("    (Most likely - earthquakes don't occur constantly)")
    else:
        print(f"  ✓ NEW earthquakes detected: {len(result.get('features', []))} found")
        print("    (A more recent earthquake has occurred!)")

    # --- DIFFERENT QUERY PARAMETERS ---
    print("\n[7c] Tracking different earthquake criteria (magnitude 5.0+):")
    new_eq_params_2 = {
        "minmagnitude": 5.0,
        "orderby": "time",
        "limit": 5
    }
    result = client.get_new_earthquake(new_eq_params_2)
    print("  ✓ Separate tracking initialized for magnitude 5.0+")
    print("    (Different query parameters = separate tracking)")

except Exception as e:
    print(f"✗ Error with new earthquake detection: {e}")

print("\n" + "="*70)
print("SECTION 8: LOCATION SWITCHING")
print("="*70)

# You can switch locations and query data for different places
# All data is cached per location, so switching is efficient

try:
    # Define multiple locations
    locations = {
        "New York": "350 Fifth Avenue, New York, NY",
        "London": "Tower Bridge, London",
        "Tokyo": "Tokyo, Japan"
    }

    print("\n[8a] Weather comparison across locations:")
    for city, address in locations.items():
        print(f"\n  Setting location to: {city}")
        client.set_location(address)
        temp = client.get_forecast("current", "temperature_2m")
        wind = client.get_forecast("current", "wind_speed_10m")
        print(f"    Temperature: {temp}°C, Wind: {wind} km/h")

except Exception as e:
    print(f"✗ Error switching locations: {e}")

print("\n" + "="*70)
print("SECTION 9: ERROR HANDLING")
print("="*70)

# Examples of error conditions and how to handle them

print("\n[9a] Missing location (forecast requires location):")
try:
    # Create a new client without setting location
    test_client = nature_api.Client(ssid, password, debug_mode=False)
    test_client.wifi_connected = True  # Simulate connection
    test_client.get_forecast("current", "temperature_2m")
except ValueError as e:
    print(f"  ✓ Caught expected error: {e}")

print("\n[9b] Invalid earthquake parameters:")
try:
    client.get_earthquakes("invalid")  # Should be a dict
except ValueError as e:
    print(f"  ✓ Caught expected error: {e}")

print("\n[9c] Astronomy without API key:")
try:
    test_client = nature_api.Client(ssid, password, debug_mode=False)
    test_client.wifi_connected = True
    test_client.set_location("New York, NY")
    # No API key set - will fail
    test_client.get_astronomy("astronomy", "moon_illumination_percentage")
except ValueError as e:
    print(f"  ✓ Caught expected error: {e}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
This example demonstrated all major features of the nature_api library:

1. ✓ Initialization and Wi-Fi/Time setup
2. ✓ API key management
3. ✓ Location geocoding and switching
4. ✓ Timezone handling
5. ✓ Weather forecasts (current, hourly, daily)
6. ✓ Caching and data management
7. ✓ Astronomy data queries
8. ✓ Earthquake data queries
9. ✓ New earthquake detection with state tracking
10. ✓ Error handling and exceptions

For more information:
- Open-Meteo (weather): https://open-meteo.com/
- ipgeolocation.io (astronomy): https://ipgeolocation.io/
- USGS Earthquakes: https://earthquake.usgs.gov/fdsnws/event/1/
- Nominatim (geocoding): https://nominatim.openstreetmap.org/
""")

print("✓ All examples completed successfully!\n")
