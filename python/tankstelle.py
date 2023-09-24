import requests
import csv
import time
from datetime import datetime
import os
from sklearn.linear_model import LinearRegression
import numpy as np
import logging
import threading


logging.basicConfig(
    filename="tankerkoenig.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


latitude = 
longitude = 


radius = 15.0


api_url = "https://creativecommons.tankerkoenig.de/json/list.php"
api_params = {
    "lat": latitude,
    "lng": longitude,
    "rad": radius,
    "sort": "dist",
    "type": "all",
    "apikey": "YOUR_API_KEY_HERE" 
}

csv_filename = "tankdaten.csv"

output_dir = "tankerkoenig_data"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

model = LinearRegression()

def clear_logs():
    while True:
        current_time = datetime.now()
        if current_time.minute == 0 and current_time.second == 0:
            with open("tankerkoenig.log", "w"):
                pass
            log_message = "Logs cleared."
            print(log_message)
            logging.info(log_message)
        time.sleep(60)

def get_and_save_data():
    try:
        response = requests.get(api_url, params=api_params)
        data = response.json()
        if data["ok"]:
            stations = data["stations"]
            current_datetime = datetime.now()

            with open(csv_filename, "a", newline="") as csvfile:
                fieldnames = ["datetime", "id", "brand", "diesel", "e5", "e10"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                for station in stations:
                    row = {
                        "datetime": current_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        "id": station["id"],
                        "brand": station["brand"],
                        "diesel": station["diesel"],
                        "e5": station["e5"],
                        "e10": station["e10"]
                    }

                    writer.writerow(row)

            log_message = f"Daten für {len(stations)} Tankstellen gespeichert."
            print(log_message)
            logging.info(log_message)
            return stations
        else:
            log_message = "Fehler beim Abrufen der Daten von der API."
            print(log_message)
            logging.error(log_message)
            return None
    except Exception as e:
        log_message = f"Fehler beim Abrufen und Speichern der Daten: {str(e)}"
        print(log_message)
        logging.error(log_message)
        return None

def predict_best_deal_time():
    try:
        valid_data = []
        with open(csv_filename, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["diesel"] and row["e10"]:
                    valid_data.append(row)

        if not valid_data:
            log_message = "Keine gültigen Daten für die Preisvorhersage verfügbar."
            print(log_message)
            logging.info(log_message)
            return None, None

        timestamps = [datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M:%S").timestamp() for row in valid_data]
        diesel_prices = [float(row["diesel"]) for row in valid_data]
        e10_prices = [float(row["e10"]) for row in valid_data]

        timestamps = np.array(timestamps).reshape(-1, 1)
        diesel_prices = np.array(diesel_prices)
        e10_prices = np.array(e10_prices)

        diesel_model = LinearRegression()
        e10_model = LinearRegression()

        diesel_model.fit(timestamps, diesel_prices)
        e10_model.fit(timestamps, e10_prices)

        current_timestamp = time.mktime(datetime.now().timetuple())
        best_diesel_price = diesel_model.predict([[current_timestamp]])[0]
        best_e10_price = e10_model.predict([[current_timestamp]])[0]

        best_diesel_time = datetime.fromtimestamp(best_diesel_price).strftime("%Y-%m-%d %H:%M:%S")
        best_e10_time = datetime.fromtimestamp(best_e10_price).strftime("%Y-%m-%d %H:%M:%S")

        return best_diesel_time, best_e10_time
    except Exception as e:
        log_message = f"Fehler bei der Preisvorhersage: {str(e)}"
        print(log_message)
        logging.error(log_message)
        return None, None

if __name__ == "__main__":
    # Start the log clearing thread
    log_clearing_thread = threading.Thread(target=clear_logs)
    log_clearing_thread.daemon = True  # Allow the thread to exit when the main program exits
    log_clearing_thread.start()

    while True:
        stations = get_and_save_data()
        if stations:
            best_diesel_time, best_e10_time = predict_best_deal_time()
            if best_diesel_time and best_e10_time:
                log_message = f"Voraussichtlich bester Zeitpunkt für den günstigsten Diesel-Preis: {best_diesel_time}"
                print(log_message)
                logging.info(log_message)
                log_message = f"Voraussichtlich bester Zeitpunkt für den günstigsten E10-Preis: {best_e10_time}"
                print(log_message)
                logging.info(log_message)
        time.sleep(300)
