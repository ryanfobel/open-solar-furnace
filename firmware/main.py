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


# Initialize the fan duty cycle.
blynk.virtual_write(3, fan.duty() / 1023.0 * 100)

@blynk.ON("connected")
def blynk_connected(ping):
    print('Blynk ready. Ping:', ping, 'ms')

 
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
  print('frequency=%.0f' % frequency)
  blynk.virtual_write(2, frequency)
  return frequency


def get_temp_in(convert=True):
  if convert:
    ds.convert_temp()
    time.sleep_ms(750)
  temp = ds.read_temp(addresses[0])
  print("Temp in=%.1fC" % temp)
  blynk.virtual_write(0, temp)
  return temp


def get_temp_out(convert=True):
  if convert:
    ds.convert_temp()
    time.sleep_ms(750)
  temp = ds.read_temp(addresses[1])
  print("Temp out=%.1fC" % temp)
  blynk.virtual_write(1, temp)
  return temp

@blynk.VIRTUAL_WRITE(3)
def duty_cycle_write_handler(value):
  duty_cycle = int(float(value[0]) / 100 * 1023)
  fan.duty(duty_cycle)
  print('duty_cycle=%d' % duty_cycle)


@blynk.VIRTUAL_READ(4)
def get_temp():
  temp = si7021_sensor.temperature()
  print("Temp=%.1fC" % temp)
  blynk.virtual_write(4, temp)
  return temp


@blynk.VIRTUAL_READ(5)
def get_humidity():
  humidity = si7021_sensor.humidity()
  print("Humidity=%.1f%%" % humidity)
  blynk.virtual_write(5, humidity)
  return humidity
  

def get_power():
  temp_in = get_temp_in(False)
  temp_out = get_temp_out(False)

  # Use the fan's rated flow rate from the datasheet scaled by the duty
  # cycle. We could probably calibrate this based on the tachometer signal,
  # which seems to change when the air flow is restricted.
  flow_rate = fan.duty() / 100.0 * 3 # m^3/min
  
  """
  https://builditsolar.com/References/Measurements/CollectorPerformance.htm

  # https://www.engineeringtoolbox.com/air-properties-d_156.html
  air_density = 1.208 kg/m^3
  
  Air density increases as it is heated. Use the same correction factor
  as builditsolar.com page for now (1.208 * 0.065 / 0.075 = 1.047 kg/m^3).
  
  Qout = (flow_rate)*(air_density)*(temp_out - temp_in)*(Cp_air)
  Qout = (0.6 m^3/min)(1.047 kg/m^3)(30C - 20C)(1.006 kJ/kgK)
  Qout = (7.29 kJ/min)*(1000 J/kJ)*(1/60 min/s)
  Qout = 105 W
  """
  air_density = 1.208 * (.065 / .075)
  
  # Specific heat capacity of air (should also correct for temperature:
  # https://www.ohio.edu/mechanical/thermo/property_tables/air/air_Cp_Cv.html).
  # Should we be using Cp or Cv (constant pressure or constant volume)?
  Cp_air = 1.006 # kJ/kgK

  # Hard code temp_in for now (since it is the same as temp_out)
  temp_in = min(20, temp_in)

  Qout = flow_rate * air_density * (temp_out - temp_in) * Cp_air * 1000.0 / 60.0
  print("Qout=%.1f W" % Qout)
  blynk.virtual_write(6, Qout)
  return Qout


async def update_sensors(sleep_s=10):
  convert_s = 0.75
  while True:
    try:
      get_frequency()
      get_temp()
      get_humidity()
      ds.convert_temp()
      await asyncio.sleep(convert_s)
      get_power() # also triggers get_temp_in() and get_temp_out()
    except:
      pass
    if sleep_s > convert_s:
      await asyncio.sleep(sleep_s - convert_s)


async def blynk_event_loop(sleep_s=0.1):
  while True:
    blynk.run()
    await asyncio.sleep(sleep_s)

def start_event_loop():
  try:
    del loop
  except:
    pass
  loop = asyncio.get_event_loop()
  loop.create_task(blynk_event_loop(0))
  loop.create_task(update_sensors(10))
  loop.run_forever()
  
start_event_loop()

