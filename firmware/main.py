"""
Code for controlling a PC fan (model # FFC0912DE-TP04)
using an ESP32 board.

Hookup:

* red wire to +12V
* black wire to GND
* yellow wire to pin 19
* blue wire to pin 25


References:

https://techtutorialsx.com/2017/10/07/esp32-micropython-timeimport webrepl_setupr-interrupts/
http://partner.delta-corp.com/Products/FanUploads/Specification/FFC0912DE-TP04.pdf
DS18B20: https://www.adafruit.com/product/381
si7021: https://bitbucket.org/thesheep/micropython-si7021
"""

import machine
from machine import Pin
import time
import network
import onewire
import ds18x20

import BlynkLib
import si7021
import uasyncio as asyncio

try:
  from secrets import BLYNK_AUTH, WIFI_SSID, WIFI_PASSWORD
except:
  print('You must create a secrets.py file.')


interrupt_counter = 0

def callback(pin):
  """This callback function is attached to an interrupt handler.
  """
  global interrupt_counter
  interrupt_counter = interrupt_counter + 1

# Attach an interrupt to trigger on the falling edge on pin 25.
tach = Pin(25, Pin.IN, Pin.PULL_UP)
tach.irq(trigger=Pin.IRQ_FALLING, handler=callback)

# Setup the fan to use a PWM frequency of 25kHz and a 50% duty cycle.
fan = machine.PWM(Pin(19, Pin.OUT), freq=25000, duty=int(0.5*1023))

ds = ds18x20.DS18X20(onewire.OneWire(Pin(32)))

addresses = None
while not addresses or len(addresses) < 2:
  addresses = ds.scan()

i2c = machine.I2C(sda=Pin(21),scl=Pin(22))
si7021_sensor = si7021.SI7021(i2c)

print("Connecting to WiFi...")
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)
while not wifi.isconnected():
    pass
    
print('IP:', wifi.ifconfig()[0])

print("Connecting to Blynk...")
blynk = BlynkLib.Blynk(BLYNK_AUTH)


@blynk.ON("connected")
def blynk_connected(ping):
    print('Blynk ready. Ping:', ping, 'ms')

counter_start_time_ms = time.ticks_ms()

def get_frequency():
  global interrupt_counter, counter_start_time_ms
  
  """
  # 1. Measure time for n pulses (blocking)
  
  interrupt_counter = 0
  start_time = time.ticks_ms()
  while interrupt_counter < n:
    pass
  t_delta = time.ticks_diff(time.ticks_ms(), start_time)
  frequency = float(n) / t_delta * 1000
  return frequency

  # 2. Measure number of pulses over a fixed period of time (blocking)
  
  interrupt_counter = 0
  t_delta_ms = 500
  time.sleep_ms(t_delta_ms)
  frequency = interrupt_counter / (t_delta_ms / 1000.0)
  return frequency

  # 3. Measure the number of pulses and time since the last time
  # this function was called (non-blocking). Values with this method seem
  # too low (gets better the longer the blynk_event_loop co-routine sleeps).
  
  current_time_ms = time.ticks_ms()
  t_delta = time.ticks_diff(current_time_ms, counter_start_time_ms)
  frequency = interrupt_counter / (t_delta / 1000.0)
  print('t_delta=%d, interrupt_counter=%d' % (t_delta, interrupt_counter))
  interrupt_counter = 0
  counter_start_time_ms = time.ticks_ms()
  return frequency
  """
  interrupt_counter = 0
  t_delta_ms = 500
  time.sleep_ms(t_delta_ms)
  frequency = interrupt_counter / (t_delta_ms / 1000.0)
  return frequency


def read_temp_in(convert=True):
  try:
    if convert:
      ds.convert_temp()
      time.sleep_ms(750)
    temp = ds.read_temp(addresses[0])
    print("Temp in=%.1fC" % temp)
    blynk.virtual_write(0, temp)
    """
    Need to handle CRC error
    File "ds18x20.py", line 29, in read_scratch
    Exception: CRC error
    """
  except:
    pass


def read_temp_out(convert=True):
  try:
    if convert:
      ds.convert_temp()
      time.sleep_ms(750)
    temp = ds.read_temp(addresses[1])
    print("Temp out=%.1fC" % temp)
    blynk.virtual_write(1, temp)
  except:
    pass


def read_frequency():
  frequency = round(get_frequency())
  print('frequency=%d' % frequency)
  blynk.virtual_write(2, frequency)
  
  
@blynk.VIRTUAL_WRITE(3)
def duty_cycle_write_handler(value):
  duty_cycle = int(float(value[0]) / 100 * 1023)
  fan.duty(duty_cycle)
  print('duty_cycle=%d' % duty_cycle)


@blynk.VIRTUAL_READ(4)
def read_temp():
  temp = si7021_sensor.temperature()
  print("Temp=%.1fC" % temp)
  blynk.virtual_write(4, temp)


@blynk.VIRTUAL_READ(5)
def read_humidity():
  hum = si7021_sensor.humidity()
  print("Humidity=%.1f%%" % hum)
  blynk.virtual_write(5, hum)
  

async def update_frequency(sleep_s=1):
  while True:
    read_frequency()
    await asyncio.sleep(sleep_s)
    

async def update_temperatures(sleep_s=10):
  convert_s = 0.75
  while True:
    ds.convert_temp()
    await asyncio.sleep(convert_s)
    read_temp_in(False)
    read_temp_out(False)
    read_temp()
    read_humidity()
    if sleep_s > convert_s:
      await asyncio.sleep(sleep_s - convert_s)


async def blynk_event_loop(sleep_s=0.1):
  while True:
    blynk.run()
    await asyncio.sleep(sleep_s)


loop = asyncio.get_event_loop()
loop.create_task(blynk_event_loop(0.1))
loop.create_task(update_frequency(1))
loop.create_task(update_temperatures(10))
loop.run_forever()
