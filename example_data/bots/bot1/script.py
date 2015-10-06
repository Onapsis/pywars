from basebot import BaseBot

# Example responses:
#
# Move forwards:
#   return {'ACTION': 'MOVE', 'WHERE': 1}
#
# Move backwards:
#   return {'ACTION': 'MOVE', 'WHERE': -1}
#
# Shooting projectile:
#   return {'ACTION': 'SHOOT', 'VEL': 100, 'ANGLE': 35}
#   # 'VEL' should be a value x, 0 < x < 150
#   # 'ANGLE' should be an x, 10 <= x < 90
#
#
# Do nothing:
#   return None
#
# For full API description and usage please visit the Rules section


class Bot(BaseBot):


    def __init__(self):
        self.previous = None
        self.shoot_pwr = 80

    def on_turn(self, data_dict):
        if data_dict['life'] != 100:
            # I was hit
            return {'ACTION': 'MOVE', 'WHERE': 1}

        if data_dict['feedback']['MISSING'] == None:
            self.shoot_pwr += 8
            self.direction = "RIGHT"
        elif data_dict['feedback']['MISSING'] == 'COLD':
            self.direction = "RIGHT"
            self.shoot_pwr += 1
        elif data_dict['feedback']['MISSING'] == 'WARM':
            if self.previous == "COLD":
                self.direction = "RIGHT"
                self.shoot_pwr += 1
            elif self.previous == "HOT":
                self.direction = "LEFT"
                self.shoot_pwr += 1
        elif data_dict['feedback']['MISSING'] == 'HOT':
            self.direction = "RIGHT"
        self.shoot_pwr += 3
        self.previous = data_dict['feedback']['MISSING']
        return {'ACTION': 'SHOOT', 'VEL': self.shoot_pwr, 'ANGLE': 50}