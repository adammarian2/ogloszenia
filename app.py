
from flask import Flask, render_template, request
import sqlite3
import plotly.graph_objs as go
from plotly.offline import plot
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date
import random

app = Flask(__name__)
DB_PATH = "data.db"

CITIES = [
    "Wszystkie miasta",
    "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
    "Łódź", "Katowice", "Lublin", "Sopot", "Zakopane"
]

def scrape_data():
    print(f"Scraping triggered at {datetime.now()}")
    cities = CITIES[1:]

    def fetch_listings(city):
        return random.randint(500, 1500), random.randint(700, 1700)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS listings (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, city TEXT, olx_count INTEGER, otodom_count INTEGER)")

    today = date.today().isoformat()
    c.execute("SELECT COUNT(*) FROM listings WHERE date = ?", (today,))
    if c.fetchone()[0] == 0:
        for city in cities:
            olx, otodom = fetch_listings(city)
            c.execute("INSERT INTO listings (date, city, olx_count, otodom_count) VALUES (?, ?, ?, ?)",
                      (today, city, olx, otodom))
        conn.commit()
        print("Dane zapisane.")
    else:
        print("Dane na dziś już istnieją.")
    conn.close()

@app.route("/force-scrape")
def force_scrape():
    scrape_data()
    return "Scraping completed (ręcznie). Możesz wrócić na <a href='/'>stronę główną</a>."

@app.route("/", methods=["GET"])
def index():
    selected_city = request.args.get("city", "Wszystkie miasta")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if selected_city == "Wszystkie miasta":
        c.execute("SELECT date, SUM(olx_count), SUM(otodom_count) FROM listings GROUP BY date ORDER BY date")
    else:
        c.execute("SELECT date, SUM(olx_count), SUM(otodom_count) FROM listings WHERE city = ? GROUP BY date ORDER BY date", (selected_city,))
    
    rows = c.fetchall()
    conn.close()

    dates = [row[0] for row in rows]
    olx_counts = [row[1] for row in rows]
    otodom_counts = [row[2] for row in rows]
    total_counts = [olx + oto for olx, oto in zip(olx_counts, otodom_counts)]

    fig_olx = go.Figure()
    fig_olx.add_trace(go.Scatter(x=dates, y=olx_counts, mode='lines+markers', name='OLX', line=dict(color='green')))
    fig_olx.update_layout(title=f"Ogłoszenia OLX – {selected_city}", xaxis_title="Data", yaxis_title="Liczba", xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    plot_olx = plot(fig_olx, output_type='div')

    fig_oto = go.Figure()
    fig_oto.add_trace(go.Scatter(x=dates, y=otodom_counts, mode='lines+markers', name='Otodom', line=dict(color='blue')))
    fig_oto.update_layout(title=f"Ogłoszenia Otodom – {selected_city}", xaxis_title="Data", yaxis_title="Liczba", xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    plot_oto = plot(fig_oto, output_type='div')

    fig_sum = go.Figure()
    fig_sum.add_trace(go.Scatter(x=dates, y=total_counts, mode='lines+markers', name='Suma OLX+Otodom', line=dict(color='magenta')))
    fig_sum.update_layout(title=f"Suma ogłoszeń OLX + Otodom – {selected_city}", xaxis_title="Data", yaxis_title="Liczba", xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    plot_sum = plot(fig_sum, output_type='div')

    return render_template("index.html", plot_olx=plot_olx, plot_oto=plot_oto, plot_sum=plot_sum, cities=CITIES, selected_city=selected_city)

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(scrape_data, 'interval', hours=24)
    scheduler.start()
    scrape_data()
    app.run(host="0.0.0.0", port=10000)
