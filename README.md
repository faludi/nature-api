The Nature API provides a live, realtime feed of natural phenomenon from around the world for use in DIY electronics projects. Our intent is to support easy creation of projects that calmly connect humans with nature, rather than those that simply increase our anxiety, or use numbers to numb our sense of wonder.

Caching
-------

This library includes a simple in-memory TTL cache for fetched data. Both `get_forecast()` and `get_astronomy()` consult the cache before making external API requests and will store fetched values with an expiry (in seconds). Cache keys include the request `category`, `parameter`, and the client's `location` (latitude,longitude), so cached entries are scoped per-location.

Usage notes:
- `get_forecast(category, parameters, forecast_days=1, expiry=900)` — returns a single dictionary of results. The `expiry` parameter controls the TTL in seconds (default 900).
- `get_astronomy(category, parameter, expiry=900)` — behaves similarly, with caching and the same `expiry` parameter.

The cache is in-process only and is not persisted to disk.