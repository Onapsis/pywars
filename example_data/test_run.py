import sys
from pywars.engine import BotPlayer, PyWarsGameController


def main(argv):
    bot1_username = "user1"
    bot2_username = "user2"
    bots = [BotPlayer(bot1_username, argv[0]),
            BotPlayer(bot2_username, argv[1])]

    pywars_game = PyWarsGameController(bots)
    for b in bots:
        pywars_game.add_player(b.username, b.script)
    pywars_game.run()

    json_data = pywars_game.json_game_output()
    print(json_data)

    sys.exit(0)


if __name__ == "__main__":
    main(["/tmp/tmphytOj1/bot1/script.py", "/tmp/tmphytOj1/bot2/script.py"])
