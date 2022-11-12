import time
import network
import utime
import socket
from machine import Pin
from machine import PWM
from time import sleep

pwm = PWM(Pin(0))
pwm. freq(50)

def setServoCycle (position):
    pwm.duty_u16(position)
    sleep(0.01)

door = False

pin_1 = Pin(2, Pin.OUT)
pin_2 = Pin(3, Pin.OUT)
pin_3 = Pin(4, Pin.OUT)
pin_4 = Pin(5, Pin.OUT)

pin_1.low()
pin_2.low()
pin_3.low()
pin_4.low()

def o_lock():
    number_of_steps = 1
    max_steps = 130

    while True:
        pin_1.low()
        pin_2.low()
        pin_3.high()
        pin_4.high()
        utime.sleep(0.002)

        pin_1.low()
        pin_2.high()
        pin_3.high()
        pin_4.low()
        utime.sleep(0.002)
        
        pin_1.high()
        pin_2.high()
        pin_3.low()
        pin_4.low()
        utime.sleep(0.002)
        
        pin_1.high()
        pin_2.low()
        pin_3.low()
        pin_4.high()
        utime.sleep(0.002)

        number_of_steps += 1
        
        if number_of_steps == max_steps:
           pin_1.low()
           pin_2.low()
           pin_3.low()
           pin_4.low()
           break

def c_lock():
    number_of_steps = 1
    max_steps = 130

    while True:
        pin_1.high()
        pin_2.low()
        pin_3.low()
        pin_4.high()
        utime.sleep(0.002)

        pin_1.high()
        pin_2.high()
        pin_3.low()
        pin_4.low()
        utime.sleep(0.002)

        pin_1.low()
        pin_2.high()
        pin_3.high()
        pin_4.low()
        utime.sleep(0.002)

        pin_1.low()
        pin_2.low()
        pin_3.high()
        pin_4.high()
        utime.sleep(0.002)

        number_of_steps += 1

        if number_of_steps == max_steps:
           pin_1.low()
           pin_2.low()
           pin_3.low()
           pin_4.low()
           break

led = Pin(15, Pin.OUT)
ledState = 'LED State Unknown'

button = Pin(16, Pin.IN, Pin.PULL_UP)

ssid = ''
password = ''

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)


html = """<!DOCTYPE html><html>
<head><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}
.buttonGreen { background-color: #4CAF50; border: 2px solid #000000;; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }
.buttonRed { background-color: #D11D53; border: 2px solid #000000;; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }
text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
</style></head>
<body><center><h1>Self Automated Touchless Locker</h1></center><br><br>
<form><center>
<center> <button class="buttonGreen" name="led" value="on" type="submit">Open Door</button>
<br><br>
<center> <button class="buttonRed" name="led" value="off" type="submit">Close Door</button>
</form>
<br><br>
<br><br>
<p>%s<p></body></html>
"""

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('Connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('listening on', addr)

while True:
    try:       
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)
        print("request:")
        print(request)
        request = str(request)
        led_on = request.find('led=on')
        led_off = request.find('led=off')
        
        print( 'led on = ' + str(led_on))
        print( 'led off = ' + str(led_off))
        
        if (door == False):
            if led_on == 8:
                print("led on")
                led.value(1)
                o_lock()
                for pos in range(1000,9000,50):
                    setServoCycle(pos)
                door == True
        if (door == True):
            if led_off == 8:
                print("led off")
                led.value(0)
                for pos in range(9000,1000,-50):
                    setServoCycle(pos)
                c_lock()
                door = False
        
        ledState = "Door is closed" if led.value() == 0 else "Door is open"
        
        stateis = ledState
        response = html % stateis
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

    except OSError as e:
        print('connection closed')
