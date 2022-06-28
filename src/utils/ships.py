import requests

main_url = "https://api.betfiery.com/game/crash/list/ship"


def get_ships() -> list:
    ships = requests.post(main_url).json()["data"]
    
    return ships


def get_last_ship() -> dict:
    ship = requests.post(main_url).json()["data"][0]

    return ship