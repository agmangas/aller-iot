import gc
import socket
import time

import machine
import pycom
import utime
from LIS2HH12 import LIS2HH12
from network import LoRa
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


def main():
    pycom.heartbeat(False)
    enable_gc()
    pycoproc = Pycoproc(Pycoproc.PYTRACK)
    acc = LIS2HH12()
    lora, sckt = init_lora()
    rtc = machine.RTC()
    setup_rtc(rtc=rtc)

    while True:
        log_acc(acc=acc)
        payload = "{},{}".format(acc.roll(), acc.pitch())
        print("Sending: {}".format(payload))
        sckt.send(payload)
        pycom.rgbled(0x0000FF)
        time.sleep(0.5)
        pycom.rgbled(0x000000)
        time.sleep(0.5)


main()
