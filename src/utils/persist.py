from tinydb import TinyDB, Query

db = TinyDB("outputs/persistence.json")

def save_ship_data(ship, bets=[]) -> bool:
    table = db.table("ships")
    Ship = Query()

    if not table.get(Ship._id == ship["_id"]):
        ship["win"] = int(ship["result"] >= 2)
        ship["bets"] = bets

        inserted = table.insert(ship) > 0
        print(f"---- Multiplicador: {ship['result']} -  {len(bets)} Apostas nesta rodada ----")
        
        return inserted
    
    return False
