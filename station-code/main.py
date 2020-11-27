import network
import urequests
import ujson
import machine
import time

def do_post(url, data):

    headers = {'Content-Type': 'application/json'}

    r = urequests.post(url, data=data, headers=headers)
    #print(r)
    results = r.json()
    #print(results)
    
def do_connect_as_ap(ap_ssid, ap_pwd):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(False)
    ap.config(essid=ap_ssid, password=ap_pwd)

    while ap.active() == False:
      pass
    print('network config:', ap.ifconfig())
      
def do_connect_as_station(sta_ssid, sta_pwd):
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(sta_ssid, sta_pwd)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())


### Main config parameters
viola_host_ip = "http://10.41.2.37:8000/"
CONFIG_PIN = 0 ## GPIO 0 - config button in wiolink
GPIO_PIN_14_DP0 = 14
GPIO_PIN_12_DP1 = 12
GPIO_PIN_13_DP2 = 13

key_val_dp0 = 0
key_val_dp1 = 0
key_val_dp2 = 0
self_id = 100 # Some unique id for this station
ap_ssid = "MicroPython-abba"
ap_pwd = "abba"
sta_ssid = ""
sta_pwd = ""

# Connect to target host
do_connect_as_station(sta_ssid, sta_pwd);

data = {}
data["station-id"] = str(self_id)
data["counter"] = 0
data["value"] = 0
data["value1"] = 0
data["value2"] = 0
press_count = 0

# Power all sensors (RED led turns on)
p15 = machine.Pin(15, machine.Pin.OUT)
p15.on()

print ("Entering loop. Press config to exit...")
# DEMO - Exit if config pressed
config_val = 1
while config_val == 1:
    time.sleep_ms(50)
    key_val_dp0 = machine.Pin(GPIO_PIN_14_DP0, machine.Pin.IN).value()
    key_val_dp1 = machine.Pin(GPIO_PIN_12_DP1, machine.Pin.IN).value()
    key_val_dp2 = machine.Pin(GPIO_PIN_13_DP2, machine.Pin.IN).value()

    if int(key_val_dp0) == 1 or int(key_val_dp1) == 1 or int(key_val_dp2) == 1: # if any high
        press_count = press_count + 1
        
        data["value"] = int(key_val_dp0)
        data["value1"] = int(key_val_dp1)
        data["value2"] = int(key_val_dp2)
        data["counter"] = press_count
        json_data = ujson.dumps(data)
        # POST to target host
        try:
            do_post(viola_host_ip, json_data)
        except:
            print('Error posting')
    config_val = machine.Pin(CONFIG_PIN, machine.Pin.IN).value()

p15.off()
print("Exiting")
