import requests
from time import sleep

base_url = "https://api.betfiery.com/game/crash/list/tickets"


def get_bets() -> list:
    bets = []
    response = requests.post(base_url)
    while True:
        response = requests.post(base_url)
        if response.text == "":
            break
        bets = response.json()["data"]["data"]

        sleep(1)
        
    print(f"---- {len(bets)} Apostas nesta rodada ----")
    return bets
