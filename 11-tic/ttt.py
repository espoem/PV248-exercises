import os
import socketserver
import sys
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler
from http import HTTPStatus
import json
import threading


class Game:
    def __init__(self, game_id: int, game_name: str = None):
        self.id = game_id
        self.name = game_name or ""
        self.next = 1  # [1,2] player
        self.winner = None  # 0 draw, 1 wins player 1, 2 wins player 2
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.empty_cells = 9
        self.end = False

    def is_winner(self, player: int) -> bool:
        return player == self.get_winner()

    def is_draw(self):
        return 0 == self.get_winner()

    def get_winner(self):
        if self.winner is not None:
            return self.winner
        winner = None
        for i in range(3):
            if (
                self.board[i][0] != 0
                and self.board[i][0] == self.board[i][1]
                and self.board[i][1] == self.board[i][2]
            ):
                winner = self.board[i][0]
        for j in range(3):
            if (
                self.board[0][j] != 0
                and self.board[0][j] == self.board[1][j]
                and self.board[1][j] == self.board[2][j]
            ):
                winner = self.board[0][j]
        if self.board[1][1] != 0 and (
            (
                self.board[0][0] == self.board[1][1]
                and self.board[1][1] == self.board[2][2]
            )
            or (
                self.board[2][0] == self.board[1][1]
                and self.board[1][1] == self.board[0][2]
            )
        ):
            winner = self.board[1][1]

        if winner is None:
            if self.game_over():
                self.winner = 0
        else:
            self.winner = winner
            self.end = True
        return self.winner

    def game_over(self):
        if not self.end:
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == 0:
                        return False
            self.end = True
        return self.end

    def game_status(self):
        if self.winner is None:
            return self.board, self.next
        else:
            return self.board, self.winner

    def make_move(self, player: int, x: int, y: int):
        if self.next != player:
            return False, "It is player {} move.".format(player)

        if self.end or self.winner is not None:
            return False, "Game is over."

        if (x < 0 or x > 2) or (y < 0 or y > 2):
            return False, "Coordinations [{},{}] out of board.".format(y, x)

        if self.board[y][x] != 0:
            return (
                False,
                (
                    "Can't place a symbol on cell [{x},{y}]."
                    " Already filled by player {player}."
                ).format(x=x, y=y, player=self.board[y][x]),
            )

        self.board[y][x] = player
        self.empty_cells -= 1
        self.next = 2 - (player + 1) % 2
        self.winner = self.get_winner()
        return True, "Cell [{},{}] filled by player {}".format(x, y, player)


class GameManager:
    GAME_FILE = os.path.join(os.path.dirname(__file__), "games.json")
    lock = threading.Lock()

    def __init__(self):
        self.games = {}
        # if os.path.exists(self.GAME_FILE):
        #     self.load_games()

    def load_games(self):
        with open(self.GAME_FILE) as f:
            d = json.load(f)
            for k, v in d.items():
                self.games[k] = self.load_game(v)

    def get_game_by_id(self, id: int) -> Game:
        return self.games.get(id)

    def new_game(self, name: str = None) -> int:
        game_id = len(self.games) + 1
        game_name = name or ""
        self.games[game_id] = Game(game_id, game_name)
        return game_id

    def save_games(self):
        print("Saving games")
        print(self.games)
        with self.lock:
            out = {}
            for k, game in self.games.items():
                out[k] = game.__dict__
            with open(self.GAME_FILE, "w") as f:
                json.dump(f, out, indent=2)

    def load_game(self, game_dict):
        g = Game(0)
        g.__dict__ = game_dict
        return g


