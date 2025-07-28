from PySide6.QtCore import QThread, Signal
from constants import *
from time import sleep
from typing import Callable, Any
import requests
import datetime

class RiotWorker(QThread):
    finished = Signal(str)

    def __init__(self, fn: Callable[..., Any], *args: Any):
        super().__init__()
        self.fn = fn
        self.args = args

    def run(self):
        result = self.fn(*self.args)
        self.finished.emit(result)

def get_error_code_reason(code: int) -> str:
    match code:
        case 400:
            return("Bad request")
        case 401:
            return("Unauthorized")
        case 403:
            return("Forbidden")
        case 404:
            return("Data not found")
        case 405:
            return("Method not allowed")
        case 415:
            return("Unsupported media type")
        case 429:
            return("Rate limit exceeded")
        case 500:
            return("Internal server error")
        case 502:
            return("Bad gateway")
        case 503:
            return("Service unavailable")
        case 504:
            return("Gateway timeout")
        case _:
            return("No error found for this code")

def init_file() :
    try:
        open("lists/master", "r")
    except FileNotFoundError:
        open("lists/master", "x")

    try:
        open("lists/grandmaster", "r")
    except FileNotFoundError:
        open("lists/grandmaster", "x")

    try:
        open("lists/challenger", "r")
    except FileNotFoundError:
        open("lists/challenger", "x")

def get_list() :
    with open("lists/master", "r") as f:
        master = set(line.strip() for line in f)
    with open("lists/grandmaster", "r") as f:
        grandmaster = set(line.strip() for line in f)
    with open("lists/challenger", "r") as f:
        chall = set(line.strip() for line in f)

    return master, grandmaster, chall

def get_players_in_league(api_key: str) -> str:
    init_file()
    new_playersM: set[str] = set()
    new_playersGM: set[str] = set()
    new_playersC: set[str] = set()
    master, grandmaster, challenger = get_list()
    ranks = ["CHALLENGER", "GRANDMASTER", "MASTER"]

    for rank in ranks :
        page = 1

        while (True) :
            response = requests.get(PLAYER_IN_LEAGUE_EXP.format(rank, str(page), api_key))
            if (response.status_code == 200) :

                data = response.json()
                if (data == []) :
                    break
                else :
                    for player in data :
                        puuid = player["puuid"]
                        if (rank == "MASTER") :
                            new_playersM.add(puuid)
                        elif (rank == "GRANDMASTER") :
                            new_playersGM.add(puuid)
                        elif (rank == "CHALLENGER") :
                            new_playersC.add(puuid)
            elif (response.status_code == 429) :
                print("Two many requests, see you in 20 seconds")
                sleep(20)
            else :
                print(f"An error has occured ({response.status_code})")
                print(get_error_code_reason(response.status_code))
                return(str(response.status_code)+" : "+get_error_code_reason(response.status_code))
            page += 1

    date: str = datetime.datetime.now().strftime("----------------------------------%Y:%m:%d----------------------------------")

    master_to_add = [id for id in new_playersM if id not in master]
    grandmaster_to_add = [id for id in new_playersGM if id not in grandmaster]
    challenger_to_add = [id for id in new_playersC if id not in challenger]

    with open("lists/master", "a") as f:
        f.write(date+"\n")
        for id in master_to_add:
            f.write(id + "\n")
    with open("lists/grandmaster", "a") as f:
        f.write(date+"\n")
        for id in grandmaster_to_add:
            f.write(id + "\n")
    with open("lists/challenger", "a") as f:
        f.write(date+"\n")
        for id in challenger_to_add:
            f.write(id + "\n")
    return("Player lists filled successfully")

def get_player_by_puuid(puuid: str, api_key: str) -> str:
    response = requests.get(PLAYER_BY_PUUID.format(puuid, api_key))
    if (response.status_code == 200) :
        data = response.json()
        print(data)
        return ("Player returned successfully")
    else :
        print(f"An error has occured ({response.status_code})")
        print(get_error_code_reason(response.status_code))
        return(str(response.status_code)+" : "+get_error_code_reason(response.status_code))
    
def get_player_by_riotid(name: str, tag: str, api_key: str) -> str:
    response = requests.get(PLAYER_BY_RIOTID.format(name, tag, api_key))
    if (response.status_code == 200) :
        data = response.json()
        print(data)
        return ("Player returned successfully")
    else :
        print(f"An error has occured ({response.status_code})")
        print(get_error_code_reason(response.status_code))
        return(str(response.status_code)+" : "+get_error_code_reason(response.status_code))