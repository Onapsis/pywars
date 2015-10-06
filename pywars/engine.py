# encoding=utf-8

import json
import pprint
import math
import random
from turnboxed.gamecontroller import BaseGameController


class InvalidBotOutput(Exception):
    reason = u'Invalid output'
    pass


class BotTimeoutException(Exception):
    reason = u'Timeout'
    pass


class MissedTargetException(Exception):
    pass


class TankDestroyedException(Exception):
    reason = u'Tank Destroyed'
    pass


class GameOverException(Exception):
    pass

# Exit error codes
EXIT_ERROR_NUMBER_OF_PARAMS = 1
EXIT_ERROR_MODULE = 2
EXIT_ERROR_BOT_INSTANCE = 3

# Relation between our grid and the coordinates in [m]
SCALE = 60

# Constants we use in the game
FREE = 0
DAMAGE_DELTA = 25
REPAIR_DELTA = 10
INITIAL_HEALTH = 100
FAILED = 'FAILED'
SUCCESS = 'SUCCESS'
LOSER = 'loser'
WINNER = 'winner'
DRAW = 'draw'
RESULT = 'result'
ACTION = 'action'
TANK_LENGTH = 3
# Map each firing result threshold with its feedback
HOT = 'HOT'
WARM = 'WARM'
COLD = 'COLD'


def _resolve_missing(distance):
    if distance <= 3:
        return HOT
    elif distance <= 8:
        return WARM
    else:
        return COLD


def _x_for_players(players, limit):
    """Given the list of players, return the numbers which will indicate the
    initial position of each one, according to the formula."""
    half = limit // 2
    p1_x = random.choice(range(1, half))
    p2_x = random.choice(range(half + 1, limit))
    print "PLAYER POSITIONS: ", p1_x, p2_x
    return p1_x, p2_x

def shoot_projectile(speed, angle, starting_height=0.0, gravity=9.8, x_limit=1000):
    '''
    returns a list of (x, y) projectile motion data points
    where:
    x axis is distance (or range) in meters
    y axis is height in meters
    :x_limit: Indicates if the trajectory is going out of the grid
    '''
    angle = math.radians(angle)
    distance = (speed ** 2) * math.sin(2*angle) / gravity
    return [(0, 0), (distance, 0)]


