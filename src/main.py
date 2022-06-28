from time import sleep
from utils import persist as dbController
from utils.ships import Ships
from utils import bets as betsController

shipsController = Ships()

def start_up():
    ships = shipsController.get_ships()
    for ship in ships:
        dbController.save_ship_data(ship)


def listen_realtime_bets():
    bets = betsController.get_bets()
    if bets:
        ship = shipsController.get_last_ship()
        dbController.save_ship_data(ship, bets)


def start():
    while True:
        listen_realtime_bets()
        sleep(0.1)

if __name__ == '__main__':
    start_up()
    start()
