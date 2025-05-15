from flask import Flask, render_template, request, send_file
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import os
import scrape  # zakładamy, że masz scrape.py w tym samym katalogu
from datetime import datetime, timedelta

app = Flask(__name__)

CITIES = [
    "Wszystkie miasta",
    "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
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
    selected_city = request.args.get("city", "Wszystkie miasta")
    if not os.path.exists("data.csv"):
        return "Brak danych"

    data = pd.read_csv("data.csv")
    stats = None

    if selected_city != "Wszystkie miasta":
        data = data[data["city"] == selected_city]
    else:
        data = data.groupby("date")[["olx", "otodom"]].sum().reset_index()
        stats = calculate_stats(data)

    dates = data["]()
