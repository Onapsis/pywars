from basebot import BaseBot


class Mybot(BaseBot):

    def __init__(self):
        BaseBot.__init__(self)
        self.shoot_pwr = 80
        self.direction = "RIGHT"
        self.previous = None


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

# class Bot(object):
#     def evaluate_turn(self, feedback, life):
#         """Move until it is no longer possible and then shoot"""
#         self.previous_action = getattr(self, 'previous_action', None)
#         MOVE = 1
#         FIRE = 2
#         if self.previous_action == MOVE and feedback == 'FAILED':
#             self.previous_action = FIRE
#             return {'ACTION': 'SHOOT', 'VEL': 10, 'ANGLE': 35}
#         else:
#             self.previous_action = MOVE
#             return {'ACTION': 'MOVE', 'WHERE': 1}
