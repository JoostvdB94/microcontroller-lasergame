from helpers import Button
from machine import Pin
from nec_tx import NEC
from ir_codes import get_code

class Gun:
    ir_led = None
    ammo = 0
    shot_count=0

    def __init__(self, team, initial_ammo, ir_led, trigger_btn_pin_number):
        self.team = team
        self.ammo = initial_ammo
        self.ir_led = ir_led
        self.setup_pins(trigger_btn_pin_number)
        self.on_shoot = lambda: print("Shot fired!")

    def setup_pins(self, trigger_btn_pin_number):
        button_pin = Pin(trigger_btn_pin_number, Pin.IN, Pin.PULL_UP)
        self.button_handler = Button(pin=button_pin, callback=self.shoot)

    def shoot(self,pin): 
        if self.can_shoot():
            self.ir_led.transmit(0,30)
            self.ammo -= 1
            self.on_shoot()
    
    def set_ammo(self, ammo):
        self.ammo = ammo

    def get_ammo(self):
        return self.ammo

    def set_on_shoot(self, on_shoot):
        self.on_shoot = on_shoot

    def can_shoot(self):
        return self.ammo > 0;

    def __del__(self):
        del self.ir_led
        