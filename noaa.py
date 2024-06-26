# Author: Jared De Blander (github.com/jwd83)
#
# Let's talk to National Oceanic and Atmospheric Administration! (NOAA)
#
# The National Oceanic and Atmospheric Administration has a public api
# that we can use to get weather data and alerts
#
# default rate limit is 60 second cooldown
# you can change this by passing in a different value
# minimum rate limit is 1 second
# let's all play nice in the sandbox and not spam too much :)


import requests
import time
import json


class NOAA:
    def __init__(
        self,
        cooldown=60,
        verbose_enabled=False,
        lat=None,
        lon=None,
        logging_enabled=False,
    ):

        with open("settings.json") as json_file:
            settings = json.load(json_file)

        if lat is None:
            self.lat = settings["weather_lat"]
        else:
            self.lat = lat

        if lon is None:
            self.lon = settings["weather_lon"]
        else:
            self.lon = lon

        self.state = settings["weather_state"]

        self.cooldown = int(cooldown)
        self.verbose_enabled = bool(verbose_enabled)
        self.logging_enabled = bool(logging_enabled)

        self.last_update = 0
        if self.cooldown < 1:
            self.cooldown = 1

    def update(self):
        # handle rate limit then update data if needed
        if time.time() - self.last_update < self.cooldown:
            self.verbose("Rate limited, skipping update")
            return

        # record the timestamp of the new rate limit.
        self.last_update = time.time()

        self.verbose("Updating NOAA data")
        url = f"https://api.weather.gov/points/{self.lat},{self.lon}"
        response = requests.get(url)
        if response.status_code != 200:
            self.verbose(f"Failed to get NOAA data: {response.status_code}")
            return

        self.points_data = response.json()

        # pretty print the data
        self.verbose(json.dumps(self.points_data, indent=4))

        # get the forecast urls
        forecast_url = self.points_data["properties"]["forecast"]
        forecast_hourly_url = self.points_data["properties"]["forecastHourly"]

        # get the forecast data
        response = requests.get(forecast_url)
        if response.status_code != 200:
            self.verbose(f"Failed to get forecast data: {response.status_code}")
            return

        self.forecast_data = response.json()

        # pretty print the forecast data
        self.verbose(json.dumps(self.forecast_data, indent=4))

        # get the forecast hourly data

        response = requests.get(forecast_hourly_url)
        if response.status_code != 200:
            self.verbose(f"Failed to get forecast hourly data: {response.status_code}")
            return

        self.forecast_hourly_data = response.json()

        # pretty print the forecast hourly data
        self.verbose(json.dumps(self.forecast_hourly_data, indent=4))

        if self.logging_enabled:
            self.__log_data()

    def __log_data(self):
        # write the dumps too noaa-point.json
        with open("noaa-point.json", "w") as file:
            json.dump(self.points_data, file, indent=4)

        with open("noaa-forecast.json", "w") as file:
            json.dump(self.forecast_data, file, indent=4)

        with open("noaa-forecast-hourly.json", "w") as file:
            json.dump(self.forecast_hourly_data, file, indent=4)

    def verbose(self, str: str):
        if self.verbose_enabled:
            print(str)

    def get_short_forecast(self):
        if self.forecast_data is not None:
            return self.forecast_data["properties"]["periods"][0]["shortForecast"]
        else:
            return "No Data"

    def get_current_hourly_forecast(self):
        if self.forecast_hourly_data is not None:
            return self.get_active_periods()[0]
        else:
            return "No Data"

    def get_instantaneous_temperature(self):
        if self.forecast_hourly_data is not None:

            # extract the minutes and seconds of the current time
            current_time = time.localtime()
            fractional_seconds = time.time() % 1

            seconds_into_hour = (
                current_time.tm_sec + current_time.tm_min * 60 + fractional_seconds
            )
            hour_progress = seconds_into_hour / (60 * 60)

            # get the temperature for this hour and next hour
            temperatures = self.get_hourly_temperatures()

            t1 = temperatures[0]
            t2 = temperatures[1]

            # linear interpolation
            ti = t1 + (t2 - t1) * hour_progress

            return ti

        else:
            return 0

    def get_active_periods(self):

        active_periods = []

        if self.forecast_hourly_data is not None:

            # reject any data that is before the current time
            current_time = time.time()

            for period in self.forecast_hourly_data["properties"]["periods"]:
                # look at when this hour ends
                end_time = period["endTime"]

                # end time is in the following format 2024-04-23T19:00:00-04:00
                # we need to convert this to unix time

                end_time_unix = time.mktime(
                    time.strptime(end_time, "%Y-%m-%dT%H:%M:%S%z")
                )

                if current_time < end_time_unix:
                    active_periods.append(period)

        return active_periods

    def get_hourly_rain_chances(self):

        hourly_rain_chances = []

        active_periods = self.get_active_periods()

        for period in active_periods:
            hourly_rain_chances.append(period["probabilityOfPrecipitation"]["value"])

        return hourly_rain_chances

    def get_hourly_temperatures(self):

        hourly_temps = []

        active_periods = self.get_active_periods()

        for period in active_periods:
            hourly_temps.append(period["temperature"])

        return hourly_temps


if __name__ == "__main__":
    noaa = NOAA(verbose_enabled=True, logging_enabled=True)
    noaa.update()
    print("Current Weather Conditions ")
    print(noaa.forecast_data["properties"]["periods"][0]["detailedForecast"])
    print("Hourly Forecast")

    # for period in noaa.forecast_hourly_data["properties"]["periods"]:
    #     print(
    #         f"{period['startTime']} to {period['endTime']} {period['temperature']}F {period['shortForecast']}"
    #     )
    # # loop through the periods

    # print(noaa.get_hourly_temperatures())
    # print("Active periods")
    # print(noaa.get_active_periods())
    print(f"Current Hourly Forecast: {noaa.get_current_hourly_forecast()}")

    print(f"Temp: {noaa.get_instantaneous_temperature()}")

    noaa.update()