class ArenaGrid(object):
    """
    The grid that represents the arena over which the players are playing.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.arena = [FREE for _ in xrange(self.width)]

    def copy_for_player(self):
        """Return just a copy of the portion we provide to the player."""
        return self.arena[:]

    def players_distance(self):
        """Return the distance between the bots. Only two players."""
        p1, p2 = [i for i in xrange(self.width) if self.arena[i] != FREE]
        return p2 - p1

    def __getitem__(self, (x, y)):
        return self.arena[x]

    def __setitem__(self, (x, y), value):
        self.arena[x] = value


class PywarsArena(object):
    """The game arena."""

    PLAYING = 0
    LOST = 1
    WINNER = 2

    def __init__(self, players, width=30, height=50):
        self.width = width
        self.height = height
        self.rounds = xrange(100)
        self.players = players
        self.match = PywarsGroundMatchLog(width, height, players)
        self.arena = ArenaGrid(self.width, self.height)
        self.setup()

    def setup(self):
        self.match.trace_action(dict(action="new_arena",
                                     width=self.width,
                                     height=self.height,))
        #if self.randoms:
        #    x1, x2 = map(int, self.randoms)
        #else:
        x1, x2 = _x_for_players(self.players, limit=self.width)
        for i, player in enumerate(self.players, start=1):
            player.color = i
            player.status = self.PLAYING
            # Initial position
            x = x1 if i % 2 != 0 else x2
            y = 0
            self.setup_new_player(player, x, y, self.width)

    def setup_new_player(self, player, x, y, width):
        """Register the new player at the (x, y) position on the arena."""
        player.x, player.y = x, y
        self.arena[x, y] = player.color
        x_factor = 1 if x <= (width // 2) else -1
        player.assign_team(x_factor)
        player.move_feedback(ok=True)
        self.match.trace_action(dict(action="new_player",
                                     name=player.username,
                                     position=[x * SCALE, y],
                                     tank=player.username,
                                     ))

    def _check_player_boundaries(self, player, new_x):
        assert player.x_factor in [-1, 1]
        half = self.width // 2
        if player.x_factor == 1:
            #Do not include half for ANY player, to avoid crashes
            return 0 <= new_x < half
        #player.x_factor == -1, idem: half is not valid location:
        return half < new_x < self.width

    def resolve_move_action(self, player, where):
        new_x = player.x + (player.x_factor * where)
        if self._check_player_boundaries(player, new_x):
            self.arena[player.x, player.y] = FREE
            player.x = new_x
            self.arena[player.x, player.y] = player.color
            # Tell the user it moved successfully
            player.move_feedback(ok=True)
        else:
            player.move_feedback(ok=False)
        # Trace what just happened in the match
        self.match.trace_action(dict(action="make_move",
                                     player=player.username,
                                     position=[player.x * SCALE, player.y], ))

    def adjust_player_shoot_trajectory(self, player, trajectory):
        """Depending on which side of the arena :player: is, we need or not to
        reverse the x coordinates.
        Calibrate according to the position of :player:"""
        if player.x_factor == -1:  # Side B, symetric x
            trajectory = trajectory[::-1]
        initial_x = trajectory[0][0]  # x of the first coord
        delta_x = player.x - initial_x
        trajectory = [(x + delta_x, y) for x, y in trajectory]
        #x_off = lambda i: int(i) if player.x_factor == -1 else int(i)
        #return [(int(x), int(y)) for x, y in trajectory]
        initial_x = player.x
        shoot_x = initial_x + int((trajectory[1][0] )/SCALE)

        shoot = [(initial_x,0) ,( shoot_x,0)]
        #print_msg("SHOOT %s Factor %s Trajectory %s" % (shoot, player.x_factor, trajectory[1][0]))
        return shoot

    def _scale_coords(self, (x, y)):
        """Given impact coords (x, y), translate their numbers to our arena
        grid.
        Current Scale: 1m² per grid cell"""
        if y <= 3:
            y = 0
        return int(round(x)), int(round(y))

    def get_adjusted_angle(self, player, angle):
        if (player.x_factor == -1):
            return angle + 90
        return angle

    def resolve_shoot_action(self, player, speed, angle):
        trajectory = shoot_projectile(speed, angle, x_limit=self.width)
        trajectory = self.adjust_player_shoot_trajectory(player, trajectory)
        #print "TRAJECTORY: ", trajectory
        x_m_origen, x_m_destino = trajectory[0][0], trajectory[1][0]

        # Log the shoot made by the player
        self.match.trace_action(dict(action="make_shoot",
                                     player=player.username,
                                     angle=self.get_adjusted_angle(player, angle),
                                     speed=speed,
                                     trajectory=trajectory,
                                     ))
        # Get the impact coordinates
        #x_imp, y_imp = self._scale_coords(trajectory[-1])
        # Correct x_imp according to our scale
        x_imp = x_m_destino
        try:
            affected_players = [p for p in self.players if p.x == x_imp]
            if not affected_players:
                raise MissedTargetException
        except MissedTargetException:
            other_x = [p.x for p in self.players if p is not player][0]
            difference = (x_imp - other_x) * player.x_factor
            player.shoot_feedback(ok=False, difference=difference)
        else:
            player.shoot_feedback(ok=True)
            for p in affected_players:
                p.decrease_life(DAMAGE_DELTA)
                self.match.trace_action(dict(action="make_healthy",
                                             player=p.username,
                                             health_value=p.life))


class PywarsGroundMatchLog(object):
    """Represents the match log among players, the entire game."""

    def __init__(self, width, height, players):
        self.width = width
        self.height = height
        self.players = players
        self.trace = []   # All actions performed during the match
        self.game_over_template = {ACTION: RESULT,
                                   WINNER: None,
                                   LOSER: None,
                                   DRAW: False,
                                   'reason': ''}

    def trace_action(self, arena_action):
        """Receive an action performed on the arena, and log it as a part of
        the match."""
        self.trace.append(arena_action)

    def draw(self):
        self.game_over_template[DRAW] = True
        self.trace_action(self.game_over_template)

    def winner(self, player):
        player.status = PywarsArena.WINNER
        self._trace_game_over(WINNER, LOSER, player, 'Max points')

    def lost(self, player, cause):
        player.status = PywarsArena.LOST
        self._trace_game_over(LOSER, WINNER, player, cause)

    def _trace_game_over(self, k1, k2, player, cause):
        self.game_over_template[k1] = player.username
        self.game_over_template['reason'] = cause
        others = ','.join(p.username for p in self.players if p is not player)
        self.game_over_template[k2] = others
        self.trace_action(self.game_over_template)

    def __json__(self):
        data = dict(width=self.width,
                    height=self.height,
                    players=[player.username for player in self.players],
                    actions=self.trace,
                    )
        return data


class PyWarsGameController(BaseGameController):

    def __init__(self, bots):
        BaseGameController.__init__(self)
        self.bots = bots
        self.rounds = 100
        self.arena = PywarsArena(players=bots)

    def get_bot(self, bot_cookie):
        bot_name = self.players[bot_cookie]['player_id']
        for b in self.bots:
            if b.username == bot_name:
                return b
        return None

    def json_game_output(self):
        return json.dumps(self.arena.match.__json__())

    def evaluate_turn(self, request, bot_cookie):
        # Game logic here. Return should be an integer."
        bot = self.get_bot(bot_cookie)
        #print "BOT STATUS: ", request, bot.username, bot.x_factor, bot.x, bot.x_factor, bot.life
        if "EXCEPTION" in request.keys():
            # bot failed in turn
            self.arena.match.lost(bot, request['EXCEPTION'])
            self.log_msg("EXCP: Tank destroyed: " + request['EXCEPTION'])
            self.stop()
        elif request['MSG'] is None:
            bot.heal()
        else:
            try:
                if request['MSG']['ACTION'] == 'SHOOT':
                    self.arena.resolve_shoot_action(bot, request['MSG']['VEL'], request['MSG']['ANGLE'])
                elif request['MSG']['ACTION'] == 'MOVE':
                    self.arena.resolve_move_action(bot, request['MSG']['WHERE'])
                else:
                    # heal
                    bot.heal()
            except TankDestroyedException, e:
                self.arena.match.lost(bot, e.reason)
                self.log_msg("Tank destroyed: " + str(e))
                self.stop()
        return -1

    def get_turn_data(self, bot_cookie):
        bot = self.get_bot(bot_cookie)
        # this should return the data sent to the bot
        # on each turn
        #pprint.pprint(self.players[bot_cookie]['player_id'])
        bot_id = self.players[bot_cookie]['player_id']
        f = {"feedback": bot.feedback, "life": bot.life}
        self.log_msg("FEEDBACK: " + str(f))
        return f


class BotPlayer(object):

    def __init__(self, bot_name, script):
        self.script = script
        self.x_factor = None
        self.username = bot_name
        self.feedback = {'RESULT': None, 'POSITION': None, 'MISSING': None}
        self.x = 0
        self.y = 0
        self.life = 100

    def move_feedback(self, ok=True):
        self.feedback['RESULT'] = SUCCESS if ok else FAILED
        self.feedback['POSITION'] = (self.x, self.y) if ok else None
        self.feedback['MISSING'] = None

    def shoot_feedback(self, ok=True, difference=0):
        """:difference: How long the shoot was missed"""
        self.feedback['RESULT'] = SUCCESS if ok else FAILED
        self.feedback['POSITION'] = None
        if not ok:
            self.feedback['MISSING'] = _resolve_missing(difference)
        else:
            self.feedback['MISSING'] = None

    def decrease_life(self, damage_delta):
        self.life -= damage_delta
        if self.life <= 0:
            raise TankDestroyedException(self.username + " Destroyed")

    def heal(self):
        if self.life + REPAIR_DELTA <= INITIAL_HEALTH:
            self.life += REPAIR_DELTA
        else:
            self.life = INITIAL_HEALTH

    def assign_team(self, x_factor):
        """Assign team depending on which side is allocated
        x_factor -> -1 | 1"""
        self.x_factor = x_factor