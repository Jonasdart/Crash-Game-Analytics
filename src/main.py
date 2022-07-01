from time import sleep
from utils import persist as dbController
from utils.ships import Ships
from utils import bets as betsController
from models.prediction import Model

shipsController = Ships()
model = Model(goal=2)

def start_up():
    ships = shipsController.get_ships()
    for ship in ships:
        dbController.save_ship_data(ship)


def listen_realtime_bets():
    # bets = betsController.get_bets()
    # if bets:
    while True:
        ship = shipsController.get_last_ship()
        if dbController.save_ship_data(ship):
            return ship
        
        sleep(0.1)


def get_prediction() -> int:
    """Predicts whether the next flight will reach the objective"""
    ships = shipsController.get_ships()
    prediction = model.predict(ships)[-1]

    return prediction


def save_prediction(prediction, ship_data):
    ship_data['win'] = int(ship_data['result'] >= model.goal)
    dbController.save_predict_data(prediction, ship_data)


def start():
    while True:
        prediction = get_prediction()
        actual_ship = listen_realtime_bets()
        save_prediction(prediction, actual_ship)

        sleep(0.1)


if __name__ == "__main__":
    start_up()
    start()
