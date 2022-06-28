import requests
from time import sleep

BASE_URL = "https://api.betfiery.com/game/crash/list/tickets"
MAX_OCCURRENCES = 5


def get_bets() -> list:
    bets = []
    count_estabilization = 0
    while True:
        response = requests.post(BASE_URL)
        if response.status_code == 200:
            _bets = response.json()["data"]["data"]

            if len(_bets) > len(bets):
                bets = _bets.copy()
            if len(_bets) == len(bets):
                count_estabilization += 1

            if count_estabilization >= MAX_OCCURRENCES:
                return bets
            if len(_bets) == 0:
                return bets

        sleep(0.1)
