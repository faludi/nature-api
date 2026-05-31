# Nature API — Comprehensive Reference

This document is the full API reference for `nature_api.py`. It covers every public function, expected input formats, returned values, caching behavior, error cases, and example usage.

## 1. Overview

The Nature API library provides real-time natural phenomenon data for MicroPython projects, including:

- Weather forecasts from Open-Meteo (`get_forecast()`)
- Astronomy data from IPGeolocation (`get_astronomy()`)
- Earthquake data from USGS (`get_earthquakes()` and `get_new_earthquake()`)
- Offline in-memory caching for repeated queries
- Location geocoding using OpenStreetMap / Nominatim

## 2. Setup and installation

Copy `nature_api.py`, `Url_encode.py`, and `secrets.py` to your MicroPython device.

### Required files

- `nature_api.py` — main library
- `Url_encode.py` — URL encoding helper
- `secrets.py` — local credentials file

### Optional example files

- `example.py`
- `full_example.py`
- `example responses/` — sample JSON responses for reference

### `secrets.py` structure

```python
WIFI_SSID = "your-wifi-ssid"
WIFI_PASSWORD = "your-wifi-password"
IPGEOLOCATION_API_KEY = "your-ipgeolocation-api-key"
```

## 3. Client initialization

### `Client(ssid, password, default_refresh=300, status_led_pin=None, debug_mode=False, watchdog=None)`

Creates the API client.

Arguments:
- `ssid`: Wi-Fi SSID string
- `password`: Wi-Fi password string
- `default_refresh`: default cache expiry in seconds (default `300`)
- `status_led_pin`: optional MicroPython pin name/number for an activity LED
- `debug_mode`: enable verbose logging when `True`
- `watchdog`: optional watchdog object with a `feed()` method

Example:

```python
client = nature_api.Client(
    ssid,
    password,
    default_refresh=300,
    status_led_pin="LED",
    debug_mode=False
)
```

## 4. Connection and time helpers

### `connect_wifi(attempts_per_cycle=10, max_attempts=10)`

Connects to Wi-Fi using the provided credentials.

Returns:
- `True` on successful connection
- Resets the device using `machine.reset()` if the connection cannot be established after the specified attempts

Notes:
- `attempts_per_cycle` controls how many status checks are made per connection cycle
- `max_attempts` controls how many cycles are attempted

### `sync_time(max_retries=5)`

Attempts to sync the device clock via NTP.

Returns:
- `True` on success
- `False` after repeated failure

### `set_timezone_from_location()`

Sets `client.utc_offset` based on the current location.

Requires:
- `client.location` must be set
- `client.ipgeolocation_api_key` if using IPGeolocation

Behavior:
- If `ipgeolocation_api_key` is set, uses `ipgeolocation.io`
- Otherwise uses `timeapi.io`

### `get_local_timezone_offset()`

Fetches the local timezone offset from IP geolocation.

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

### `get_remote_offset()`

Returns `client.utc_offset`, the current timezone offset in seconds.

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

### `get_forecast(category, parameters, forecast_days=1, expiry=900)`

Fetches weather forecast data from Open-Meteo.

Arguments:
- `category`: string; e.g. `"current"`, `"hourly"`, `"daily"`
- `parameters`: string or list; one or more Open-Meteo parameter names
- `forecast_days`: integer number of forecast days (default `1`)
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

Example:

```python
temp = client.get_forecast("current", "temperature_2m")
```

Example response handling:

```python
results = client.get_forecast("current", "temperature_2m,cloud_cover,wind_speed_10m")
print(results["temperature_2m"])
print(results["cloud_cover"])
print(results["wind_speed_10m"])
```

### Caching behavior

`get_forecast()` uses an in-memory TTL cache keyed by:
- category
- parameter
- current location

If cached data exists and has not expired, the cached value will be returned.

## 8. Astronomy API

### `get_astronomy(category, parameter, expiry=900)`

Fetches astronomy data using IPGeolocation.

Arguments:
- `category`: string; currently only `"astronomy"`
- `parameter`: string or list; one or more astronomy fields
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

### Astronomy parameters

Common astronomy fields returned by IPGeolocation include:
- `sunrise`
- `sunset`
- `moonrise`
- `moonset`
- `moon_illumination_percentage`
- `moon_phase`

## 9. Earthquake API

### `get_earthquakes(params, expiry=900)`

Fetches earthquake data from the USGS event API.

Arguments:
- `params`: dictionary of USGS query parameters
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

## 10. Error handling and debug mode

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

## 11. Reference tables

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

## 12. Example scripts

For working examples, see:

- `example.py`
- `full_example.py`

These demonstrate the connection flow, forecast calls, astronomy queries, and earthquake queries.
