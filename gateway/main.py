import gc
import socket
import time

import machine
import pycom
import utime
import urequests
import ubinascii
from network import WLAN, LoRa
from pycoproc_1 import Pycoproc

WLAN_SSID = "pycom-wifi"
WLAN_PASS = "securepassword"
WLAN_TIMEOUT_MS = 180000

ENABLE_WIFI = True

INFLUX_TOKEN = "secret"
INFLUX_WRITE_URL = "https://influxdb.test.ctic.es/api/v2/write"
INFLUX_WRITE_ARGS = "org=default_org&bucket=default_bucket&precision=s"


def enable_gc():
    print("Enabling garbage collector")
    time.sleep(2.0)
    gc.enable()
    print("Garbage collector: OK")


def setup_rtc(rtc):
    print("RTC NTP sync")
    rtc.ntp_sync("pool.ntp.org")
    utime.sleep_ms(750)
    print("RTC set from NTP to UTC: {}".format(rtc.now()))


def connect_wlan(wlan):
    print("Connecting to SSID: {}".format(WLAN_SSID))

    wlan.connect(
        ssid=WLAN_SSID,
        auth=(WLAN.WPA2, WLAN_PASS),
        timeout=WLAN_TIMEOUT_MS)

    now = time.ticks_ms()

    while not wlan.isconnected():
        if (time.ticks_ms() - now) > WLAN_TIMEOUT_MS:
            raise TimeoutError("WiFi timeout")

        print("Still disconnected")
        pycom.rgbled(0xFF0000)
        time.sleep(0.5)
        pycom.rgbled(0x000000)
        time.sleep(0.5)

    pycom.rgbled(0x000000)
    print("WiFi connected succesfully")
    print("wlan.ifconfig:\n{}".format(wlan.ifconfig()))


def log_acc(acc):
    print("Acceleration: " + str(acc.acceleration()))
    print("Roll: " + str(acc.roll()))
    print("Pitch: " + str(acc.pitch()))


def init_lora():
    print("Initializing LoRa")
    lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)
    sckt = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    sckt.setblocking(False)

    return lora, sckt


def parse_payload(payload):
    try:
        payload = payload.decode()
        splitted = payload.split(",")
        roll = float(splitted[0])
        pitch = float(splitted[1])
        return {"roll": roll, "pitch": pitch}
    except Exception as ex:
        return None


def map_to_rgbled(val, vmax):
    val = abs(val)
    val = min(vmax, max(0, val))
    rgb_val = int((float(val) / vmax) * 254) << 8
    pycom.rgbled(rgb_val)


def post_roll(roll):
    try:
        url = "{}?{}".format(INFLUX_WRITE_URL, INFLUX_WRITE_ARGS)
        device = ubinascii.hexlify(machine.unique_id()).decode()
        data = "acceleration,device={} roll={}".format(device, roll)

        print("Uploading: {}".format(data))

        res = urequests.post(
            url,
            headers={
                "Content-Type": "text/plain",
                "Authorization": "Token {}".format(INFLUX_TOKEN)
            },
            data=str(data))

        res.close()
    except Exception as ex:
        print("HTTP error: {}".format(ex))


def main():
    pycom.heartbeat(False)
    enable_gc()
    Pycoproc(Pycoproc.PYTRACK)

    if ENABLE_WIFI:
        wlan = WLAN(mode=WLAN.STA)
        connect_wlan(wlan=wlan)

    lora, sckt = init_lora()
    rtc = machine.RTC()
    setup_rtc(rtc=rtc)

    while True:
        payload = sckt.recv(64)
        print("Raw payload: {}".format(payload))
        data = parse_payload(payload=payload)

        if data:
            print("Received: {}".format(data))
            map_to_rgbled(data["roll"], vmax=180)

            if ENABLE_WIFI:
                post_roll(data["roll"])

        time.sleep(0.05)


main()
