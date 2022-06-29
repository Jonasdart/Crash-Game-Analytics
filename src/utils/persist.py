import logging
from tinydb import TinyDB, Query

db = TinyDB("outputs/persistence.json")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s-%(levelname)s: ---- %(message)s')

def save_ship_data(ship, bets=[]) -> bool:
    table = db.table("ships")
    Ship = Query()

    if not table.get(Ship._id == ship["_id"]):
        ship["bets"] = bets

        inserted = table.insert(ship) > 0
        logging.info(f"Multiplicador: {ship['result']} - {len(bets)} Apostas nesta rodada")
        logging.info(f"{table.count(Ship._id != '')} Rodadas persistidas")

        return inserted
    
    return False
