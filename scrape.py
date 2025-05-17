import csv
import os
from datetime import datetime
import random
import requests
from bs4 import BeautifulSoup
import logging
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CITIES = [
    "Cała Polska", "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
    "Łódź", "Katowice", "Lublin", "Sopot", "Zakopane"
]

# Rotacja nagłówków
HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "pl,en-US;q=0.7,en;q=0.3",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "pl,en-US;q=0.7,en;q=0.3",
    }
]

def fetch_listings(city):
    # Placeholder – losowe dane
    logger.warning(f"Fetch_listings dla {city} używa losowych danych")
    return random.randint(500, 1500), random.randint(700, 1700)

def extract_otodom_number():
    url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie"
    session = requests.Session()
    
    # Konfiguracja retry
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    for headers in HEADERS_LIST:
        try:
            logger.info(f"Próba scrapowania Otodom z nagłówkami: {headers['User-Agent']}")
            response = session.get(url, headers=headers, timeout=10)
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
            else:
                logger.error("Otodom: Nie znaleziono meta tagu lub liczby ogłoszeń")
                # Loguj fragment HTML dla debugowania
                logger.debug(f"Otodom: Fragment HTML: {str(soup)[:500]}...")
            
        except requests.RequestException as e:
            logger.error(f"Otodom: Błąd HTTP dla nagłówków {headers['User-Agent']}: {e}")
            time.sleep(2)  # Opóźnienie przed kolejną próbą
            continue
        
        time.sleep(1)  # Opóźnienie między próbami
        
    logger.error("Otodom: Wszystkie próby scrapowania nieudane")
    return 0  # Domyślna wartość w przypadku niepowodzenia

def fetch_all_poland_real():
    otodom_total = extract_otodom_number()
    olx_total = 0  # Placeholder – dodaj scrapowanie OLX
    logger.info(f"Cała Polska: OLX={olx_total}, Otodom={otodom_total}")
    return olx_total, otodom_total

def save_data():
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = "data.csv"
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
        except Exception as e:
            logger.error(f"Błąd wczytywania {filepath}: {e}")

    # Zbierz nowe dane
    new_data = []
    for city in CITIES:
        if (today, city) not in existing_dates:
            try:
                if city == "Cała Polska":
                    olx, otodom = fetch_all_poland_real()
                else:
                    olx, otodom = fetch_listings(city)
                new_data.append([today, city, olx, otodom])
                logger.info(f"Zebrano dane dla {city}: OLX={olx}, Otodom={otodom}")
            except Exception as e:
                logger.error(f"Błąd scrapowania dla {city}: {e}")
                # Zapisz dane z wartościami 0 w przypadku błędu
                new_data.append([today, city, 0, 0])
                logger.info(f"Zapisano domyślne dane dla {city}: OLX=0, Otodom=0")
                continue

    # Zapisz dane
    if new_data:
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
    else:
        logger.info(f"Brak nowych danych dla {today}")

if __name__ == "__main__":
    save_data()
