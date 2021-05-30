import urandom
from neopixel import NeoPixel
from sensorclass import Sensor
from machine import Pin
import time

# ledclock2
# updated 2/1/2021

def set_nightlight(brightlevel):
    #print("brightlevel: " + str(brightlevel))
    global led
    for x in range(13):
        led[x] = (brightlevel,brightlevel,brightlevel)
    led.write()

ledpin = Pin(5, Pin.OUT)
led = NeoPixel(ledpin, 13)
m = [6,5,4,3,2,1,0,11,10,9,8,7,12]
state = False
statechange = False
timechange = True
nldelay = 60
nightlight = False
heartbeat = True
hour = 0
minute = 0
lasthour = 0
lastminute = 0
second = 1
lastsecond = 0
gottime = False

brightness = Sensor("brightness", initval=40)

def main():
    global led
    global gottime
    global state
    global statechange
    global timechange
    global nldelay
    global brightness
    global nightlight
    global heartbeat
    global hour
    global minute
    global lasthour
    global lastminute
    global second
    global lastsecond
    secfade = time.ticks_ms()
    set_nightlight(1)

    Sensor.MQTTSetup("ledclock")
    Sensor.lasthour = -1

    secfade = time.ticks_ms()
    print("End Setup... Starting loop")

    while True:
        Sensor.lastblink = time.time()
        Sensor.Spin()
        secbright = time.ticks_ms() - secfade 
        fadetime = 500
        if secbright < fadetime:
            led[m[11-lastsecond]] = (led[m[11-lastsecond]][0],led[m[11-lastsecond]][1], int(brightness.value * (fadetime - secbright) / fadetime)+1)
            led.write()

        if secbright < 1001:
            led[m[11-second]] = (led[m[11-second]][0],led[m[11-second]][1], int(brightness.value * secbright / 1000))
            led.write()

        if (secbright > 100 ) and not gottime:
            secbright = 5001
            timechange = True
            led[m[11-lastsecond]] = (0,0,0)
            if second == 11 and not gottime:
                lastminute = minute
                minute += 1
                if minute > 11:
                    minute = 0
                    lasthour = hour
                    hour += 1
                if hour > 11:
                    hour =   0

        if secbright > 5000:
            lastsecond = second
            second = second + 1
            if second == 12:
                second = 0
            secfade = time.ticks_ms()

        if (Sensor.lastminute != minute) and (Sensor.lasthour >= 0):
            set_nightlight(1)
            gottime = True
            lasthour = hour
            lastminute = minute
            hour = Sensor.lasthour
            if hour > 12:
                hour = hour - 12
            if hour == 0:
                hour = 12
            minute = int(Sensor.lastminute / 5)
            if minute == 0:
                minute = 12
            Sensor.lastminute = minute
            timechange = True

        if timechange or brightness.triggered:
            led[m[12-lasthour]] = (1,1,1)
            led[m[12-lastminute]] = (1,1,1)
            led[m[11-lastsecond]] = (1,1,1)
            led.write()
            led[m[12-hour]] = (brightness.value,0,0)
            led[m[12-minute]] = (led[m[12-minute]][0],brightness.value,0)
            led.write()
            brightness.triggered = False
            timechange = False
