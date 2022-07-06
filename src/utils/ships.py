import logging
import requests
from time import sleep

BASE_URL = "https://api.betfiery.com/game/crash/list/ship"
BET_TIME = 8


class Ships:
    def __init__(self):
        self.last_ship = None

    def get_ships(self) -> list:
        ships = requests.post(BASE_URL).json()["data"]

        return ships

    def get_last_ship(self, bot_controller) -> dict:
        logging.info("Waiting ship crash")
        while bot_controller.get_bet_status() == 'wait': 
            sleep(0.1)
        while bot_controller.get_bet_status() != 'wait':
            sleep(0.1)

        sleep(1)
        ship = requests.post(BASE_URL).json()["data"][0]
        return ship
