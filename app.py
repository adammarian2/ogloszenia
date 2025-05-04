
from flask import Flask, render_template
import sqlite3
import plotly.graph_objs as go
from plotly.offline import plot

app = Flask(__name__)

@app.route("/")
def index():
    conn = sqlite3.connect("data.db")
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
    app.run(host="0.0.0.0", port=10000)
