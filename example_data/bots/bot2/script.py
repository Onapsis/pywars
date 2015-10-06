from basebot import BaseBot


class Mybot(BaseBot):

    def __init__(self):
        BaseBot.__init__(self)

    def on_turn(self, data_dict):
        return {'ACTION': 'MOVE', 'WHERE': 1}
        #return {'ACTION': 'SHOOT', 'VEL': 100, 'ANGLE': 35}


# class Bot(object):
#     def evaluate_turn(self, feedback, life):
#         A = 1
#         B = 2
#         C = 3
#         self.next_action = getattr(self, 'next_action', A)
#         self.previous_action = getattr(self, 'previous_action', None)
#         if self.next_action == A:
#             if self.previous_action == A:
#                 self.next_action = B
#             self.previous_action = A
#             return {'ACTION': 'MOVE', 'WHERE': 1}
#         elif self.next_action == B:
#             self.next_action = C
#             self.previous_action = B
#             return {'ACTION': 'SHOOT', 'VEL': 10, 'ANGLE': 35}
#         elif self.next_action == C:
#             self.next_action = A
#             self.previous_action = C
#             return {'ACTION': 'MOVE', 'WHERE': -1}
#         else:
#             return {'ACTION': 'SHOOT', 'VEL': 10, 'ANGLE': 30}
