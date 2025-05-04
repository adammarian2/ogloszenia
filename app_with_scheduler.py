
from flask import Flask, render_template
import sqlite3
import plotly.graph_objs as go
from plotly.offline import plot
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date
import random

app = Flask(__name__)

DB_PATH = "data.db"

def scrape_data():
    print(f"Scraping triggered at {datetime.now()}")
    cities = [
        "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
        "Łódź", "Katowice", "Lublin", "Sopot", "Zakopane"
    ]

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
        print("Data scraped and saved.")
    else:
        print("Data for today already exists. Skipping.")
    conn.close()

@app.route("/")
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT date, city, SUM(olx_count), SUM(otodom_count) FROM listings GROUP BY date ORDER BY date")
    rows = c.fetchall()
    conn.close()

    dates = [row[0] for row in rows]
    olx_counts = [row[2] for row in rows]
    otodom_counts = [row[3] for row in rows]
    total_counts = [olx + oto for olx, oto in zip(olx_counts, otodom_counts)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=total_counts, fill='tozeroy', mode='lines', name='Suma OLX+Otodom'))
    fig.update_layout(title="Suma ogłoszeń OLX + Otodom", xaxis_title="Data", yaxis_title="Liczba ogłoszeń", yaxis_type='log')

    plot_div = plot(fig, output_type='div')
    return render_template("index.html", plot_div=plot_div)

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(scrape_data, 'interval', hours=24)
    scheduler.start()
    scrape_data()
    app.run(host="0.0.0.0", port=10000)
