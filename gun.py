from helpers import Button
from machine import Pin
from nec_tx import NEC
from ir_codes import get_code

class Gun:
    ir_led = None
    ir_recv = None
    ammo = 0
    shot_count=0

    def __init__(self, team, initial_ammo, ir_led_pin_number, trigger_btn_pin_number):
        self.team = team
        self.ammo = initial_ammo
        self.setup_pins(ir_led_pin_number, trigger_btn_pin_number)
        self.on_shoot = lambda: print("Shot fired!")

    def setup_pins(self, ir_led_pin_number, trigger_btn_pin_number):
        ir_led_pin = Pin(ir_led_pin_number, Pin.OUT)
        self.ir_led = NEC(ir_led_pin)

        button_pin = Pin(trigger_btn_pin_number, Pin.IN, Pin.PULL_UP)
        self.button_handler = Button(pin=button_pin, callback=self.shoot)

    def shoot(self,pin): 
        if self.can_shoot():
            self.ir_led.transmit(0,30)
            self.ammo -= 1
            self.on_shoot()
    
    def set_ammo(self, ammo):
        self.ammo = ammo

    def set_on_shoot(self, on_shoot):
        self.on_shoot = on_shoot

    def can_shoot(self):
        return self.ammo > 0;
        