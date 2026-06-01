# Getting Started with Nature API

This guide walks you through the simplest way to use `nature_api.py` on Raspberry Pi Pico 2 W with MicroPython. It is aimed at beginners who know the basics of MicroPython and Wi-Fi-enabled devices.

## 1. What you need

- A Raspberry Pi Pico 2 W, running [MicroPython](https://micropython.org/download/RPI_PICO2_W/)
- `nature_api.py` copied to the device
- `Url_encode.py` copied to the device
- `secrets.py` with your Wi-Fi and API credentials
- An ordinary Wi-Fi network (not "captive")

## 2. Create your `secrets.py`

Create a file called `secrets.py` on the device with:

```python
WIFI_SSID = "your-wifi-ssid"
WIFI_PASSWORD = "your-wifi-password"
IPGEOLOCATION_API_KEY = "your-ipgeolocation-api-key"
```

`IPGEOLOCATION_API_KEY` is needed only for astronomy queries and is freely available [here](https://app.ipgeolocation.io/signup).

## 3. Initialize the client and connect

Create a small script such as `main.py`:

```python
import nature_api
import secrets

client = nature_api.Client(
    secrets.WIFI_SSID,
    secrets.WIFI_PASSWORD,
    default_refresh=300,
    status_led_pin=None,
    debug_mode=False
)

client.connect_wifi()
print("Wi-Fi connected")
```

Run this on your board and verify that Wi-Fi connects successfully.

## 4. Simple temperature lookup

Now add a location and request the current temperature. We use the temperature reading at ground level (2 meters)

```python
client.set_location("350 Fifth Avenue, New York, NY")

temperature = client.get_forecast("current", "temperature_2m")
print("Current temperature:", temperature, "°C")
```

### What this does

- `set_location()` converts the address to latitude/longitude
- `get_forecast("current", "temperature_2m")` fetches current temperature from Open-Meteo
- The result is a raw temperature value for simplicity, not a dictionary

## 5. Multiple forecast variables

Use multiple parameters to read several weather values at once.

```python
results = client.get_forecast(
    "current",
    "temperature_2m,cloud_cover,wind_speed_10m"
)

print("Temperature:", results["temperature_2m"], "°C")
print("Cloud cover:", results["cloud_cover"], "%")
print("Wind speed:", results["wind_speed_10m"], "km/h")
```

Note that for multiple variables, results are returned as a Python dictionary

### Alternative list syntax

```python
results = client.get_forecast(
    "current",
    ["temperature_2m", "wind_speed_10m"]
)
print(results)
```

This shows the raw dictionary.

## 6. Astronomy lookup

Set the astronomy API key and request a single astronomy value.

```python
client.set_api_key("ipgeolocation", secrets.IPGEOLOCATION_API_KEY)

moon_illumination = client.get_astronomy(
    "astronomy",
    "moon_illumination_percentage"
)
print("Moon illumination:", moon_illumination, "%")
```

### Multiple astronomy values

```python
astronomy = client.get_astronomy(
    "astronomy",
    ["sunrise", "sunset", "moon_illumination_percentage"]
)
print("Sunrise:", astronomy["sunrise"])
print("Sunset:", astronomy["sunset"])
print("Moon illumination:", astronomy["moon_illumination_percentage"], "%")
```
Note that for multiple variables, results are returned as a Python dictionary

## 7. Earthquake queries

Request recent earthquakes using USGS query parameters.

```python
quake_params = {
    "minmagnitude": 5.0,
    "orderby": "time",
    "limit": 5
}

quakes = client.get_earthquakes(quake_params)
print("Found", len(quakes.get("features", [])), "earthquakes")
for quake in quakes.get("features", [])[:3]:
    props = quake["properties"]
    time_ms = props["time"]
    print("Magnitude", props["mag"], "at", props["place"])
```

### Example location-based earthquake query

```python
location = client.get_location()
quake_params = {
    "latitude": location["latitude"],
    "longitude": location["longitude"],
    "maxradiuskm": 500,
    "orderby": "time",
    "limit": 5
}
results = client.get_earthquakes(quake_params)
```

Earthquake results are always returned as a Python dictionary.

## 8. Getting new earthquakes only

`get_new_earthquake()` helps you detect when a newer earthquake has occurred for the same query.

```python
new_params = {
    "minmagnitude": 1.0,
    "orderby": "time",
    "limit": 10
}

new_quakes = client.get_new_earthquake(new_params)
if new_quakes:
    print("New earthquake data available")
else:
    print("No new earthquakes since last check")
```

### How it behaves

- On first run, the library stores the newest earthquake ID and returns `None`
- On later runs, it will return data **only** if the newest earthquake has changed
- Request tracking survives reboots, using a hashed filesystem database of newest IDs for each request, saved as `earthquake_ids.txt` by default

## 9. Full beginner example

```python
import time
import nature_api
import secrets

client = nature_api.Client(
    secrets.WIFI_SSID,
    secrets.WIFI_PASSWORD,
    default_refresh=300,
    status_led_pin=None,
    debug_mode=False
)

client.connect_wifi()
client.set_api_key("ipgeolocation", secrets.IPGEOLOCATION_API_KEY)
client.set_location("350 Fifth Avenue, New York, NY")

# Temperature lookup
print("Current temperature:", client.get_forecast("current", "temperature_2m"), "°C")

# Multiple forecast variables
weather = client.get_forecast(
    "current",
    "temperature_2m,cloud_cover,wind_speed_10m"
)
print("Weather:", weather)

# Astronomy lookup
astronomy = client.get_astronomy(
    "astronomy",
    ["sunrise", "sunset", "moon_illumination_percentage"]
)
print("Astronomy:", astronomy)

# Earthquake query
quake_params = {
    "minmagnitude": 5.0,
    "orderby": "time",
    "limit": 5
}
quakes = client.get_earthquakes(quake_params)
print("Earthquakes found:", len(quakes.get("features", [])))
```

## 10. Troubleshooting

- If Wi-Fi does not connect, verify `WIFI_SSID` and `WIFI_PASSWORD` in `secrets.py`.
- If `get_forecast()` raises `ValueError`, make sure `set_location()` has been called.
- If `get_astronomy()` raises `ValueError`, make sure `set_api_key("ipgeolocation", ...)` has been called.
- If earthquake queries fail, ensure `params` is a dictionary and includes at least one parameter.

## 11. Next steps

- Try `forecast_days=7` for a week-long daily forecast
- Use `hourly` category to fetch hourly forecasts
- Add a status LED or display to show current weather and astronomy values
- Schedule `get_new_earthquake()` to run periodically for live earthquake detection
