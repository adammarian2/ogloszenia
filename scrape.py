
import sqlite3
from datetime import date
import random

cities = [
    "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
    "Łódź", "Katowice", "Lublin", "Sopot", "Zakopane"
]

def fetch_listings(city):
    return random.randint(500, 1500), random.randint(700, 1700)

conn = sqlite3.connect("data.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS listings (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, city TEXT, olx_count INTEGER, otodom_count INTEGER)")

today = date.today().isoformat()

for city in cities:
    olx, otodom = fetch_listings(city)
    c.execute("INSERT INTO listings (date, city, olx_count, otodom_count) VALUES (?, ?, ?, ?)",
              (today, city, olx, otodom))

conn.commit()
conn.close()
