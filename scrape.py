import csv
import os
from datetime import datetime
import random

CITIES = [
    "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
    "Łódź", "Katowice", "Lublin", "Sopot", "Zakopane"
]

def fetch_listings(city):
    return random.randint(500, 1500), random.randint(700, 1700)

def save_data():
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = "data.csv"
    need_header = not os.path.exists(filepath) or os.path.getsize(filepath) == 0
    zapisane = False

    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                if today in line:
                    zapisane = True
                    break

    if not zapisane:
        with open(filepath, "a", newline="") as f:
            writer = csv.writer(f)
            if need_header:
                writer.writerow(["date", "city", "olx", "otodom"])
            for city in CITIES:
                olx, otodom = fetch_listings(city)
                writer.writerow([today, city, olx, otodom])
                print(f"Zapisano dane dla {city}: OLX={olx}, Otodom={otodom}")
    else:
        print("Dane na dziś już istnieją.")
