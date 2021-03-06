import logging
from msilib.schema import tables
from tinydb import TinyDB, Query

db = TinyDB("outputs/persistence.json")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s-%(levelname)s: ---- %(message)s"
)


async def save_ship_data(ship) -> bool:
    table = db.table("ships")
    Ship = Query()

    if not table.get(Ship._id == ship["_id"]):
        ship["bets"] = []
        inserted = table.insert(ship) > 0
        # logging.info(f"{table.count(Ship._id != '')} Rodadas persistidas")

        return inserted

    return False


async def save_predict_data(prediction: int, ship_data: dict):
    table = db.table("predictions")
    inserted = table.insert({
        'ship': ship_data['_id'],
        "result": ship_data['result'],
        'win': ship_data['win'],
        'prediction': int(prediction),
        'hit': int(prediction == ship_data['win'])
    })
    return inserted > 0


def renew_predictions():
    Predictions = Query()
    table = db.table("predictions")
    table.remove(Predictions.ship != '')