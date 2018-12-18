import json
import sys
import time
from urllib import request, parse

hostname = "localhost"
port = "8000"

MARKS = {0: "_", 1: "x", 2: "o"}


def main():
    server_address = get_server_address()
    try:
        games = list_games(server_address)
    except Exception as e:
        print(e)
        games = []

    show_games(games)
    valid_ids = set(g["id"] for g in games)

    joined_game = False
    while not joined_game:
        if not games:
            game_to_join = input(
                "There are no games to join. Type 'new' to start a new game:\n"
            )
        else:
            game_to_join = input(
                "Enter 'id' of a game to join. You can start a new game by typing 'new':\n"
            )

        if game_to_join.strip().lower().startswith("new"):
            try:
                game_name = game_to_join.strip().split(maxsplit=1)[1]
            except:
                game_name = ""
            game_id = new_game(server_address, game_name)
            print("created a new game")
            player = 1
        else:
            game_id = parse_int(game_to_join)
            if game_id not in valid_ids:
                print("invalid input")
                continue
            player = 2

        joined_game = True

    game = get_game_status(server_address, game_id)
    waiting_for_other_player = True
    while "winner" not in game:
        if game["next"] != player and waiting_for_other_player:
            print_board(game)
            print("waiting for the other player")
            waiting_for_other_player = False

        if game["next"] == player:
            print_board(game)
            coords = prompt_move(player)
            move = make_move(server_address, game_id, player, coords[0], coords[1])

            if move is not None and move["status"] == "ok":
                waiting_for_other_player = True
            else:
                print("invalid input")

        time.sleep(1)
        game = get_game_status(server_address, game_id)

    print_board(game)
    winner = game["winner"]
    if winner == player:
        print("you win")
    elif winner != 0:
        print("you lose")
    else:
        print("draw")


def prompt_move(player):
    while True:
        coords = input("your turn ({}): ".format(MARKS[player]))
        try:
            coords = coords.strip().split()
            x = int(coords[0].strip())
            y = int(coords[1].strip())
        except:
            print("invalid input")
            continue

        if x < 0 or x > 2 or y < 0 or y > 2:
            print("invalid input")
            continue

        return x, y


def make_move(address, game_id, player, x, y):
    try:
        with request.urlopen(
            address + "/play?game={}&player={}&x={}&y={}".format(game_id, player, x, y)
        ) as response:
            status = parse_json_response(response)
            return status
    except:
        print("invalid input")
    return None


def print_board(game):
    board = []
    if "board" in game:
        for y in game["board"]:
            row = ""
            for x in y:
                row += MARKS[x]
            board.append(row)
    print("\n".join(board))


def get_game_status(address, game_id):
    with request.urlopen(address + "/status?game={}".format(game_id)) as response:
        game = parse_json_response(response)
        return game


def new_game(address, game_name):
    with request.urlopen(
        address + "/start?name={}".format(parse.quote(game_name))
    ) as response:
        game = parse_json_response(response)
        return game["id"]


def parse_int(game_to_join):
    try:
        parsed_int = int(game_to_join.strip())
    except:
        parsed_int = None
    return parsed_int


def show_games(games):
    print("Games:")
    for game in games:
        print("{} {}".format(game["id"], game["name"]))


def list_games(address):
    with request.urlopen(url=address + "/list") as response:
        games = parse_json_response(response)
        return [g for g in games if g["is_empty"] is True]


def parse_json_response(response):
    content = response.read().decode("UTF-8")
    try:
        return json.loads(content)
    except Exception as e:
        print(e)
        return None


def get_server_address():
    server_address = "{}:{}".format(hostname, port)
    if not server_address.startswith("http"):
        server_address = "http://" + server_address
    # print(server_address)
    return server_address


if __name__ == "__main__":
    hostname = sys.argv[1]
    port = sys.argv[2]
    main()
