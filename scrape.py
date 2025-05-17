import csv
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

CITIES = [
    "Cała Polska",
    "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
    "Łódź", "Katowice", "Lublin", "Sopot", "Zakopane"
]

CITY_SLUGS = {
    "Warszawa": "warszawa",
    "Kraków": "krakow",
    "Gdańsk": "gdansk",
    "Poznań": "poznan",
    "Wrocław": "wroclaw",
    "Łódź": "lodz",
    "Katowice": "katowice",
    "Lublin": "lublin",
    "Sopot": "sopot",
    "Zakopane": "zakopane"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

FILEPATH = "/mnt/data/data.csv"

def get_otodom_count(city_slug=None):
    if city_slug:
        url = f"https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/{city_slug}"
    else:
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
            print(f"[Otodom] Meta tag not found for {url}")
    except Exception as e:
        print(f"[Otodom] Error for {url}: {e}")
    return 0

def get_olx_count(city_slug=None):
    if city_slug:
        url = f"https://www.olx.pl/nieruchomosci/mieszkania/{city_slug}/"
    else:
        url = "https://www.olx.pl/nieruchomosci/mieszkania/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)
        for link in links:
            if "/nieruchomosci/mieszkania/sprzedaz/" in link["href"] and "Sprzedaż" in link.text:
                digits = ''.join(filter(str.isdigit, link.text))
                return int(digits) if digits else 0
        print(f"[OLX] Link not found for {url}")
    except Exception as e:
        print(f"[OLX] Error for {url}: {e}")
    return 0

def fetch_listings(city):
    if city == "Cała Polska":
        olx = get_olx_count()
        otodom = get_otodom_count()
    else:
        slug = CITY_SLUGS.get(city)
        if not slug:
            print(f"[Błąd] Brak slug dla miasta: {city}")
            return 0, 0
        olx = get_olx_count(slug)
        otodom = get_otodom_count(slug)
    return olx, otodom

def save_data():
    today = datetime.now().strftime("%Y-%m-%d")
    need_header = not os.path.exists(FILEPATH) or os.path.getsize(FILEPATH) == 0
    zapisane = False

    if os.path.exists(FILEPATH):
        with open(FILEPATH, "r") as f:
            for line in f:
                if today in line and "Cała Polska" in line:
                    zapisane = True
                    break

    if not zapisane:
        with open(FILEPATH, "a", newline="") as f:
            writer = csv.writer(f)
            if need_header:
                writer.writerow(["date", "city", "olx", "otodom"])
            for city in CITIES:
                olx, otodom = fetch_listings(city)
                writer.writerow([today, city, olx, otodom])
                print(f"Zapisano {city}: OLX={olx}, Otodom={otodom}")
    else:
        print("Dane na dziś już istnieją.")

if __name__ == "__main__":
    save_data()
