
#
# Player: Class for keeping lives
#
class Player:
    def __init__(self, team, initial_hp):
        self.team = team
        self.hp = initial_hp
        self.killed = lambda: print("Game Over!")

    def hit(self, ap):
        if self.hp > 0:
            self.hp -= ap
        if self.hp < 1:
            self.killed()
    
    def add_hp(self, hp):
        self.hp += hp

    def set_killed(self, killed):
        self.killed = killed

    
