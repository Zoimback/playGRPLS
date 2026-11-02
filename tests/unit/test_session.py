from src.config import Settings
from src.session import GrepolisSession, _InputParser


class Response:
    def __init__(self, value=None, url="https://es0.grepolis.com/start/index", status=200, headers=None, text=""):
        self.value, self.url, self.status_code, self.headers, self.text = value, url, status, headers or {}, text
    def raise_for_status(self):
        if self.status_code >= 400: raise RuntimeError("http")
    def json(self): return self.value


class HTTP:
    def __init__(self):
        self.headers = {}
        self.responses = [
            Response(url="https://es-play.grepolis.com/"),
            Response({"redirectUrl": "https://es0.grepolis.com/start/transfer"}),
            Response(url="https://es0.grepolis.com/start/index", text='<input name="name" value="u"><input name="passwordhash" value="hash"><input name="token" value="form">'),
            Response({"worlds": [{"id": "es148", "playing_on": True}]}),
            Response(url="https://es0.grepolis.com/start", status=302, headers={"Location": "https://es148.grepolis.com/game/login"}),
            Response(url="https://es148.grepolis.com/game/index", text="game"),
            Response(url="https://es148.grepolis.com/game/index", text='Game.csrfToken = "csrf-value"'),
        ]
    def request(self, method, url, **kwargs): return self.responses.pop(0)
    def close(self): pass


def test_input_parser_and_origin():
    parser = _InputParser()
    parser.feed('<input name="token" value="x" checked>')
    assert parser.inputs[0]["name"] == "token"
    assert GrepolisSession._origin("https://example.test/a") == "https://example.test"


def test_login_sequence_refreshes_csrf():
    session = GrepolisSession(Settings(username="u", password="p", world="es148", town_ids=(3915,)))
    session.http = HTTP()
    session.login()
    assert session.logged_in
    assert session.get_csrf_token() == "csrf-value"
    session.close()
