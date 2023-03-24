import neopixel
from machine import Pin
import uasyncio as asyncio

class Suit:
    teamcolors=[
        (0, 0, 255),
        (0, 255, 0),
        (255, 0, 255)
    ]

    def __init__(self, team, neopixel_pin_number, neopixel_count):
        self.team = team
        self.neopixel_count = neopixel_count
        self.setup_pins(neopixel_pin_number)
        self.fill_color(self.get_team_color(team))

    def setup_pins(self, neopixel_pin_number):
        np_pin = Pin(neopixel_pin_number, Pin.OUT)
        self.np = neopixel.NeoPixel(np_pin, self.neopixel_count)

    def reset():
        self.should_blink = False
        self.blackout()

    def fill_color(self, color):
        for i in range(0, self.neopixel_count):
            self.np[i] = color
        self.np.write()

    def alternate_color(self, color):
        for i in range(0, self.neopixel_count):
            if i % 2 == 0:
                self.np[i] = color
            else:
                self.np[i] = (0,0,0)
        self.np.write()

    #functions
    def blackout(self):
        for i in range(0, self.neopixel_count):
                self.np[i] = (0,0,0)
        self.np.write()

    async def defeated(self):
        color = self.get_team_color(self.team)
        self.should_blink = True
        while self.should_blink:
            self.alternate_color(color)
            await asyncio.sleep(1)
            self.blackout();
            await asyncio.sleep(1)
        self.blackout()

    async def single_flash(self, team):
        self.blackout()
        await asyncio.sleep_ms(20)
        self.fill_color(self.get_team_color(team))
        await asyncio.sleep_ms(100)
        self.fill_color(self.get_team_color(self.team))

    def get_team_color(self, team):
        if team <= len(self.teamcolors) and team > 0:
            return self.teamcolors[self.team -1]
        else:
            raise Exception("Zero or negative teams are not allowed")