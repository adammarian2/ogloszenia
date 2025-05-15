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
    # Losowe dane tylko dla miast
    return random.randint(500, 1500), random.randint(700, 1700)

def fetch_all_poland_real():
    olx_url = "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/"
    otodom_url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie"

    def extract_number(url, selector, fallback_label):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                digits = ''.join(filter(str.isdigit, text))
                return int(digits) if digits else 0
            else:
                print(f"[{fallback_label}] Element nie znaleziony w HTML")
        except Exception as e:
            print(f"[{fallback_label}] Błąd pobierania: {e}")
        return 0

    olx_total = extract_number(olx_url, "h6", "OLX")
    otodom_total = extract_number(otodom_url, "div.css-1vr17z4 > span", "Otodom")

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

            # 🔹 Rzeczywiste dane z całej Polski
            olx_all, otodom_all = fetch_all_poland_real()
            writer.writerow([today, "Cała Polska", olx_all, otodom_all])
            print(f"Zapisano Cała Polska: OLX={olx_all}, Otodom={otodom_all}")

            # 🔹 Losowe dane dla miast
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
