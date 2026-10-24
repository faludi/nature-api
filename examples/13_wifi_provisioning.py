import nature_api

client = nature_api.Client("", "")

def on_status(state):
    print("Provisioning status:", state)

print("Join the 'NatureAPI-Setup' network and open http://192.168.4.1/")
try:
    ssid, password = client.provision_wifi(on_status=on_status, firmware_version="1.0.0")
except nature_api.WifiConnectError:
    print("Could not connect with the submitted credentials")
except nature_api.WifiProvisioningTimeout:
    print("Setup timed out")
else:
    print("Connected to", ssid)
    # This overwrites secrets.py; merge in any other keys (e.g. API keys) you keep there
    with open("secrets.py", "w") as f:
        f.write("WIFI_SSID = %r\nWIFI_PASSWORD = %r\n" % (ssid, password))
