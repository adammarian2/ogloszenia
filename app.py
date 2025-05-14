from flask import Flask, render_template, request, send_file
import pandas as pd
import os

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
