from basebot import BaseBot


class MyBot(BaseBot):

    def __init__(self):
        BaseBot.__init__(self)

    def on_turn(self, data_dict):
        return {'ACTION': 'MOVE', 'WHERE': 1}