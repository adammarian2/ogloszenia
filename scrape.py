import csv
import os
from datetime import datetime

# <<< Tu wstaw swój prawdziwy kod zliczający ogłoszenia >>>
olx_count = 123  # przykładowa liczba
otodom_count = 456  # przykładowa liczba

def save_data(olx, otodom):
    today = datetime.now().strftime("%Y-%m-%d")
    file_exists = os.path.exists("data.csv")

    with open("data.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "olx", "otodom"])
        writer.writerow([today, olx, otodom])

save_data(olx_count, otodom_count)
