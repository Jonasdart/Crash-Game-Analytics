import logging
from time import sleep
from utils import persist as dbController
from utils.ships import Ships
from utils import bets as betsController
from models.prediction import Model
from modules.bot.src.bot import Bet
import asyncio
import nest_asyncio
nest_asyncio.apply()

shipsController = Ships()


async def start_up():
    ships = shipsController.get_ships()
    for ship in ships:
        asyncio.run(dbController.save_ship_data(ship))


async def listen_realtime_bets(bot_controller):
    # bets = betsController.get_bets()
    # if bets:
    while True:
        ship = shipsController.get_last_ship(bot_controller)
        if await dbController.save_ship_data(ship):
            return ship

        sleep(0.1)


async def get_prediction(model) -> int:
    """Predicts whether the next flight will reach the objective"""
    ships = shipsController.get_ships()
    prediction = model.predict(ships)[0]

    return prediction


async def save_prediction(prediction, ship_data, goal):
    ship_data['win'] = int(ship_data['result'] >= goal)

    logging.info(f"Prediction: {prediction} | Hit: {prediction == ship_data['win']}")
    asyncio.run(dbController.save_predict_data(prediction, ship_data))


async def start(model, bot_controller):
    while True:
        if model.count_predictions >= 9:
            model.train()
            model.count_predictions = 0
        try:
            if bot_controller.get_bet_status() == 'wait':
                logging.info("-" * 50)
                prediction = await get_prediction(model)
                if prediction:
                    try:
                        logging.info("Sending bet request..")
                        # asyncio.run(bot_controller.send_bet(1))
                        asyncio.run(bot_controller.send_bet_with_money_control())
                    except:
                        logging.error("Não foi possível apostar")
                else:
                    logging.info("Pulando aposta!")
                # actual_ship = listen_realtime_bets(bot_controller)
                actual_ship = shipsController.get_last_ship(bot_controller)
                logging.info(
                    f"Multiplicador: {actual_ship['result']}"
                )
                asyncio.run(dbController.save_ship_data(actual_ship))
                asyncio.run(save_prediction(prediction, actual_ship, model.goal))
        except Exception as e:
            logging.error(str(e))

        sleep(0.1)


async def start_bot(bot_controller):
    bot_controller.login()
    bot_controller.open_crash_game()
    bot_controller.purse_value = bot_controller.acquire_purse_value()

    return bot_controller


async def init():
    model = None
    bot_controller = await start_bot(Bet())
    try:
        model = Model(goal=2)
    except Exception as e:
        logging.error(str(e))
    await start_up()
    await start(model, bot_controller)

if __name__ == "__main__":
    asyncio.run(init())