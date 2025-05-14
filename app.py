from flask import Flask, render_template, request, send_file
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import os
import scrape  # zakładamy, że masz scrape.py w tym samym katalogu
from datetime import datetime

app = Flask(__name__)

CITIES = [
    "Wszystkie miasta",
    "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
    "Łódź", "Katowice", "Lublin", "Sopot", "Zakopane"
]

@app.route("/")
def index():
    selected_city = request.args.get("city", "Wszystkie miasta")
    if not os.path.exists("data.csv"):
        return "Brak danych"

    data = pd.read_csv("data.csv")
    if selected_city != "Wszystkie miasta":
        data = data[data["city"] == selected_city]
    else:
        data = data.groupby("date")[["olx", "otodom"]].sum().reset_index()

    dates = data["date"].tolist()
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
        selected_city=selected_city
    )

@app.route("/export")
def export():
    return send_file("data.csv", as_attachment=True)

@app.route("/force-scrape")
def force_scrape():
    try:
        scrape.save_data()
        return "Scrape done!"
    except Exception as e:
        return f"Błąd scrape: {e}"

# Harmonogram codzienny o 6:00
scheduler = BackgroundScheduler()
scheduler.add_job(scrape.save_data, "cron", hour=6, minute=0)
scheduler.start()

# Pierwsze uruchomienie od razu
try:
    scrape.save_data()
except Exception as e:
    print(f"Błąd podczas startowego scrape: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
