from constants import *
from time import sleep
import requests
import datetime

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

def main() :
    init_file()
    new_playersM: set[str] = set()
    new_playersGM: set[str] = set()
    new_playersC: set[str] = set()
    master, grandmaster, challenger = get_list()
    ranks = ["CHALLENGER", "GRANDMASTER", "MASTER"]

    for rank in ranks :
        page = 1

        while (True) :
            response = requests.get(PLAYER_IN_LEAGUE_EXP.format(rank, str(page)))
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
                return
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

main()