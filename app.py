from flask import Flask, render_template, request, send_file
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import os
import scrape
from datetime import datetime, timedelta

app = Flask(__name__)

CITIES = [
    "Cała Polska",
    "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
    "Łódź", "Katowice", "Lublin", "Sopot", "Zakopane"
]

DATA_PATH = "/mnt/data/data.csv"

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
    if not os.path.exists(DATA_PATH):
        return "Brak danych"

    data = pd.read_csv(DATA_PATH)
    stats = None

    if selected_city != "Cała Polska":
        data = data[data["city"] == selected_city]
    else:
        data = data[data["city"] == "Cała Polska"]
        stats = calculate_stats(data)

    data["date"] = pd.to_datetime(data["date"])
    data = data.sort_values("date")

    dates = data["date"].dt.strftime("%Y-%m-%d").tolist()
    olx_counts = data["olx"].tolist()
    otodom_counts = data["otodom"].tolist()
    total_counts = [olx + oto for olx, oto in zip(olx_counts, otodom_counts)]

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
    return send_file(DATA_PATH, as_attachment=True)

@app.route("/force-scrape")
def force_scrape():
    try:
        scrape.save_data()
        return "Scrape done!"
    except Exception as e:
        return f"Błąd scrape: {e}"

@app.route("/merge-history")
def merge_history():
    import shutil
    try:
        # Ścieżki
        source = "merged_data.csv"
        destination = "/mnt/data/data.csv"
        backup = "/mnt/data/data_backup.csv"

        # Kopia zapasowa
        if os.path.exists(destination):
            shutil.copyfile(destination, backup)

        # Nadpisanie
        shutil.copyfile(source, destination)

        return "✅ Plik data.csv został nadpisany danymi z merged_data.csv. Backup: data_backup.csv"
    except Exception as e:
        return f"❌ Błąd podczas kopiowania: {e}"

# Harmonogram scraper-a
scheduler = BackgroundScheduler()
scheduler.add_job(scrape.save_data, "cron", hour=6, minute=0)
scheduler.start()

try:
    scrape.save_data()
except Exception as e:
    print(f"Błąd podczas startowego scrape: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
