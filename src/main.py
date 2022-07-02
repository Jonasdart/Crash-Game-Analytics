import logging
from time import sleep
from utils import persist as dbController
from utils.ships import Ships
from utils import bets as betsController
from models.prediction import Model
from modules.bot.src.bot import Bet

shipsController = Ships()


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


def get_prediction(model) -> int:
    """Predicts whether the next flight will reach the objective"""
    ships = shipsController.get_ships()
    prediction = model.predict(ships)[-1]

    return prediction


def save_prediction(prediction, ship_data):
    ship_data['win'] = int(ship_data['result'] >= model.goal)
    dbController.save_predict_data(prediction, ship_data)


def start(model, bot_controller):
    while True:
        try:
            logging.info("-" * 50)
            prediction = get_prediction(model)
            if prediction:
                try:
                    bot_controller.send_bet(1)
                except: 
                    logging.error("Não foi possível apostar")
            else:
                logging.info("Pulando aposta!")
            actual_ship = listen_realtime_bets()
            save_prediction(prediction, actual_ship)
            model.train()
        except Exception as e:
            logging.error(str(e))

        sleep(0.1)


def start_bot(bot_controller):
    bot_controller.login()
    bot_controller.open_crash_game()
    bot_controller.purse_value = bot_controller.acquire_purse_value()

    return bot_controller


if __name__ == "__main__":
    model = None
    bot_controller = start_bot(Bet())
    try:
        model = Model(goal=2)
    except Exception as e:
        logging.error(str(e))
    start_up()
    start(model, bot_controller)
