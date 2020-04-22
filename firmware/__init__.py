"""
Code for controlling a PC fan (model # FFC0912DE-TP04)
using an ESP32 board.

# Hookup:

* red wire to +12V
* black wire to GND
* yellow wire to pin 19
* blue wire to pin 25

# Library dependencies:

* BlynkLib
* BlynkTimer
* si7021
* uasyncio
* umqtt

# References:

* https://techtutorialsx.com/2017/10/07/esp32-micropython-timeimport webrepl_setupr-interrupts/
* http://partner.delta-corp.com/Products/FanUploads/Specification/FFC0912DE-TP04.pdf
* DS18B20: https://www.adafruit.com/product/381
* si7021: https://bitbucket.org/thesheep/micropython-si7021
"""

import machine
import time
import network
import onewire
import ds18x20
import json

import BlynkLib
import uasyncio as asyncio
from umqtt.robust import MQTTClient
from supervisor import BaseService, get_env


try:
    env = json.load(open('env.json', 'r'))
except OSError:
    print('You must create an env.json file.')


interrupt_counter = 0

keys = ['temp_in',         # v0
        'temp_out',        # v1
        'temp_panel',      # v2
        'fan_duty_cycle',  # v3
        'fan_frequency',   # v4
        'power']           # v5

data = dict(zip(keys, [0]*len(keys)))
virtual_pins = dict(zip(keys, range(len(keys) + 1)))


def callback(pin):
  # This callback function is attached to an interrupt handler.
  global interrupt_counter
  interrupt_counter = interrupt_counter + 1


# Attach an interrupt to trigger on the falling edge on pin 25.
tach = machine.Pin(25, machine.Pin.IN, machine.Pin.PULL_UP)
tach.irq(trigger=machine.Pin.IRQ_FALLING, handler=callback)


class Service(BaseService):

    # Setup the fan to use a PWM frequency of 25kHz and a 50% duty cycle.
    fan = machine.PWM(machine.Pin(19, machine.Pin.OUT), freq=25000, duty=int(0.5*1023))
    ds = ds18x20.DS18X20(onewire.OneWire(machine.Pin(32)))

    # Setup
    def __init__(self):
        super().__init__()

        self.wifi = network.WLAN(network.STA_IF)
        
        self.mqtt_client = MQTTClient(self.env['MQTT_CLIENT_ID'],
                                      self.env['MQTT_HOST'],
                                      user=self.env['MQTT_USER'],
                                      password=self.env['MQTT_PASSWORD'])
        self._loop.create_task(self.blynk_event_loop())
        self._loop.create_task(self.update_sensors(5))

        self.onewire_addresses = {'temp_in': None,
                                  'temp_out': bytearray(b'(\xd6G\x8a\x01\x00\x00\xb9'),
                                  'temp_panel': bytearray(b'(\xd6ay\x97\t\x03\x8d')
                                  }

        self.logger.info("Scanning onewire bus...")
        self.logger.info(str(self.ds.scan()))

    def wifi_connect(self):
        self.logger.info("Connecting to WiFi...")
        self.wifi.active(True)
        self.wifi.connect(env['WIFI_SSID'], env['WIFI_PASSWORD'])
        self.logger.info('IP:', wifi.ifconfig()[0])

    def mqtt_connect(self):
        self.mqtt_client.connect()

    @classmethod
    def set_fan_duty_cycle(cls, value):
      cls.logger.debug('set_fan_duty_cycle(%s)' % value)
      duty_cycle = int(float(value) / 100 * 1023)
      cls.fan.duty(duty_cycle)

    @staticmethod
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

    @classmethod
    def get_temperatures(cls, convert=True):
        output = {}
        try:
            if convert:
                cls.ds.convert_temp()
                time.sleep_ms(750)
            for label, address in onewire_addresses.items():
                if address:
                    output[label] = cls.ds.read_temp(address)
                else:
                    output[label] = None
        except onewire.OneWireError:
            pass
        return output

    @classmethod
    def get_power(cls):
        global data

        # only turn on the fan if the panel temp is > 25C
        if data['temp_panel'] > 25:
            cls.set_fan_duty_cycle(75)
        else:
            cls.set_fan_duty_cycle(0)

        # Use the fan's rated flow rate from the datasheet scaled by the duty
        # cycle. We could probably calibrate this based on the tachometer signal,
        # which seems to change when the air flow is restricted.
        flow_rate = cls.fan.duty() / 100.0 * 3 # m^3/min
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

        Qout = flow_rate * air_density * (data['temp_out'] - data['temp_in']) * Cp_air * 1000.0 / 60.0
        return Qout

    async def update_sensors(self, sleep_s=10):
        global data

        convert_s = 0.75
        while True:
            if self.state == 'running':
                self.logger.debug("update_sensors()")
                try:
                    data['fan_frequency'] = self.get_frequency()
                    data['fan_duty_cycle'] = int(self.fan.duty() / 1023.0 * 100)

                    data.update(self.get_temperatures())

                    # Hard code temp_in for now
                    data['temp_in'] = 20
                    data['power'] = self.get_power()

                    self.logger.debug(repr(data))

                    # If we're connected to the blynk server, push out updates
                    if blynk.state == BlynkLib.CONNECTED:
                        for label, pin in virtual_pins.items():
                            blynk.virtual_write(pin, data[label])

                    # Try to publish updates over mqtt
                    try:
                        self.mqtt_client.ping()
                        self.mqtt_client.publish('open-solar-furnace/%s' % self.env['MQTT_CLIENT_ID'], json.dumps(data))
                    except:
                        pass
                except Exception as e:
                    self.logger.error('Exception: %s' % e)
                if sleep_s > convert_s:
                    await asyncio.sleep(sleep_s - convert_s)
            else:
              await asyncio.sleep(1)

    async def blynk_event_loop(self, sleep_s=.1):
        while True:
            if self.state == 'running':
                await asyncio.sleep(sleep_s)
                try:
                    if not self.wifi.isconnected():
                        self.logger.debug('blynk.disconnnect()')
                        blynk.disconnect()
                        self.logger.debug('wifi.connect()')
                        self.wifi_connect()
                        await asyncio.sleep(5)
                    if self.mqtt_client.sock is None:
                        self.logger.debug('mqtt_connect()')
                        self.mqtt_connect()
                    if blynk.state == BlynkLib.DISCONNECTED:
                        self.logger.info("blynk_connect()")
                        blynk.connect()
                        await asyncio.sleep(5)
                    blynk.run()
                except Exception as e:
                    self.logger.error('Exception: %s' % e)
            else:
                await asyncio.sleep(sleep_s)

blynk = BlynkLib.Blynk(get_env(Service.__module__)['BLYNK_AUTH'], connect=False)

@blynk.VIRTUAL_WRITE(3)
def duty_cycle_write_handler(value):
    Service.set_fan_duty_cycle(value[0])

@blynk.ON("connected")
def blynk_connected(ping):
    print('Blynk ready. Ping:', ping, 'ms')
