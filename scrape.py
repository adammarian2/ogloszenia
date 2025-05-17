import csv
import os
from datetime import datetime
import random
import requests
from bs4 import BeautifulSoup
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CITIES = [
    "Cała Polska", "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
    "Łódź", "Katowice", "Lublin", "Sopot", "Zakopane"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "pl,en-US;q=0.7,en;q=0.3",
}

def fetch_listings(city):
    logger.info(f"Fetch_listings dla {city} używa losowych danych")
    return random.randint(500, 1500), random.randint(700, 1700)

def extract_otodom_number():
    url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        logger.info(f"Otodom: Kod odpowiedzi HTTP {response.status_code}")
        soup = BeautifulSoup(response.text, "html.parser")
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and "ogłoszeń" in meta.get("content", ""):
            text = meta["content"]
            digits = ''.join(filter(str.isdigit, text))
            number = int(digits) if digits else 0
            logger.info(f"Otodom: Znaleziono {number} ogłoszeń")
            return number
        logger.error("Otodom: Nie znaleziono meta tagu lub liczby")
        return 0
    except Exception as e:
        logger.error(f"Otodom: Błąd: {e}")
        return 0

def fetch_all_poland_real():
    otodom_total = extract_otodom_number()
    olx_total = 0
    logger.info(f"Cała Polska: OLX={olx_total}, Otodom={otodom_total}")
    return olx_total, otodom_total

def save_data():
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = "/app/data.csv"  # Ścieżka zgodna z dyskiem Rendera
    logger.info(f"Rozpoczęcie zapisu danych dla {today} do {filepath}")

    # Sprawdź uprawnienia zapisu
    directory = os.path.dirname(filepath) or '.'
    if not os.access(directory, os.W_OK):
        logger.error(f"Brak uprawnień zapisu do katalogu {directory}")
        return
    logger.info(f"Uprawnienia zapisu do katalogu {directory}: OK")

    need_header = not os.path.exists(filepath) or os.path.getsize(filepath) == 0

    # Sprawdź istniejące wpisy
    existing_dates = set()
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # Pomiń nagłówek
                for row in reader:
                    if len(row) >= 2:
                        existing_dates.add((row[0], row[1]))
            logger.info(f"Istniejące wpisy w {filepath}: {existing_dates}")
        except Exception as e:
            logger.error(f"Błąd wczytywania {filepath}: {e}")

    # Zbierz nowe dane
    new_data = []
    for city in CITIES:
        if (today, city) not in existing_dates:
            try:
                logger.info(f"Pobieranie danych dla {city}")
                if city == "Cała Polska":
                    olx, otodom = fetch_all_poland_real()
                else:
                    olx, otodom = fetch_listings(city)
                new_data.append([today, city, olx, otodom])
                logger.info(f"Zebrano dane dla {city}: OLX={olx}, Otodom={otodom}")
            except Exception as e:
                logger.error(f"Błąd pobierania dla {city}: {e}")
                new_data.append([today, city, 0, 0])
                logger.info(f"Dodano domyślne dane dla {city}: OLX=0, Otodom=0")

    # Zapisz dane
    if new_data:
        logger.info(f"Próba zapisu {len(new_data)} wierszy: {new_data}")
        try:
            with open(filepath, "a", newline="", encoding='utf-8') as f:
                writer = csv.writer(f)
                if need_header:
                    writer.writerow(["date", "city", "olx", "otodom"])
                    logger.info("Zapisano nagłówek CSV")
                writer.writerows(new_data)
                logger.info(f"Zapisano {len(new_data)} wierszy do {filepath}")
        except Exception as e:
            logger.error(f"Błąd zapisu do {filepath}: {e}")
            logger.info(f"Uprawnienia pliku {filepath}: {os.access(filepath, os.W_OK) if os.path.exists(filepath) else 'plik nie istnieje'}")
    else:
        logger.info(f"Brak nowych danych do zapisania dla {today}")

if __name__ == "__main__":
    save_data()
