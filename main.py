import tkinter as tk
import requests
import json
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather App")
        self.geometry("1200x800")
        
        # Create frames for different weather windows
        self.frames = []
        self.current_labels = []
        self.daily_labels = []
        n = 2     #number of needed weather windows (current and daily)
        
        for i in range(n):
            frame = tk.Frame(self)
            self.frames.append(frame)
            frame.pack(fill="both", expand=True)
        
        self.create_widgets()

    def create_widgets(self):
        #self.labels = []
        for i, frame in enumerate(self.frames):
            if i == 0:
                self.create_current_weather_widgets(frame)
            else:
                for i in range(0, 13, 1):
                    self.create_daily_weather_widgets(frame)


            #self.labels.append((main_label, current_temp_label, current_apparent_temp_label, current_precipitation_label, current_wind_speed_label, current_wind_direction_label))

        self.quit = tk.Button(self, text="CLOSE", fg="black", command=self.destroy)
        self.quit.pack(side="bottom", pady=10, padx=10, anchor="se")

    def create_current_weather_widgets(self, frame):
        main_label = tk.Label(frame, text=f"Current Weather")
        main_label.pack(pady=10)

        current_temp_label = tk.Label(frame, text="Temperature: ")
        current_temp_label.pack()
        current_apparent_temp_label = tk.Label(frame, text="Apparent temperature: ")
        current_apparent_temp_label.pack()
        current_precipitation_label = tk.Label(frame, text="Precipitation: ")
        current_precipitation_label.pack()
        current_wind_speed_label = tk.Label(frame, text="Wind Speed: ")
        current_wind_speed_label.pack()
        current_wind_direction_label = tk.Label(frame, text="Wind Direction: ")
        current_wind_direction_label.pack()
        
        self.current_labels.append((main_label, current_temp_label, current_apparent_temp_label, current_precipitation_label, current_wind_speed_label, current_wind_direction_label))
        
    def create_daily_weather_widgets(self, frame):
        main_label = tk.Label(frame, text=f"Daily Weather")
        main_label.pack(pady=10)

        daily_max_temp_label = tk.Label(frame, text="Max Temperature: ")
        daily_max_temp_label.pack()
        daily_min_temp_label = tk.Label(frame, text="Min Temperature: ")
        daily_min_temp_label.pack()
        daily_apparent_max_temp_label = tk.Label(frame, text="Apparent Max temperature: ")
        daily_apparent_max_temp_label.pack()
        daily_apparent_min_temp_label = tk.Label(frame, text="Apparent Min temperature: ")
        daily_apparent_min_temp_label.pack()
        
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
            "latitude": 46.072491,
            "longitude": 14.50998,
            "current": ["temperature_2m", "apparent_temperature", "precipitation", "wind_speed_10m", "wind_direction_10m"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min"],
            "timezone": "auto",
            "forecast_days": 14
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
        current_temperature_2m = current.Variables(0).Value()
        current_apparent_temperature = current.Variables(1).Value()
        current_precipitation = current.Variables(2).Value()
        current_wind_speed_10m = current.Variables(3).Value()
        current_wind_direction_10m = current.Variables(4).Value()

        #print(f"Current temperature_2m {current_temperature_2m}")
        #print(f"Current apparent_temperature {current_apparent_temperature}")
        #print(f"Current time {current.Time()}")
        #print(f"Current precipitation {current_precipitation}")
        #print(f"Current wind_speed_10m {current_wind_speed_10m}")
        #print(f"Current wind_direction_10m {current_wind_direction_10m}")

        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
        daily_apparent_temperature_max = daily.Variables(2).ValuesAsNumpy()
        daily_apparent_temperature_min = daily.Variables(3).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )}
        
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
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