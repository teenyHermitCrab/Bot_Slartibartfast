# SPDX-FileCopyrightText: 2020 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import os
import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests

# URLs to fetch from
TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
JSON_QUOTES_URL = "https://www.adafruit.com/api/quotes.php"
JSON_STARS_URL = "https://api.github.com/repos/adafruit/circuitpython"


print()
print('#' * 40)
print(f'{"  ESP32-S2 web client test  ":#^40}')
print('#' * 40)
mac = ':'.join([hex(i)[2:] for i in wifi.radio.mac_address]).upper()
print(f'MAC address: {mac}')
#print(f'{wifi.radio.hostname=}')
print(f'{wifi.radio.enabled=}')


# explicitly stopping because it seems to already be scanning when booting up
# the subsequent call to scan in loop below sometimes raises a RuntimeError
# since scan already in progress


wifi.radio.stop_scanning_networks()
seen = set()
networks = []
longest_name = 0
for network in wifi.radio.start_scanning_networks():
    if network.ssid not in seen:
        networks.append(network)
        longest_name = max(longest_name, len(network.ssid))
        seen.add(network.ssid)
wifi.radio.stop_scanning_networks()
print()
print("Available WiFi networks:  ")
print(f'{"SSID":>{longest_name}}  {"channel":^7}  {"RSSI":^4}')
print('-' * (longest_name + 16))
for n in networks:
    print(f'{n.ssid.strip():>{longest_name}}  {n.channel:^7}  {n.rssi:^4}')
print()


print(f'connecting to network: {os.getenv("CIRCUITPY_WIFI_SSID")}...', end='')
wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
print(f"connected.")
print(f'IP address: {wifi.radio.ipv4_address}')

ping_ip = ipaddress.IPv4Address("8.8.8.8")  # Google DNS
ping = wifi.radio.ping(ip=ping_ip)
# TODO: set this to variable argument
# retry once if timed out
if ping is None:
    print('retry ping to dns.google (8.8.8.8)')
    ping = wifi.radio.ping(ip=ping_ip)

if ping is None:
    print("Couldn't ping 'google.com' successfully")
else:
    # convert s to ms
    print(f'Pinging "google.com" took: {ping * 1000} ms')


pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

print()
print(f'fetching text from {TEXT_URL}')
response = requests.get(TEXT_URL)
print("-" * 40)
print(response.text)
print("-" * 40)
print()

print(f"Fetching json from {JSON_QUOTES_URL}")
response = requests.get(JSON_QUOTES_URL)
print("-" * 40)
print(response.json())
print("-" * 40)
print()

print(f"Fetching and parsing json from {JSON_STARS_URL}")
response = requests.get(JSON_STARS_URL)
print("-" * 40)
print(f"CircuitPython GitHub Stars: {response.json()['stargazers_count']}")
print("-" * 40)

print("Done")
