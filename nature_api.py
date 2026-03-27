# A library that connects to realtime weather and natural events data, using open-meteo and other sources.

import time
import network
import requests
from Url_encode import url_encode
import machine
import ntptime

class Client:
    def __init__(self, ssid, password, default_refresh=300, status_led_pin=None, debug_mode=False):
        self.ssid = ssid
        self.password = password
        self.default_refresh = default_refresh
        self.status_led_pin = status_led_pin
        self.wifi_connected = False
        self.address = None
        self.location = None
        self.utc_offset = 0
        self.debug_mode = debug_mode

        if self.status_led_pin is not None:
            self.led = machine.Pin(self.status_led_pin, machine.Pin.OUT)
            self.led.off()

    # def connect_wifi(self, max_retries=5):

    #     if self.status_led_pin is not None:
    #         self.led.on()  # Turn on LED while connecting

    #     wlan = network.WLAN(network.STA_IF)
    #     wlan.active(True)
    #     wlan.connect(self.ssid, self.password)

    #     while not wlan.isconnected():
    #         time.sleep(1)

    #     self.wifi_connected = True

    #     if self.status_led_pin is not None:
    #         self.led.off()  # Turn off LED after connecting

    # def connect_wifi(self, max_retries=10):
    #         connection = False
    #         connection_timeout = max_retries
    #         while not connection:
    #             connection = connect_to_wifi()
    #             connection_timeout -= 1
    #             if connection_timeout == 0:
    #                 print('Could not connect to Wi-Fi, exiting')
    #                 machine.reset()
                
    def connect_wifi(self, attempts_per_cycle=10, max_attempts=10):
        while max_attempts > 0:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            # Connect to network
            wlan.connect(self.ssid, self.password)
            tries = attempts_per_cycle
            while tries > 0:
                if wlan.status() >= 3:
                    self.wifi_connected = True
                    break
                tries -= 1
                print('Waiting for Wi-Fi connection...')
                time.sleep(1)
            # Check if connection is successful
            if wlan.status() != 3:
                print('Failed to establish a network connection')
                max_attempts -= 1
            else:
                print('Connection successful!')
                network_info = wlan.ifconfig()
                print('IP address:', network_info[0])
                return True
        print('Exceeded maximum connection attempts, resetting device...')
        machine.reset()

    def sync_time(self, max_retries=5):
        for _ in range(max_retries):
            try:
                print('Syncing time via NTP...')
                ntptime.settime()
                return True
            except Exception as e:
                print("Error syncing time:", e)
        print(f"Failed to sync time after {max_retries} attempts.")
        return False
        
    def set_timezone_from_location(self):
        if not self.location:
            raise ValueError("Location is not set.")
        
        try:
            headers = {
                "User-Agent": "rp2"  # Add a custom user agent
            }
            response = requests.get(f"https://timeapi.io/api/v1/time/current/coordinate?latitude={self.location['latitude']}&longitude={self.location['longitude']}")
            if self.debug_mode:
                print(response.content)
                print('Response code: ', response.status_code)
            timezone_data = response.json()
                
            if 'utc_offset_seconds' in timezone_data:
                self.utc_offset = timezone_data['utc_offset_seconds']
            else:
                raise ValueError("UTC offset not found in timezone data.")
        except Exception as e:
            print('Error fetching timezone data:', e)
            return False
        
    def set_location(self, address):
        self.address = address
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

    def get_location(self):
        if not self.location:
            return None
        return self.location

    def get_address(self):
        if not self.address:
            return None
        return self.address

    def get_forecast(self, category ,parameter, forecast_days=1):
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

    def set_api_key(self, type, key):
        if type == "ipgeolocation":
            self.ipgeoloation_api_key = key
        else:
            raise ValueError("Unsupported API type. Currently only 'ipgeolocation' is supported.")
        
    def get_astronomy(self, category, parameter):
        if not self.wifi_connected:
            raise ConnectionError("Wi-Fi is not connected.")
        
        if not self.location:
            raise ValueError("Location is not set.")

        astro_url = f"https://api.ipgeolocation.io/v3/astronomy?apiKey={self.ipgeoloation_api_key}&lat={self.location['latitude']}&long={self.location['longitude']}"
        
        response = requests.get(astro_url)
        data = response.json()
        if self.debug_mode:
            print(f"Astronomy data: {data}")  # Debugging line to check the astronomy data
        response_code = response.status_code
        if self.debug_mode:
            print('Response code: ', response_code)

        if category in data and parameter in data[category]:
            return data[category][parameter]
        else:
            raise ValueError(f"{parameter} is not available in the {category} data.")
        