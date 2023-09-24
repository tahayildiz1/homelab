import requests
import mysql.connector
from datetime import datetime
import time


api_key = ''

city_name = ''

base_url = 'https://api.openweathermap.org/data/2.5/weather?'

db_config = {
    'host': '',
    'user': '',
    'password': '',
    'database': ''  
}

while True:
    url = f'{base_url}q={city_name}&appid={api_key}&units=metric'

    conn = mysql.connector.connect(**db_config)

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        temperature = data['main']['temp']
        description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']

        cursor = conn.cursor()
        insert_query = "INSERT INTO user_weather_data (city_name, temperature, description, humidity, wind_speed) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (city_name, temperature, description, humidity, wind_speed))
        conn.commit()
        cursor.close()

        print(f'City: {city_name}')
        print(f'Temperature: {temperature}°C')
        print(f'Description: {description}')
        print(f'Humidity: {humidity}%')
        print(f'Wind Speed: {wind_speed} m/s')

        timestamp = datetime.now()
        print(f'Timestamp: {timestamp}')

        conn.close()
    else:
        print('Error: Unable to retrieve weather data.')

    time.sleep(300)
