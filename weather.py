import json
import requests
import time


class OpenWeatherMap:
    def __init__(self):

        # load the settings.json into a settings object
        with open("settings.json") as json_file:
            settings = json.load(json_file)

        lat = settings["openweathermap_lat"]
        lon = settings["openweathermap_lon"]
        key = settings["openweathermap_api_key"]

        self.lat = lat
        self.lon = lon
        self.key = key
        self.update_interval = float(settings["openweathermap_update_minutes"]) * 60
        self.last_update = 0

        self.current_temperature = 0
        self.current_pressure = 0
        self.current_humidity = 0
        self.weather_description = ""

    def update(self):

        if time.time() - self.last_update < self.update_interval:
            return

        self.last_update = time.time()

        lat = self.lat
        lon = self.lon
        key = self.key

        complete_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}"
        response = requests.get(complete_url)
        x = response.json()

        if x["cod"] != "404":

            # store the value of "main"
            # key in variable y
            y = x["main"]

            # store the value corresponding
            # to the "temp" key of y
            self.current_temperature = self.kelvin_to_fahrenheit(y["temp"])

            # store the value corresponding
            # to the "pressure" key of y
            self.current_pressure = y["pressure"]

            # store the value corresponding
            # to the "humidity" key of y
            self.current_humidity = y["humidity"]

            # store the value of "weather"
            # key in variable z
            z = x["weather"]

            # store the value corresponding
            # to the "description" key at
            # the 0th index of z
            self.weather_description = z[0]["description"]

            # print following values
            print(
                " Temperature (in fahrenheit unit) = "
                + str(self.current_temperature)
                + "\n atmospheric pressure (in hPa unit) = "
                + str(self.current_pressure)
                + "\n humidity (in percentage) = "
                + str(self.current_humidity)
                + "\n description = "
                + str(self.weather_description)
            )

    def kelvin_to_celsius(self, kelvin):
        return kelvin - 273.15

    def kelvin_to_fahrenheit(self, kelvin):
        return (kelvin - 273.15) * 9 / 5 + 32


def main():
    a = OpenWeatherMap()
    a.update()
    a.update()


if __name__ == "__main__":
    main()
