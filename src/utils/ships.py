import requests
from time import sleep

BASE_URL = "https://api.betfiery.com/game/crash/list/ship"
BET_TIME = 10


class Ships:
    def __init__(self):
        self.last_ship = None

    def get_ships(self) -> list:
        ships = requests.post(BASE_URL).json()["data"]

        return ships

    def get_last_ship(self) -> dict:
        while True:
            ship = requests.post(BASE_URL).json()["data"][0]
            if ship != self.last_ship:
                self.last_ship = ship
                return ship

            sleep(BET_TIME)
