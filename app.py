import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from flask import Flask, render_template, request, send_file
import pandas as pd
import os
import scrape

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

CITIES = [
    "Cała Polska", "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
    "Łódź", "Katowice", "Lublin", "Sopot", "Zakopane"
]

def calculate_stats(df):
    if df.empty:
        return {"ath": None, "d1": None, "w1": None, "m1": None, "y1": None}
    df = df.copy()
    df["total"] = df["olx"] + df["otodom"]
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    latest = df.iloc[-1]
    ath = df["total"].max()
    def get_diff(days):
        target_date = latest["date"] - timedelta(days=days)
        past = df[df["date"] <= target_date]
        if not past.empty:
            return int(latest["total"] - past.iloc[-1]["total"])
        return None
    return {
        "ath": int(ath),
        "d1": get_diff(1),
        "w1": get_diff(7),
        "m1": get_diff(30),
        "y1": get_diff(365)
    }

@app.route("/")
def index():
    selected_city = request.args.get("city", "Cała Polska")
    if not os.path.exists("data.csv"):
        logger.error("Plik data.csv nie istnieje")
        return "Brak danych"

    # Wczytaj dane
    try:
        data = pd.read_csv("data.csv")
        logger.info(f"Wczytano {len(data)} wierszy z data.csv, daty: {data['date'].unique()}")
    except Exception as e:
        logger.error(f"Błąd wczytywania data.csv: {e}")
        return "Błąd danych"

    stats = None
    # Filtruj według miasta
    if selected_city != "Cała Polska":
        data = data[data["city"] == selected_city]
    else:
        data = data[data["city"] == "Cała Polska"]
        stats = calculate_stats(data)

    # Konwertuj daty i sortuj
    data["date"] = pd.to_datetime(data["date"])
    data = data.sort_values("date")

    # Stwórz pełny zakres dat
    if not data.empty:
        min_date = data["date"].min()
        max_date = data["date"].max()
        today = pd.to_datetime(datetime.now().date())
        if max_date < today:
            max_date = today
        all_dates = pd.date_range(start=min_date, end=max_date, freq="D")
        logger.info(f"Zakres dat: od {min_date} do {max_date}, {len(all_dates)} dni")

        # Uzupełnij brakujące dni zerami
        data_full = pd.DataFrame(all_dates, columns=["date"])
        data_full = data_full.merge(
            data[["date", "olx", "otodom"]], 
            on="date", 
            how="left"
        ).fillna({"olx": 0, "otodom": 0})

        # Przygotuj dane do szablonu
        dates = data_full["date"].dt.strftime("%Y-%m-%d").tolist()
        olx_counts = data_full["olx"].astype(int).tolist()
        otodom_counts = data_full["otodom"].astype(int).tolist()
        total_counts = [olx + oto for olx, oto in zip(olx_counts, otodom_counts)]
    else:
        logger.warning(f"Brak danych dla miasta {selected_city}")
        dates = []
        olx_counts = []
        otodom_counts = []
        total_counts = []

    return render_template(
        "index.html",
        dates=dates,
        olx_counts=olx_counts,
        otodom_counts=otodom_counts,
        total_counts=total_counts,
        cities=CITIES,
        selected_city=selected_city,
        stats=stats
    )

@app.route("/export")
def export():
    logger.info("Eksportowanie data.csv")
    return send_file("data.csv", as_attachment=True)

@app.route("/force-scrape")
def force_scrape():
    logger.info("Ręczne wywołanie scrape.save_data()")
    try:
        scrape.save_data()
        logger.info("Scrapowanie zakończone sukcesem")
        return "OK"
    except Exception as e:
        logger.error(f"Błąd scrapowania: {e}")
        return "Error", 500

# Harmonogram codzienny o 6:00
scheduler = BackgroundScheduler()
scheduler.add_job(scrape.save_data, "cron", hour=6, minute=0)
scheduler.start()
logger.info("Scheduler uruchomiony")

# Pierwsze uruchomienie na starcie
try:
    logger.info("Pierwsze uruchomienie scrape.save_data()")
    scrape.save_data()
except Exception as e:
    logger.error(f"Błąd podczas startowego scrape: {e}")

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
