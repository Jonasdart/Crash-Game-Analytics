from time import sleep
import persist as dbController
import ships as shipsController
import bets as betsController


def start_up():
    ships = shipsController.get_ships()
    for ship in ships:
        dbController.save_ship_data(ship)


def listen_realtime_bets():
    bets = betsController.get_bets()
    ship = shipsController.get_last_ship()
    dbController.save_ship_data(ship, bets)


def start():
    while True:
        listen_realtime_bets()
        sleep(0.5)

if __name__ == '__main__':
    start_up()
    start()