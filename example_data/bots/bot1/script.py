from basebot import BaseBot


class MyBot2(BaseBot):

    def __init__(self):
        BaseBot.__init__(self)
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