# A library that connects to realtime weather and natural events data, using open-meteo and other sources.

import time
import network
import requests
from Url_encode import url_encode
import machine

class Client:
    def __init__(self, ssid, password, default_refresh=300, status_led_pin=None, debug_mode=False):
        self.ssid = ssid
        self.password = password
        self.default_refresh = default_refresh
        self.status_led_pin = status_led_pin
        self.wifi_connected = False
        self.location = None
        self.debug_mode = debug_mode

        if self.status_led_pin is not None:
            self.led = machine.Pin(self.status_led_pin, machine.Pin.OUT)
            self.led.off()

    def connect_wifi(self):
        if self.status_led_pin is not None:
            self.led.on()  # Turn on LED while connecting

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self.ssid, self.password)

        while not wlan.isconnected():
            time.sleep(1)

        self.wifi_connected = True

        if self.status_led_pin is not None:
            self.led.off()  # Turn off LED after connecting

    # def set_location(self, address):
    #     # Geocoding API to convert address to latitude and longitude
    #     headers = {
    #         "User-Agent": "rp2"  # Add a custom user agent
    #     }
    #     geocode_url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
    #     print(f"Geocoding URL: {geocode_url}")  # Debugging line to check the URL
    #     response = requests.get(geocode_url, headers=headers, timeout=10)
    #     print(f"Geocoding response: {response.text}")  # Debugging line to check the response
    #     response_code = response.status_code
    #     print(f"Geocoding response code: {response_code}")  # Debugging line to check the response code
    #     data = response.json()
    #     print(f"Geocoding data: {data}")  # Debugging line to check the parsed JSON data
        
    #     if data:
    #         self.location = {
    #             "latitude": data[0]["lat"],
    #             "longitude": data[0]["lon"]
    #         }
    #     else:
    #         raise ValueError("Unable to geocode the provided address.")
        
    def set_location(self, address):
        url=url_encode()
        encoded_address = url.encode(address)
        if self.debug_mode:
            print(f"Encoded address: {encoded_address}")  # Debugging line to check the encoded address
        try:
            headers = {
                "User-Agent": "rp2"  # Add a custom user agent
            }
            response = requests.get(f"https://nominatim.openstreetmap.org/search?q={encoded_address}&format=json&limit=1", headers=headers, timeout=10)
            if self.debug_mode:
                print(response.content)
            response_code = response.status_code
            location_data = response.json()
            if self.debug_mode:
                print('Response code: ', response_code)
            
            if location_data:
                self.location = {
                    "latitude": location_data[0]["lat"],
                    "longitude": location_data[0]["lon"]
                }

            else:
                raise ValueError("Location not found")
        except Exception as e:
            print('Error fetching location data:', e)


    def get(self, category ,parameter, forecast_days=1):
        if not self.wifi_connected:
            raise ConnectionError("Wi-Fi is not connected.")
        
        if not self.location:
            raise ValueError("Location is not set.")

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={self.location['latitude']}&longitude={self.location['longitude']}&{category}={parameter}&forecast_days={forecast_days}"
        
        response = requests.get(weather_url)
        data = response.json()
        if self.debug_mode:
            print(f"Weather data: {data}")  # Debugging line to check the weather data
        response_code = response.status_code
        if self.debug_mode:
            print('Response code: ', response_code)

        if category in data and parameter in data[category]:
            return data[category][parameter]
        else:
            raise ValueError(f"{parameter} is not available in the {category} weather data.")