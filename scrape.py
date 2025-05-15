import csv
import os
from datetime import datetime
import random
import requests
from bs4 import BeautifulSoup

CITIES = [
    "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
    "Łódź", "Katowice", "Lublin", "Sopot", "Zakopane"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_listings(city):
    # FAKE dane (Twoja wersja)
    return random.randint(500, 1500), random.randint(700, 1700)

def fetch_all_poland():
    # Prawdziwe dane OLX + Otodom dla całej Polski
    olx_url = "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/"
    otodom_url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie"

    def extract_number(url, selector, attribute="text"):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                digits = ''.join(filter(str.isdigit, text))
                return int(digits) if digits else 0
        except:
            return 0
        return 0

    olx_total = extract_number(olx_url, "h6")
    otodom_total = extract_number(otodom_url, "span[data-cy='search.result.count']")
    return olx_total, otodom_total

def save_data():
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = "data.csv"
    need_header = not os.path.exists(filepath) or os.path.getsize(filepath) == 0
    zapisane = False

    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                if today in line and "ALL" in line:
                    zapisane = True
                    break

    if not zapisane:
        with open(filepath, "a", newline="") as f:
            writer = csv.writer(f)
            if need_header:
                writer.writerow(["date", "city", "olx", "otodom"])

            # 🔹 Wpis ogólnopolski (ALL)
            olx_all, otodom_all = fetch_all_poland()
            writer.writerow([today, "ALL", olx_all, otodom_all])
            print(f"Zapisano dane dla ALL: OLX={olx_all}, Otodom={otodom_all}")

            # 🔹 Dane per miasto (Twoja dotychczasowa logika)
            for city in CITIES:
                olx, otodom = fetch_listings(city)
                writer.writerow([today, city, olx, otodom])
                print(f"Zapisano dane dla {city}: OLX={olx}, Otodom={otodom}")
    else:
        print("Dane na dziś już istnieją.")

if __name__ == "__main__":
    save_data()
