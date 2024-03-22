import tkinter as tk
import requests
import json
import openmeteo_requests
import requests_cache
import pandas as pd
import numpy as np
from retry_requests import retry
from datetime import datetime, timedelta

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather App")
        self.geometry("1000x500")
        
        # Create frames for different weather windows
        self.frames = []
        self.current_labels = []
        self.daily_labels = []
        n = 2     #number of needed weather windows (current and daily)
        
        for i in range(n):
            frame = tk.Frame(self)
            self.frames.append(frame)
            #frame.pack(fill="both", expand=True)
            frame.grid(row=i, column=0, sticky="nsew")  # Use grid geometry manager
            self.grid_columnconfigure(i, weight=1)  # Make columns expandable
        
        self.create_widgets()

    def create_widgets(self):
        for i, frame in enumerate(self.frames):
            if i == 0:
                self.create_current_weather_widgets(frame)
            else:
                for n in range(0, 8):
                    self.create_daily_weather_widgets(frame, n)

        self.quit = tk.Button(self, text="CLOSE", fg="black", command=self.destroy)
        self.quit.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="ne")

    def create_current_weather_widgets(self, frame):
        main_label = tk.Label(frame, text=f"Current Weather")
        main_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        current_temp_label = tk.Label(frame, text="Temperature: ")
        current_temp_label.grid(row=1, column=0, sticky="w", padx=10)
        current_apparent_temp_label = tk.Label(frame, text="Apparent temperature: ")
        current_apparent_temp_label.grid(row=2, column=0, sticky="w", padx=10)
        current_precipitation_label = tk.Label(frame, text="Precipitation: ")
        current_precipitation_label.grid(row=3, column=0, sticky="w", padx=10)
        current_wind_speed_label = tk.Label(frame, text="Wind Speed: ")
        current_wind_speed_label.grid(row=4, column=0, sticky="w", padx=10)
        current_wind_direction_label = tk.Label(frame, text="Wind Direction: ")
        current_wind_direction_label.grid(row=5, column=0, sticky="w", padx=10)
        
        self.current_labels.append((main_label, current_temp_label, current_apparent_temp_label, current_precipitation_label, current_wind_speed_label, current_wind_direction_label))
        
    def create_daily_weather_widgets(self, frame, n):
        date = (datetime.now() + timedelta(days=n-1)).strftime("%d-%m-%Y")
        
        if n <= 3:
            main_label = tk.Label(frame, text=f"Daily Weather: {date}")
            main_label.grid(row=0, column=n, sticky="w", padx=10, pady=15)
            
            daily_max_temp_label = tk.Label(frame, text="Max Temperature: ")
            daily_max_temp_label.grid(row=1, column=n, sticky="w", padx=10)
            daily_min_temp_label = tk.Label(frame, text="Min Temperature: ")
            daily_min_temp_label.grid(row=2, column=n, sticky="w", padx=10)
            daily_apparent_max_temp_label = tk.Label(frame, text="Apparent Max temperature: ")
            daily_apparent_max_temp_label.grid(row=3, column=n, sticky="w", padx=10)
            daily_apparent_min_temp_label = tk.Label(frame, text="Apparent Min temperature: ")
            daily_apparent_min_temp_label.grid(row=4, column=n, sticky="w", padx=10)
        else:
            main_label = tk.Label(frame, text=f"Daily Weather: {date}")
            main_label.grid(row=6, column=n-4, sticky="w", padx=10, pady=15)
            
            daily_max_temp_label = tk.Label(frame, text="Max Temperature: ")
            daily_max_temp_label.grid(row=7, column=n-4, sticky="w", padx=10)
            daily_min_temp_label = tk.Label(frame, text="Min Temperature: ")
            daily_min_temp_label.grid(row=8, column=n-4, sticky="w", padx=10)
            daily_apparent_max_temp_label = tk.Label(frame, text="Apparent Max temperature: ")
            daily_apparent_max_temp_label.grid(row=9, column=n-4, sticky="w", padx=10)
            daily_apparent_min_temp_label = tk.Label(frame, text="Apparent Min temperature: ")
            daily_apparent_min_temp_label.grid(row=10, column=n-4, sticky="w", padx=10)
        
        self.daily_labels.append((main_label, daily_max_temp_label, daily_min_temp_label, daily_apparent_max_temp_label, daily_apparent_min_temp_label))

    def fetch_weather_data(self):
        
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        parameters = {
            "latitude": 49.168680,
            "longitude": 16.563270,
            "current": ["temperature_2m", "apparent_temperature", "precipitation", "wind_speed_10m", "wind_direction_10m"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min"],
            "timezone": "Europe/Berlin",
            "forecast_days": 8
        }
        responses = openmeteo.weather_api(url, params=parameters)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        #print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        #print(f"Elevation {response.Elevation()} m asl")
        #print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        #print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Current values. The order of variables needs to be the same as requested.
        current = response.Current()
        current_temperature_2m = round(current.Variables(0).Value(), 2)
        current_apparent_temperature = round(current.Variables(1).Value(), 2)
        current_precipitation = current.Variables(2).Value()
        current_wind_speed_10m = round(current.Variables(3).Value(), 3)
        current_wind_direction_10m = round(current.Variables(4).Value(), 3)

        #print(f"Current temperature_2m {current_temperature_2m}")
        #print(f"Current apparent_temperature {current_apparent_temperature}")
        #print(f"Current time {current.Time()}")
        #print(f"Current precipitation {current_precipitation}")
        #print(f"Current wind_speed_10m {current_wind_speed_10m}")
        #print(f"Current wind_direction_10m {current_wind_direction_10m}")

        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        daily_temperature_2m_max_temp = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_max = [f"{value:.2f}".rstrip('0').rstrip('.') for value in np.round(daily_temperature_2m_max_temp, 2)]
        daily_temperature_2m_min_temp = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_min = [f"{value:.2f}".rstrip('0').rstrip('.') for value in np.round(daily_temperature_2m_min_temp, 2)]
        daily_apparent_temperature_max_temp = daily.Variables(2).ValuesAsNumpy()
        daily_apparent_temperature_max = [f"{value:.2f}".rstrip('0').rstrip('.') for value in np.round(daily_apparent_temperature_max_temp, 2)]
        daily_apparent_temperature_min_temp = daily.Variables(3).ValuesAsNumpy()
        daily_apparent_temperature_min = [f"{value:.2f}".rstrip('0').rstrip('.') for value in np.round(daily_apparent_temperature_min_temp, 2)]

        #daily_temperature_2m_max = np.round(daily_temperature_2m_max, 2)

        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )}
        
        daily_data["temperature_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
        daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
        
        daily_dataframe = pd.DataFrame(data = daily_data)
        print(daily_dataframe)

        self.update_labels(current_temperature_2m, current_apparent_temperature, current_precipitation, current_wind_speed_10m, current_wind_direction_10m, daily_temperature_2m_max, daily_temperature_2m_min, daily_apparent_temperature_max, daily_apparent_temperature_min)
            
    def update_labels(self, current_temperature_2m, current_apparent_temperature, current_precipitation, current_wind_speed_10m, current_wind_direction_10m, daily_temperature_2m_max, daily_temperature_2m_min, daily_apparent_temperature_max, daily_apparent_temperature_min):
        
        for labels in self.current_labels:
            labels[1].config(text=f"Temperature: {current_temperature_2m}°C")
            labels[2].config(text=f"Apparent temperature: {current_apparent_temperature}°C")
            labels[3].config(text=f"Precipitation: {current_precipitation}mm")
            labels[4].config(text=f"Wind Speed: {current_wind_speed_10m}m/s")
            labels[5].config(text=f"Wind Direction: {current_wind_direction_10m}°")

        for i, labels in enumerate(self.daily_labels):
            labels[1].config(text=f"Max Temperature: {daily_temperature_2m_max[i]}°C")
            labels[2].config(text=f"Min Temperature: {daily_temperature_2m_min[i]}°C")
            labels[3].config(text=f"Apparent Max temperature: {daily_apparent_temperature_max[i]}°C")
            labels[4].config(text=f"Apparent Min temperature: {daily_apparent_temperature_min[i]}°C")

if __name__ == "__main__":
    app = Application()
    app.fetch_weather_data()
    #app.update_labels()
    app.mainloop()