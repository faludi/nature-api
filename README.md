The Nature API provides a live, realtime feed of natural phenomenon from around the world for use in DIY electronics projects. Our intent is to support easy creation of projects that calmly connect humans with nature, rather than those that simply increase our anxiety, or use numbers to numb our sense of wonder.

Documentation
-------------

- `docs/API.md` — full API reference for all library methods and usage patterns
- `docs/GettingStarted.md` — beginner-friendly guide with Wi-Fi setup, temperature lookup, astronomy, and earthquake examples

Caching
-------

This library includes a simple in-memory TTL cache for fetched data. Both `get_forecast()` and `get_astronomy()` consult the cache before making external API requests and will store fetched values with an expiry (in seconds). Cache keys include the request `category`, `parameter`, and the client's `location` (latitude,longitude), so cached entries are scoped per-location.

Usage notes:
- `get_forecast(category, parameters, forecast_days=1, expiry=900)` — returns a single dictionary of results. The `expiry` parameter controls the TTL in seconds (default 900).
- `get_astronomy(category, parameter, expiry=900)` — behaves similarly, with caching and the same `expiry` parameter.

The cache is in-process only and is not persisted to disk. 

Examples
--------

Simple usage examples (Python):

```python
from nature_api import Client

client = Client('myssid', 'mypassword')
client.wifi_connected = True
client.set_coordinates(51.5, -0.12)

# Weather: request temperature 'value'
temp = client.get_weather('temperature', 'value')
print('Temperature:', temp)

# Marine: request wave height
waves = client.get_marine('waves', 'height')
print('Wave height:', waves)

# Astronomy (requires API key)
client.set_api_key('ipgeolocation', 'YOUR_KEY')
sunrise = client.get_astronomy('sun', 'sunrise')
print('Sunrise local time:', sunrise)

# Earthquakes: pass a USGS query dict
quakes = client.get_earthquakes({'starttime': '2020-01-01'})
print('Quakes response keys:', list(quakes.keys()))
```

Tests
-----

Run the tests with pytest from the repository root:

```bash
pip install pytest
pytest -q
```
