from basebot import BaseBot


class Mybot(BaseBot):

    def __init__(self):
        BaseBot.__init__(self)

    def on_turn(self, msg):
        return {'ACTION': 'SHOOT', 'VEL': 100, 'ANGLE': 50}

a = Mybot()

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
