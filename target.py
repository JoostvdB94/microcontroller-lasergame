from machine import Pin
from nec_rx import NEC_16
from ir_codes import get_team

#
# Target class: 
# Only contains logic for being shot
#
class Target:
    ir_recv = None

    def __init__(self, team, ir_recv_pin_number):
        self.team = team
        self.setup_pins(ir_recv_pin_number)
        self.on_hit = lambda hit_by_team: print("Got hit by member of team {}".format(hit_by_team))
    
    def setup_pins(self, ir_recv_pin_number):
        ir_recv_pin = Pin(ir_recv_pin_number, Pin.IN)
        self.ir_recv = NEC_16(ir_recv_pin, self.ir_received)

    # Callback for when an IR Signal is received
    def ir_received(self, data, addr, ctrl):
        if data < 0:  # NEC protocol sends repeat codes.
            print('Repeat code.')
        else:
            data = '{:02x}'.format(data)
            shot_by_team = get_team(data)
            if shot_by_team >= 0:
                self.on_hit(shot_by_team)
            else: 
                print("Unknown signal received from IR Sensor {}".format(data))
    
    def set_on_hit(self, on_hit):
        self.on_hit = on_hit