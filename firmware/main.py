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
import time
import network
import onewire
import ds18x20

import BlynkLib
import uasyncio as asyncio


try:
  from secrets import BLYNK_AUTH, WIFI_SSID, WIFI_PASSWORD
except:
  print('You must create a secrets.py file.')


wifi = network.WLAN(network.STA_IF)
blynk = BlynkLib.Blynk(BLYNK_AUTH, connect=False)
interrupt_counter = 0


def callback(pin):
  """This callback function is attached to an interrupt handler.
  """
  global interrupt_counter
  interrupt_counter = interrupt_counter + 1


# Attach an interrupt to trigger on the falling edge on pin 25.
tach = machine.Pin(25, machine.Pin.IN, machine.Pin.PULL_UP)
tach.irq(trigger=machine.Pin.IRQ_FALLING, handler=callback)


# Setup the fan to use a PWM frequency of 25kHz and a 50% duty cycle.
fan = machine.PWM(machine.Pin(19, machine.Pin.OUT), freq=25000, duty=int(0.5*1023))


ds = ds18x20.DS18X20(onewire.OneWire(machine.Pin(32)))


set_point = 25


onewire_addresses = {'temp_in': 0,
                     'temp_out': bytearray(b'(\xd6G\x8a\x01\x00\x00\xb9'),
                     'temp_panel': bytearray(b'(\xd6ay\x97\t\x03\x8d')
                     }  


virtual_pins = {'temp_in': 0,
                'temp_out': 1,
                'temp_panel': 2
                }


print("Scanning onewire bus...")
print(str(ds.scan()))


@blynk.ON("connected")
def blynk_connected(ping):
    print('Blynk ready. Ping:', ping, 'ms')


@blynk.VIRTUAL_WRITE(3)
def duty_cycle_write_handler(value):
  set_fan_duty_cycle(value[0])


def wifi_connect():
  print("Connecting to WiFi...")
  wifi.active(True)
  wifi.connect(WIFI_SSID, WIFI_PASSWORD)
  print('IP:', wifi.ifconfig()[0])


def set_fan_duty_cycle(value):
  duty_cycle = int(float(value) / 100 * 1023)
  fan.duty(duty_cycle)
  print('duty_cycle=%d' % duty_cycle)


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
  blynk.virtual_write(4, frequency)
  return frequency


def get_temp(label, convert=True):
  if convert:
    ds.convert_temp()
    time.sleep_ms(750)
  if onewire_addresses[label]:
    temp = ds.read_temp(onewire_addresses[label])
    print("%s=%.1fC" % (label, temp))
    blynk.virtual_write(virtual_pins[label], temp)
  else:
    temp = None
  return temp


def get_power():
  temp_in = get_temp('temp_in', False)
  temp_out = get_temp('temp_out', False)
  temp_panel = get_temp('temp_panel', False)

  # only turn on the fan if the panel temp is > 25C
  if temp_panel > set_point:
    set_fan_duty_cycle(100)
  else:
    set_fan_duty_cycle(0)
  # update the fan slider
  blynk.virtual_write(3, fan.duty())

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

  # Hard code temp_in for now
  temp_in = 20

  Qout = flow_rate * air_density * (temp_out - temp_in) * Cp_air * 1000.0 / 60.0
  print("Qout=%.1f W" % Qout)
  blynk.virtual_write(6, Qout)
  return Qout


async def update_sensors(sleep_s=10):
  convert_s = 0.75
  while True:
    print("update_sensors()")
    try:
      get_frequency()
      ds.convert_temp()
      await asyncio.sleep(convert_s)
      get_power() # also triggers get_temp_in() and get_temp_out()
    except Exception as e:
      print('Exception: %s' % e)
    if sleep_s > convert_s:
      await asyncio.sleep(sleep_s - convert_s)


async def blynk_event_loop(sleep_s=.1):
  while True:
    await asyncio.sleep(sleep_s)
    try:
      if not wifi.isconnected():
        print("wifi_connect()")
        blynk.disconnect()
        wifi_connect()
        await asyncio.sleep(5)
      if blynk.state == BlynkLib.DISCONNECTED:
        print("blynk_connect()")
        blynk.connect()
        await asyncio.sleep(5)
      blynk.run()
    except Exception as e:
      print('Exception: %s' % e)


loop = asyncio.get_event_loop()
loop.create_task(blynk_event_loop())
loop.create_task(update_sensors(5))
loop.run_forever()
