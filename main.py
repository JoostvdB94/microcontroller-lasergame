import machine, neopixel, time
import uasyncio as asyncio
from machine import Pin
from gun import Gun
from target import Target
from suit import Suit
from player import Player

neopixel_count=19

#pins
neopixel_pin_number=27
ir_led_pin_number=13
ir_recv_pin_number=23
trigger_btn_pin_number=26

class Game:
    friendly_fire_enabled = True
    initial_hp = 10
    initial_ammo = 10

    def __init__(self, team):
        self.team = team
        self.event_loop = asyncio.get_event_loop()
        self.gun = Gun(team, self.initial_ammo, ir_led_pin_number, trigger_btn_pin_number)
        self.target = Target(team, ir_recv_pin_number)
        self.suit = Suit(team, neopixel_pin_number, neopixel_count)
        self.player = Player(team, self.initial_hp)

        self.target.set_on_hit(self.hit_action)
        self.player.set_killed(self.killed_action)

    def killed_action(self):
        print("Game Over!")
        self.gun.set_ammo(0)
        asyncio.run(self.suit.defeated())

    def hit_action(self, shot_by_team):
        self.player.hit(1)
        print("Got shot by {}".format(shot_by_team))
        asyncio.run(self.suit.single_flash(shot_by_team))

    def start(self):
        self.event_loop.run_forever()

    def __del__(self):
        self.event_loop.stop()
        self.suit.reset()

game = Game(1)
game.start()
print("Started")
