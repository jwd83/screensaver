import pygame
import json
import time
import math
from weather import OpenWeatherMap

# from blockchaininfo import BCI
from cex import CEX
import threading
from noaa import NOAA


def update_data(noaa, owm, cex):
    noaa_thread = threading.Thread(target=noaa.update)
    owm_thread = threading.Thread(target=owm.update)
    cex_thread = threading.Thread(target=cex.update)
    owm_thread.start()
    cex_thread.start()
    noaa_thread.start()


def format_usd(value):
    return f"${value:,.2f}"


def main():
    # create our objects
    noaa = NOAA(logging_enabled=True)
    owm = OpenWeatherMap()
    cex = CEX()

    # force a synchronous of all noaa data on startup
    noaa.update()

    update_data(noaa, owm, cex)

    # load the settings.json into a settings object
    with open("settings.json") as json_file:
        settings = json.load(json_file)

    blank_space = " "

    font_color = (255, 255, 255)

    if int(settings["space_doubling"]) > 1:
        blank_space = " " * int(settings["space_doubling"])

    # start pygame
    pygame.init()

    # setup a clock to run 60fps

    clock = pygame.time.Clock()

    # detect the full screen resolution of the display we are running on
    screen_info = pygame.display.Info()

    # set the screen size to the full screen resolution
    screen_size = (screen_info.current_w, screen_info.current_h)

    # create the screen

    screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN)

    # set the screen title
    pygame.display.set_caption("Binary Dragon Screen Saver")

    # load the font Bakemono-Stereo-Extrabold-trial.ttf
    font = pygame.font.Font(settings["font"], settings["fontSize"])

    font_small = pygame.font.Font(settings["font"], settings["fontSize"] // 2)
    font_tiny = pygame.font.Font(settings["font"], settings["fontSize"] // 4)

    # calculate the size of the text we are going to render once so small variations in "fixed" size fonts don't cause the text to move around
    text_time = font.render("55:55:55", True, font_color)
    text_hundredths = font_small.render("55", True, font_color)
    text_am_pm = font.render("AM", True, font_color)

    text_tiny = font_tiny.render("55", True, font_color)
    height_tiny = text_tiny.get_height()

    width_time = text_time.get_width()
    height_time = text_time.get_height()

    width_hundredths = text_hundredths.get_width()
    height_hundredths = text_hundredths.get_height()

    width_am_pm = text_am_pm.get_width()
    height_am_pm = text_am_pm.get_height()

    min_temp = 0
    max_temp = 0

    while True:
        update_data(noaa=noaa, owm=owm, cex=cex)

        # get the current unix time in seconds
        current_time = time.time()

        font_color = (
            200 + math.sin(current_time / 2) * 50,
            200 + math.sin(current_time / 3) * 50,
            200 + math.sin(current_time / 4) * 50,
        )

        # fill the screen with black

        screen.fill((0, 0, 0))

        s_temp = ""
        s_wind = ""
        s_humidity = ""
        s_shortcast = ""
        s_pressure = f"{int(owm.current_pressure)} mbar"

        # draw the 24 hour temperature plot behind the text
        if noaa.forecast_hourly_data is not None:

            forecast_now = noaa.get_current_hourly_forecast()
            hourly_temperatures = noaa.get_hourly_temperatures()[:24]
            hourly_rain_chances = noaa.get_hourly_rain_chances()[:24]
            # get the min and max values
            min_temp = min(hourly_temperatures)
            max_temp = max(hourly_temperatures)
            max_rain = max(hourly_rain_chances)

            s_shortcast = forecast_now["shortForecast"]
            s_wind = (
                f"wind: {forecast_now['windSpeed']} {forecast_now['windDirection']}"
            )
            s_humidity = f"humidity: {forecast_now['relativeHumidity']['value']}%"
            s_rain = f"Rain chances: {forecast_now['probabilityOfPrecipitation']['value']} % this hour, {max_rain}% in the next 24 hours."
            s_temp = f"{forecast_now['temperature']}°F"

            plot_line(
                hourly_temperatures,
                screen_size=screen_size,
                screen=screen,
                color=(255, 0, 0),
                thickness=2,
            )

            plot_line(
                hourly_rain_chances,
                screen_size=screen_size,
                screen=screen,
                color=(0, 0, 255),
                thickness=2,
                custom_max=100,
                custom_min=0,
            )

        s_feels_like = f"Feels like {int(owm.current_feels_like)}°F"

        # MAIN TIME ( H:MM:SS)

        # build a clock string of the current time in the format HH:MM:SS AM/PM
        # using the time module
        # %p to get AM or PM
        clock_string = time.strftime("%I:%M:%S")
        # if the first character is a zero, replace it with two spaces for this font... oof. maybe a bad font pick..
        if clock_string[0] == "0":
            clock_string = blank_space + clock_string[1:]

        # create text of a clock face like 12:34:56 AM using the font we have selected
        text_time = font.render(clock_string, True, font_color)

        # TENTHS OR HUNDREDTHS OF A SECOND

        # make the hundreds of a second the current time in milliseconds
        # and convert it to a string with a leading zero if needed

        # first check if we want tenths instead
        tenths = str(int(time.time() * 10) % 10)
        hundredths = str(int(time.time() * 100) % 100)

        if settings["tenths_or_hundredths"] == "tenths":

            # create text of the hundredths of a second from the tenths instead
            text_hundredths = font_small.render(tenths, True, font_color)

        else:
            if len(hundredths) == 1:
                hundredths = "0" + hundredths
            # create text of the hundredths of a second
            text_hundredths = font_small.render(hundredths, True, font_color)

        # AM/PM
        am_pm = time.strftime(" %p")
        text_am_pm = font.render(am_pm, True, font_color)

        # day of the week
        day_of_week = time.strftime("%A")
        text_day_of_week = font_small.render(day_of_week, True, font_color)

        # ISO week number
        week_number = time.strftime("Week %U")
        text_week_number = font_small.render(week_number, True, font_color)

        # day month and year
        day_month_year = time.strftime("%B %d, %Y")
        text_day_month_year = font_small.render(day_month_year, True, font_color)

        # temperature and weather

        # ti = noaa.get_instantaneous_temperature()

        # # make a string of ti to 3 decimal places
        # ti = f"{ti:.3f}"

        text_weather = font_small.render(
            f"{s_shortcast} @ {s_temp}",
            True,
            font_color,
        )

        text_feels_like = font_tiny.render(
            f"{s_feels_like}",
            True,
            font_color,
        )

        text_btc_usd = font_tiny.render(
            f"BTC {format_usd(cex.btc_usd)}", True, font_color
        )
        btc_movement = cex.btc_usd - cex.last_btc_usd
        if btc_movement < 0:
            text_btc_chg = font_tiny.render(
                f"-{format_usd(btc_movement*-1)}", True, font_color
            )
        else:
            text_btc_chg = font_tiny.render(
                f"+{format_usd(btc_movement)}", True, font_color
            )

        text_pressure_humidity = font_small.render(
            f"{s_wind}, {s_humidity}",
            True,
            font_color,
        )

        # determine if we will show sunrise or sunset
        show_sunrise = False

        # if it's before sunrise display the time of sunrise
        if current_time < owm.sunrise:
            show_sunrise = True
        else:
            if current_time < owm.sunset:
                # if it's before sunset display the time of sunset
                show_sunrise = False

            else:
                # if it's after sunset display the time of sunrise
                # minor bug: this will be slightly wrong until the next owm update after midnight
                # as it's the current day's sunrise
                show_sunrise = True

        if show_sunrise:
            text_sun = font_small.render(
                f"Sunrise @ {time.strftime('%I:%M %p', time.localtime(owm.sunrise))}",
                True,
                font_color,
            )
        else:
            text_sun = font_small.render(
                f"Sunset @ {time.strftime('%I:%M %p', time.localtime(owm.sunset))}",
                True,
                font_color,
            )

        # DRAW TO THE SCREEN

        # blit the text to the screen at the center of the screen using the precautions we took earlier
        screen.blit(
            text_time,
            ((screen_size[0] - width_time) // 2, (screen_size[1] - height_time) // 2),
        )

        screen.blit(
            text_hundredths,
            (
                (screen_size[0] - width_time) // 2 + width_time,
                (screen_size[1] - height_time) // 2,
            ),
        )
        screen.blit(
            text_am_pm,
            (
                (screen_size[0] - width_time) // 2 + width_time + width_hundredths,
                (screen_size[1] - height_time) // 2,
            ),
        )

        # top left
        # draw the date (ex. may 1, 2024)
        # draw the day of the week (ex. Monday)
        # draw the btc price
        # draw the btc price change
        screen.blit(text_day_month_year, (0, 0))
        screen.blit(text_day_of_week, (0, height_hundredths))
        screen.blit(text_btc_usd, (0, height_hundredths * 2))
        screen.blit(text_btc_chg, (0, height_hundredths * 2 + height_tiny))

        # draw the feels like temperature above the weather in the bottom left
        screen.blit(
            text_feels_like,
            (
                0,
                screen_size[1] - height_hundredths * 2 - height_tiny,
            ),
        )

        # draw the weather at the bottom left
        screen.blit(text_weather, (0, screen_size[1] - height_hundredths * 2))

        # draw the pressure and humidity at the bottom left below weather
        screen.blit(
            text_pressure_humidity,
            (0, screen_size[1] - height_hundredths),
        )

        # draw the sunrise or sunset time and the week number at the top right
        screen.blit(
            text_week_number,
            (screen_size[0] - text_week_number.get_width(), 0),
        )

        screen.blit(
            text_sun, (screen_size[0] - text_sun.get_width(), height_hundredths)
        )

        # draw the tenth's gauge
        for i in range(9):
            start_angle = i / 9 * 2 * 3.14159
            stop_angle = (i + 1) / 9 * 2 * 3.14159
            angle_width = settings["fontSize"] // int(
                settings["tick_thickness_divider"]
            )
            draw_at = (
                (screen_size[0] - width_time) // 2 + width_time,
                (screen_size[1] - height_time) // 2
                + height_hundredths
                - settings["fontSize"] // 6,
                settings["fontSize"] // 3,
                settings["fontSize"] // 3,
            )

            # default to disabled color
            draw_color = (33, 33, 33)

            # check if active
            if int(tenths) > i:
                scaler = (i + 20) / 30
                draw_color = (
                    font_color[0] * scaler,
                    font_color[1] * scaler,
                    font_color[2] * scaler,
                )

                # pygame.draw.arc(screen, font_color, (screen_size[0] // 2 - 50, screen_size[1] // 2 - 50, 100, 100), i * 40, (i + 1) * 40, 5)
            # draw the segment
            pygame.draw.arc(
                screen, draw_color, draw_at, start_angle, stop_angle, angle_width
            )

        pygame.display.flip()

        # run at 60 fps
        clock.tick(settings["fps"])

        # check for events

        for event in pygame.event.get():

            # quit for basically any reason...
            if event.type in [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:

                pygame.quit()

                exit()


def plot_line(
    data, screen_size, screen, color, thickness, custom_max=None, custom_min=None
):
    return

    # get the min and max temperatures
    if custom_max is not None:
        max_range = custom_max
    else:
        max_range = max(data)

    if custom_min is not None:
        min_range = custom_min
    else:
        min_range = min(data)

    if max_range <= min_range:
        max_range = min_range + 1
    # draw the temperature plot

    stop = len(data) - 1

    for i in range(stop):
        x1 = i * (screen_size[0] // stop)
        x2 = (i + 1) * (screen_size[0] // stop)

        y1 = screen_size[1] - (
            (data[i] - min_range) / (max_range - min_range) * screen_size[1]
        )
        y2 = screen_size[1] - (
            (data[i + 1] - min_range) / (max_range - min_range) * screen_size[1]
        )

        pygame.draw.line(screen, color, (x1, y1), (x2, y2), thickness)

        # draw a small circle at x1, y1 and x2, y2
        pygame.draw.circle(screen, color, (x1, y1), thickness * 3)
        pygame.draw.circle(screen, color, (x2, y2), thickness * 3)

        # # draw the current temperature at x1 + 5, y1 + 10
        # text_temp = font_tiny.render(
        #     f"{data[i]}°", True, font_color
        # )
        # screen.blit(text_temp, (x1 + 5, y1 + 10))


if __name__ == "__main__":
    main()
