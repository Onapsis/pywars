from pywars.engine import BotPlayer, PyWarsGameController


def run_match(p1_script, p2_script,
              p1_name="user1", p2_name="user2"):
    bots = [BotPlayer(p1_name, p1_script),
            BotPlayer(p2_name, p2_script)]

    pywars_game = PyWarsGameController(bots)
    for b in bots:
        pywars_game.add_player(b.username, b.script)
    pywars_game.run()

    return pywars_game.json_game_output()
