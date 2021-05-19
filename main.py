import gc
import time

import machine
import utime
from LIS2HH12 import LIS2HH12
from network import WLAN
from pycoproc_1 import Pycoproc

WLAN_SSID = "pycom-wifi"
WLAN_PASS = "securepassword"
WLAN_TIMEOUT_MS = 20000

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
        time.sleep(1.0)
    
    print("WiFi connected succesfully")
    print("wlan.ifconfig:\n{}".format(wlan.ifconfig()))


def main():
    enable_gc()
    py = Pycoproc(Pycoproc.PYTRACK)
    acc = LIS2HH12()
    
    wlan = WLAN(mode=WLAN.STA)
    connect_wlan(wlan=wlan)

    rtc = machine.RTC()
    setup_rtc(rtc=rtc)

    while True:
        print("Acceleration: " + str(acc.acceleration()))
        print("Roll: " + str(acc.roll()))
        print("Pitch: " + str(acc.pitch()))
        time.sleep(1.0)

main()