def get_handler():
    class ServerHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            paths = ["/start", "/status", "/play", "/list"]

            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path
            query = urllib.parse.parse_qs(parsed_url.query)

            if path not in paths:
                msg = {
                    "status": "bad",
                    "message": "Invalid path. Supported paths -- {}".format(
                        ", ".join(paths)
                    ),
                }
                self.respond(HTTPStatus.OK, msg)
                return

            if path == "/status":
                return self.handle_status(query)

            if path == "/start":
                return self.handle_start(query)

            if path == "/play":
                return self.handle_play(query)

        def handle_play(self, query):
            game_id = query.get("game")
            if not game_id:
                return self._handle_missing_game_id()
            try:
                game_id = int(game_id[0])
            except:
                return self._handle_invalid_game_id_param()
            game = game_manager.get_game_by_id(game_id)
            if not game:
                return self._handle_nonexisting_game(game_id)

            player = query.get("player")
            if not player:
                msg = {"status": "bad", "message": "Missing player id"}
                self.respond(HTTPStatus.BAD_REQUEST, msg)
                return
            try:
                player = int(player[0])
            except:
                msg = {"status": "bad", "message": "Player id must be an integer"}
                self.respond(HTTPStatus.BAD_REQUEST, msg)
                return
            if player not in [1, 2]:
                msg = {"status": "bad", "message": "Player id must be in [1,2]"}
                self.respond(HTTPStatus.BAD_REQUEST, msg)
                return
            if game.next != player:
                msg = {"status": "bad", "message": "It is not your turn"}
                self.respond(HTTPStatus.BAD_REQUEST, msg)
                return

            x = query.get("x")
            y = query.get("y")
            if not (x and y):
                msg = {"status": "bad", "message": "Missing x,y coordinations"}
                self.respond(HTTPStatus.BAD_REQUEST, msg)
                return
            try:
                x = int(x[0])
                y = int(y[0])
            except:
                msg = {"status": "bad", "message": "x,y coordinations must be integers"}
                self.respond(HTTPStatus.BAD_REQUEST, msg)
                return

            valid_move, msg = game.make_move(player, x, y)
            if not valid_move:
                msg = {"status": "bad", "message": msg}
                self.respond(HTTPStatus.OK, msg)
                return

            msg = {"status": "ok"}
            self.respond(HTTPStatus.OK, msg)
            # game_manager.save_games()

        def handle_status(self, query):
            game_id = query.get("game")
            if not game_id:
                return self._handle_missing_game_id()
            try:
                game_id = int(game_id[0])
            except:
                return self._handle_invalid_game_id_param()
            game = game_manager.get_game_by_id(game_id)
            if not game:
                return self._handle_nonexisting_game(game_id)
            if game.end:
                msg = {"board": game.board, "winner": game.winner}
            else:
                msg = {"board": game.board, "next": game.next}
            self.respond(HTTPStatus.OK, msg)
            return None

        def _handle_nonexisting_game(self, game_id):
            msg = {
                "status": "bad",
                "message": "Game with id={} does not exist".format(game_id),
            }
            self.respond(HTTPStatus.BAD_REQUEST, msg)
            return None

        def _handle_invalid_game_id_param(self):
            msg = {"status": "bad", "message": "Game ID must be an integer"}
            self.respond(HTTPStatus.BAD_REQUEST, msg)
            return None

        def _handle_missing_game_id(self):
            msg = {"status": "bad", "message": "Parameter game=id is missing"}
            self.respond(HTTPStatus.BAD_REQUEST, msg)
            return None

        def handle_start(self, query):
            game_name = query.get("name")
            if game_name:
                game_name = game_name[0]
            else:
                game_name = ""
            game_id = game_manager.new_game(game_name)
            msg = {"id": game_id}
            self.respond(HTTPStatus.OK, msg)
            # game_manager.save_games()
            return None

        def respond(self, status_code, content_dict):
            prepared_data = json.dumps(content_dict, indent=2)
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=UTF-8")
            self.send_header("Content-Length", str(len(prepared_data)))
            self.end_headers()
            self.wfile.write(bytes(prepared_data, "UTF-8"))

    return ServerHandler


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    pass


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
    return httpd


game_manager = GameManager()

if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Port is missing")
        exit(1)
    port = int(args[1])

    httpd = None
    try:
        httpd = run(ThreadedHTTPServer, get_handler(), port)
    except KeyboardInterrupt:
        print("Server closed")
    finally:
        if httpd:
            httpd.server_close()
