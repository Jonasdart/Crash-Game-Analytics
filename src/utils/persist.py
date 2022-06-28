from tinydb import TinyDB, Query

db = TinyDB("outputs/persistence.json")

def save_ship_data(ship, bets=[]) -> bool:
    table = db.table("ships")
    Ship = Query()

    if not table.get(Ship._id == ship["_id"]):
        ship["win"] = int(ship["result"] >= 2)
        ship["bets"] = bets

        print(f"---- {len(bets)} Apostas nesta rodada ----")
        return table.insert(ship) > 0
    
    return False