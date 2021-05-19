import gc
import time

import machine
import utime
from LIS2HH12 import LIS2HH12
from pycoproc_1 import Pycoproc


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


def main():
    enable_gc()
    rtc = machine.RTC()
    setup_rtc(rtc=rtc)
    py = Pycoproc(Pycoproc.PYTRACK)
    acc = LIS2HH12()

    while True:
        print("Acceleration: " + str(acc.acceleration()))
        print("Roll: " + str(acc.roll()))
        print("Pitch: " + str(acc.pitch()))
        time.sleep(1.0)

main()