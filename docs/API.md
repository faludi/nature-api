# Nature API — Comprehensive Reference

This document is the full API reference for `nature_api.py`. It covers every public function, expected input formats, returned values, caching behavior, error cases, and example usage.

## 1. Overview

The Nature API library provides real-time natural phenomenon data for MicroPython projects on the Raspberry Pi Pico 2 W, including:

- Weather forecasts from [Open-Meteo](https://open-meteo.com) (`get_weather()`)
- Marine/ocean conditions from [Open-Meteo Marine](https://open-meteo.com/en/docs/marine-weather-api) (`get_marine()`)
- Astronomy data from [IPGeolocation](https://ipgeolocation.io) (`get_astronomy()`)
- Earthquake data from [USGS](https://earthquake.usgs.gov/fdsnws/event/1/) (`get_earthquakes()` and `get_new_earthquake()`)
- Offline in-memory caching for repeated queries
- Location geocoding using [OpenStreetMap](https://www.openstreetmap.org/) / Nominatim

## 2. Setup and installation

Copy `nature_api.py`, `Url_encode.py`, and `secrets.py` to your MicroPython device.

### Required files

- `nature_api.py` — main library
- `Url_encode.py` — URL encoding helper
- `secrets.py` — local credentials file

### Optional example files

- `example.py`
- `example responses/` — sample JSON responses for reference

### `secrets.py` structure

```python
WIFI_SSID = "your-wifi-ssid"
WIFI_PASSWORD = "your-wifi-password"
IPGEOLOCATION_API_KEY = "your-ipgeolocation-api-key"
```

## 3. Client initialization

### `Client(ssid, password, default_refresh=300, debug_mode=False, watchdog=None)`

Creates the API client.

Arguments:
- `ssid`: Wi-Fi SSID string
- `password`: Wi-Fi password string
- `default_refresh`: default cache expiry in seconds (default `300`)
- `debug_mode`: enable verbose logging when `True`
- `watchdog`: optional [watchdog](https://docs.micropython.org/en/latest/library/machine.WDT.html) object with a `feed()` method

Example:

```python
client = nature_api.Client(
    ssid,
    password,
    default_refresh=300,
    debug_mode=False
)
```

## 4. Connection and time helpers

### `connect_wifi(attempts_per_cycle=10, max_cycles=10)`

Connects to Wi-Fi using the provided credentials.

Returns:
- `True` on successful connection
- Resets the device using `machine.reset()` if the connection cannot be established after the specified attempts

Notes:
- `attempts_per_cycle` controls how many status checks are made per connection cycle
- `max_cycles` controls how many cycles are attempted

### `sync_time(max_retries=5)`

Attempts to sync the device clock via NTP.

Returns:
- `True` on success
- `False` after repeated failure

### `set_timezone_from_location()`

Sets `client.utc_offset` based on the currently selected remote location's longitude and latitude

Requires:
- `client.location` must be set
- `client.ipgeolocation_api_key` if using IPGeolocation

Behavior:
- If `ipgeolocation_api_key` is set, uses `ipgeolocation.io`
- Otherwise uses `timeapi.io`

### `get_local_timezone_offset()`

Fetches the local timezone offset from IP geolocation using the local ip address of the device.

Returns:
- integer offset in seconds from UTC
- returns `0` if the request fails

## 5. Location helpers

### `set_location(address)`

Sets the query location by geocoding a human-readable address.

Arguments:
- `address`: string, e.g. `"350 Fifth Avenue, New York, NY"`

Behavior:
- Uses Nominatim / OpenStreetMap to convert the address into latitude and longitude
- Stores `client.location` as a dictionary with `latitude` and `longitude`

Example:

```python
client.set_location("350 Fifth Avenue, New York, NY")
```

### `set_coordinates(latitude, longitude)`

Sets the query location directly using latitude and longitude.

Arguments:
- `latitude`: floating-point latitude value
- `longitude`: floating-point longitude value

Behavior:
- Stores `client.location` as a dictionary with `latitude` and `longitude`
- Useful for marine/ocean queries, where address lookups are not meaningful

Example:

```python
client.set_coordinates(40.569560, -73.983300)
```

### `get_location()`

Returns the current location dictionary, or `None` if no location is set.

Example return value:

```python
{
    "latitude": "40.748432",
    "longitude": "-73.985656"
}
```

### `get_address()`

Returns the original address string provided to `set_location()`, or `None` if not set.

Example return value:

```python
    "350 Fifth Avenue, New York, NY"
```

### `get_remote_offset()`

Returns `client.utc_offset`, the current timezone offset in seconds.

Example return value:

```python
    "-1440"
```

## 6. API key management

### `set_api_key(type, key)`

Configures keys for external services.

Supported key types:
- `"ipgeolocation"` — required for astronomy queries

Example:

```python
client.set_api_key("ipgeolocation", secrets.IPGEOLOCATION_API_KEY)
```

## 7. Forecast API

### `get_weather(category, parameters, forecast_days=1, expiry=900)`

Fetches weather forecast data from Open-Meteo.

Arguments:
- `category`: string; forecast type, e.g. `"current"`, `"hourly"`, `"daily"`
- `parameters`: string or list; one or more Open-Meteo parameter names (see 11. Reference Tables)
- `forecast_days`: integer; number of forecast days (default `1`)
- `expiry`: cache TTL in seconds (default `900`)

Supported parameter inputs:
- single parameter string: `"temperature_2m"`
- comma-separated string: `"temperature_2m,cloud_cover,wind_speed_10m"`
- list of strings: `[
    "temperature_2m",
    "wind_speed_10m"
  ]`

Return value:
- single parameter: direct value
- multiple parameters: dictionary of parameter values

Example: single parameter:

```python
temp = client.get_weather("current", "temperature_2m")
```

Example: multiple parameter response handling:

```python
results = client.get_weather("current", "temperature_2m,cloud_cover,wind_speed_10m")
print(results["temperature_2m"])
print(results["cloud_cover"])
print(results["wind_speed_10m"])
```

### Caching behavior

`get_weather()` uses an in-memory TTL cache keyed by:
- category
- parameter
- current location

If cached data exists and has not expired, the cached value will be returned. This reduces redundant lookups.

## 8. Marine API

### `get_marine(category, parameters, forecast_days=1, expiry=900)`

Fetches marine/ocean weather data from the Open-Meteo Marine API.

Arguments:
- `category`: string; marine forecast type, e.g. `"current"`, `"hourly"`, `"daily"`
- `parameters`: string or list; one or more marine parameter names
- `forecast_days`: integer; number of forecast days (default `1`)
- `expiry`: cache TTL in seconds (default `900`)

Supported parameter inputs:
- single parameter string: `"wave_height"`
- comma-separated string: `"wave_height,sea_level_height_msl,sea_surface_temperature"`
- list of strings: `["wave_height", "sea_level_height_msl"]`

Return value:
- single parameter: direct value
- multiple parameters: dictionary of parameter values

Example: single parameter:

```python
client.set_coordinates(40.569560, -73.983300)
wave_height = client.get_marine("current", "wave_height")
```

Example: multiple parameters:

```python
results = client.get_marine(
    "current",
    "wave_height,sea_level_height_msl,sea_surface_temperature"
)
print(results["wave_height"])
print(results["sea_level_height_msl"])
print(results["sea_surface_temperature"])
```

Example: hourly and daily forecasts:

```python
hourly = client.get_marine("hourly", "sea_level_height_msl")
daily = client.get_marine("daily", "wave_height_max", forecast_days=7)
```

### Caching behavior

`get_marine()` uses the same in-memory TTL cache behavior as `get_weather()`.

## 9. Astronomy API

### `get_astronomy(category, parameter, expiry=900)`

Fetches astronomy data using IPGeolocation.

Arguments:
- `category`: string; currently only `"astronomy"`
- `parameter`: string or list; one or more astronomy fields (see 11. Reference Tables)
- `expiry`: cache TTL in seconds (default `900`)

Return value:
- single parameter: direct value
- multiple parameters: dictionary of values

Example:

```python
moon_illumination = client.get_astronomy("astronomy", "moon_illumination_percentage")
```

Multiple parameters example:

```python
results = client.get_astronomy("astronomy", ["sunrise", "sunset", "moon_illumination_percentage"])
print(results["sunrise"])
print(results["moonset"])
```

## 10. Earthquake API

### `get_earthquakes(params, expiry=900)`

Fetches earthquake data from the USGS event API.

Arguments:
- `params`: dictionary of USGS query parameters (see 11. Reference Tables)
- `expiry`: cache TTL in seconds (default `900`)

Required:
- `params` must be a dictionary with at least one query parameter

Common query parameters:
- `minmagnitude`
- `maxmagnitude`
- `latitude`
- `longitude`
- `maxradiuskm`
- `starttime`
- `endtime`
- `orderby`
- `limit`

Example:

```python
params = {
    "minmagnitude": 5.0,
    "orderby": "time",
    "limit": 5
}
results = client.get_earthquakes(params)
```

Example result usage:

```python
features = results.get("features", [])
for quake in features:
    props = quake["properties"]
    print(props["mag"], props["place"])
```

### `get_new_earthquake(params, expiry=900, state_file="earthquake_ids.txt")`

Returns earthquake data only when a newer earthquake is detected for the same query.

How it works:
- Performs a USGS earthquake query with `get_earthquakes()`
- Finds the newest earthquake feature
- Stores its ID in `state_file`
- Returns `None` if the newest earthquake has not changed since the last call
- Returns data only when a newer event is found

Example:

```python
new_quakes = client.get_new_earthquake({
    "minmagnitude": 1.0,
    "orderby": "time",
    "limit": 10
})
if new_quakes:
    print("New earthquake data available")
else:
    print("No newer earthquakes since last check")
```

Notes:
- First run stores the newest earthquake ID and returns `None`
- The `state_file` is created on the device if needed

## 11. Error handling and debug mode

Common errors:
- `ConnectionError`: Wi-Fi is not connected before calling a network method
- `ValueError`: missing location or invalid parameters
- `ValueError`: unsupported API key type
- `ValueError`: earthquake params not provided as a dictionary

Enable debug mode with `debug_mode=True` to print:
- request URLs
- response content
- cache activity
- internal error diagnostics

## 12. Reference tables

### Forecast parameter examples

- `temperature_2m`
- `cloud_cover`
- `wind_speed_10m`
- `relative_humidity_2m`
- `precipitation_hours`

### Astronomy parameter examples

- `sunrise`
- `sunset`
- `moonrise`
- `moonset`
- `moon_illumination_percentage`
- `moon_phase`

### Earthquake query examples

Search recent significant quakes:

```python
params = {"minmagnitude": 6.0, "orderby": "time", "limit": 5}
```

Search by location:

```python
params = {
    "latitude": location["latitude"],
    "longitude": location["longitude"],
    "maxradiuskm": 500,
    "orderby": "time",
    "limit": 5
}
```

Search by date range:

```python
params = {
    "starttime": "2026-05-01",
    "endtime": "2026-05-31",
    "orderby": "magnitude",
    "limit": 10
}
```

## 13. Example scripts

For working examples, see:

- `example.py`

These demonstrate the connection flow, forecast calls, astronomy queries, and earthquake queries.
