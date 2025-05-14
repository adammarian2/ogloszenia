import csv
import os
from datetime import datetime

CITIES = [
    "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
    "Łódź", "Katowice", "Lublin", "Sopot", "Zakopane"
]

# <<< ZAMIEŃ TĘ FUNKCJĘ NA PRAWDZIWE SCRAPOWANIE >>>
def fetch_listings(city):
    import random
    return random.randint(500, 1500), random.randint(700, 1700)

def save_data():
    today = datetime.now().strftime("%Y-%m-%d")
    file_exists = os.path.exists("data.csv")

    with open("data.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "city", "olx", "otodom"])

        for city in CITIES:
            olx, otodom = fetch_listings(city)
            writer.writerow([today, city, olx, otodom])
            print(f"Zapisano dane dla {city}: OLX={olx}, Otodom={otodom}")

save_data()
