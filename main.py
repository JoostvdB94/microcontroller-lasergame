import machine, neopixel, time
import uasyncio as asyncio
from machine import Pin
from gun import Gun
from target import Target
from suit import Suit
from player import Player

import network
wlan = network.WLAN(network.STA_IF); wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect("Wokwi-GUEST", "") # Connect to an AP
    while not wlan.isconnected():
        pass

## Normally not needed, only because of wokwi
## Use a lib folder when building instead
try:
    import iotc
except:
    import upip
    upip.install('micropython-iotc')
    upip.install('itertools')
    import iotc

#pins
neopixel_pin_number=27
ir_led_pin_number=13
ir_recv_pin_number=23
trigger_btn_pin_number=26

neopixel_count=16 + 3

## IR led cannot be configured multiple times
## See https://github.com/micropython/micropython/issues/10609
from nec_tx import NEC
from nec_rx import NEC_16
ir_led_pin = Pin(ir_led_pin_number, Pin.OUT)
ir_led = NEC(ir_led_pin)
team=1

class Game:
    friendly_fire_enabled = True
    initial_hp = 10
    initial_ammo = 10

    def __init__(self, team, ir_led):
        self.team = team
        self.gun = Gun(team, self.initial_ammo, ir_led, trigger_btn_pin_number)
        self.target = Target(team, ir_recv_pin_number)
        self.suit = Suit(team, neopixel_pin_number, neopixel_count)
        self.player = Player(team, self.initial_hp)

        self.target.set_on_hit(self.hit_action)
        self.player.set_killed(self.killed_action)
        self.event_loop = asyncio.new_event_loop()
        self.event_loop.run_forever()


    def killed_action(self):
        print("Game Over!")
        self.gun.set_ammo(0)
        self.event_loop.create_task(self.suit.defeated())

    def hit_action(self, shot_by_team):
        if self.player.get_healthpoints() > 0:
            self.player.hit(1)
            print("Got shot by {}".format(shot_by_team))
            self.event_loop.create_task(self.suit.single_flash(shot_by_team))

    def get_telemetry(self):
        return {
            "healthpoints": self.player.get_healthpoints(),
            "ammo": self.gun.get_ammo()
        }

    def __del__(self):
        self.event_loop.stop()
        del self.event_loop
        self.suit.reset()
        del self.suit
        del self.gun
        del self.target
        del self.player

## Setup IoTC
from iotc import IoTCClient,IoTCConnectType,IoTCLogLevel, IoTCEvents
conn_type=IoTCConnectType.SYMM_KEY # or use DEVICE_KEY if working with device keys
id_scope = "0ne009A4B9A"
device_id = "iotc_test_device"
sasKey = "B2sbySedhL23G4QKikfCLUNNvLpWLiVjAyPR7PDMQxrPmuBMoAMJxBebOZ4g/6L2ygjztDixPGGH78/0nMLMKw==" # or use device key directly


# Create!
client=IoTCClient(id_scope, device_id, conn_type, sasKey)
client.set_model_id('dtmi:iotcJvdbSaxion:lasergame_v_1_0;1')
client.set_log_level(IoTCLogLevel.ALL)

# Tell controller what to do with properties
def on_props(prop_name, prop_value, component):
    print("key: {}, value: {}".format(prop_name, prop_value))
    if prop_name == "team":
      global team
      team = prop_value
      restart_game(team)
      return prop_value
client.on(IoTCEvents.PROPERTIES, on_props)

def on_commands(command):
    print(command.name)
    if command.name == "revive":
        restart_game(team)
        command.reply(command)
        return command.value
    else:
        print("Unknown command '{}'".format(command.name))
client.on(IoTCEvents.COMMANDS, on_commands)

def restart_game(new_team):
    print("Restarting the game")
    global game
    del game
    start_game(new_team)

def start_game(new_team):
    global game
    game = Game(new_team, ir_led)

client.connect()

start_game(team)
while client.is_connected():
    client.listen() # listen for incoming messages
    client.send_telemetry(game.get_telemetry()) # Send Telemetry
    print("Sent telemetry, pausing for a few milliseconds")
    time.sleep_ms(300)