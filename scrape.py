import csv
import os
from datetime import datetime
import random
import requests
from bs4 import BeautifulSoup

CITIES = [
    "Cała Polska",
    "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
    "Łódź", "Katowice", "Lublin", "Sopot", "Zakopane"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_listings(city):
    return random.randint(500, 1500), random.randint(700, 1700)

def extract_otodom_number():
    url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and "ogłoszeń" in meta["content"]:
            text = meta["content"]
            digits = ''.join(filter(str.isdigit, text))
            return int(digits) if digits else 0
        else:
            print("[Otodom] Nie znaleziono meta tagu lub liczby.")
    except Exception as e:
        print(f"[Otodom] Błąd: {e}")
    return 0

def fetch_all_poland_real():
    otodom_total = extract_otodom_number()
    olx_total = 0  # Placeholder – OLX może być dodany później
    print(f"[DEBUG] OLX total: {olx_total}, Otodom total: {otodom_total}")
    return olx_total, otodom_total

def save_data():
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = "data.csv"
    need_header = not os.path.exists(filepath) or os.path.getsize(filepath) == 0
    zapisane = False

    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                if today in line and "Cała Polska" in line:
                    zapisane = True
                    break

    if not zapisane:
        with open(filepath, "a", newline="") as f:
            writer = csv.writer(f)
            if need_header:
                writer.writerow(["date", "city", "olx", "otodom"])

            olx_all, otodom_all = fetch_all_poland_real()
            writer.writerow([today, "Cała Polska", olx_all, otodom_all])
            print(f"Zapisano Cała Polska: OLX={olx_all}, Otodom={otodom_all}")

            for city in CITIES:
                if city == "Cała Polska":
                    continue
                olx, otodom = fetch_listings(city)
                writer.writerow([today, city, olx, otodom])
                print(f"Zapisano {city}: OLX={olx}, Otodom={otodom}")
    else:
        print("Dane na dziś już istnieją.")

if __name__ == "__main__":
    save_data()
