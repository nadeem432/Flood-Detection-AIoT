import time
import network
import BlynkLib
from machine import Pin
import utime

rl = Pin(3, Pin.OUT)
yl = Pin(4, Pin.OUT)
trigger = Pin(5, Pin.OUT)
echo = Pin(6, Pin.IN)
buz = Pin(7, Pin.OUT)
led = Pin("LED", Pin.OUT)
led.on()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("IT-LAB", "")

wait = 20
while wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    wait -= 1
    time.sleep(0.5)

if wlan.status() != 3:
    raise RuntimeError("Network connection failed")
else:
    ip = wlan.ifconfig()[0]
    print("IP Address:", ip)

BLYNK_AUTH = "VoZ8aPe1O-kTA-DTUSnWyl9fPv2IbbJc"
blynk = BlynkLib.Blynk(BLYNK_AUTH)

def ultra():
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(10)
    trigger.low()

    while echo.value() == 0:
        signaloff = utime.ticks_us()
    while echo.value() == 1:
        signalon = utime.ticks_us()

    timepassed = signalon - signaloff
    distance = (timepassed * 0.0343) / 2
    percentage = 100 * (1 - (distance - 8.7) / (11 - 8.7))
    return max(0, min(percentage, 100))

while True:
    try:
        water_level = ultra()
        print("Water Level:", round(water_level, 2), "%")

        if water_level > 80:
            print("Flood Alert!")
            buz.value(1)
            rl.value(1)
            yl.value(0)
        else:
            buz.value(0)
            rl.value(0)
            yl.value(1)

        blynk.virtual_write(0, round(water_level, 2))
        blynk.run()
        time.sleep(1)

    except Exception as e:
        print("Sensor Error:", e)
        buz.value(0)
        rl.value(0)
        yl.value(0)
        time.sleep(1)
