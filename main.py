import pygame
import json
import time
import math
from weather import OpenWeatherMap

owm = OpenWeatherMap()
owm.update()

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

small_font = pygame.font.Font(settings["font"], settings["fontSize"] // 2)

# calcuate the size of the text we are going to render once so small variations in "fixed" size fonts don't cause the text to move around
text_time = font.render("55:55:55", True, font_color)
text_hundredths = small_font.render("55", True, font_color)
text_am_pm = font.render("AM", True, font_color)

width_time = text_time.get_width()
height_time = text_time.get_height()

width_hundredths = text_hundredths.get_width()
height_hundredths = text_hundredths.get_height()

width_am_pm = text_am_pm.get_width()
height_am_pm = text_am_pm.get_height()


while True:
    # update the weather as needed
    owm.update()

    # get the current unix time in seconds
    current_time = time.time()

    font_color = (
        150 + math.sin(current_time / 2) * 100,
        150 + math.sin(current_time / 3) * 100,
        150 + math.sin(current_time / 4) * 100,
    )

    # fill the screen with black

    screen.fill((0, 0, 0))

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
        text_hundredths = small_font.render(tenths, True, font_color)

    else:
        if len(hundredths) == 1:
            hundredths = "0" + hundredths
        # create text of the hundredths of a second
        text_hundredths = small_font.render(hundredths, True, font_color)

    # AM/PM
    am_pm = time.strftime(" %p")
    text_am_pm = font.render(am_pm, True, font_color)

    # day of the week
    day_of_week = time.strftime("%A")
    text_day_of_week = small_font.render(day_of_week, True, font_color)

    # ISO week number
    week_number = time.strftime("Week %U")
    text_week_number = small_font.render(week_number, True, font_color)

    # day month and year
    day_month_year = time.strftime("%B %d, %Y")
    text_day_month_year = small_font.render(day_month_year, True, font_color)

    # weather
    text_weather = small_font.render(
        f"{owm.weather_description} @ {int(owm.current_temperature)}°F",
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

    # draw the day of the week at the top left
    screen.blit(text_day_of_week, (0, 0))

    # draw the day month and year directly below the day of the week
    screen.blit(text_day_month_year, (0, height_hundredths))

    # draw the weather at the bottom left
    screen.blit(text_weather, (0, screen_size[1] - height_hundredths))

    # draw the week number at the top right
    screen.blit(text_week_number, (screen_size[0] - text_week_number.get_width(), 0))

    # draw the tenth's gauge
    for i in range(9):
        start_angle = i / 9 * 2 * 3.14159
        stop_angle = (i + 1) / 9 * 2 * 3.14159
        angle_width = settings["fontSize"] // int(settings["tick_thickness_divider"])
        draw_at = (
            (screen_size[0] - width_time) // 2 + width_time,
            (screen_size[1] - height_time) // 2
            + height_hundredths
            - settings["fontSize"] // 6,
            settings["fontSize"] // 3,
            settings["fontSize"] // 3,
        )

        # default to disabled color
        draw_color = (50, 50, 50)

        # check if active
        if int(tenths) > i:
            draw_color = font_color
            # pygame.draw.arc(screen, font_color, (screen_size[0] // 2 - 50, screen_size[1] // 2 - 50, 100, 100), i * 40, (i + 1) * 40, 5)
        # draw the segment
        pygame.draw.arc(
            screen, draw_color, draw_at, start_angle, stop_angle, angle_width
        )

    # # draw a circle divided up into 9 regions for tenths of a second. all will be dim at 0 and each segment will light up when it's tenth
    # # has passed. This will be a visual representation of the tenths of a second.
    # segments = 99

    # for i in range(segments):
    #     start_angle = i / segments * 2 * 3.14159
    #     stop_angle = (i+1) / segments * 2 * 3.14159
    #     angle_width = settings['fontSize'] // int(settings['tick_thickness_divider'])
    #     draw_at = (
    #         (screen_size[0] - width_time) // 2 + width_time + settings['fontSize'] // 20,
    #         (screen_size[1] - height_time) // 2 + height_hundredths - settings['fontSize'] // 6,
    #         settings['fontSize'] // 4,
    #         settings['fontSize'] // 4
    #     )

    #     # default to disabled color
    #     draw_color = (80, 80, 80)

    #     # check if active
    #     if int(hundredths)  > i:
    #         draw_color = font_color

    #     # draw the segment
    #     pygame.draw.arc(
    #         screen,
    #         draw_color,
    #         draw_at,
    #         start_angle,
    #         stop_angle,
    #         angle_width
    #     )

    pygame.display.flip()

    # run at 60 fps
    clock.tick(settings["fps"])

    # check for events

    for event in pygame.event.get():

        # quit for basically any reason...
        if event.type in [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:

            pygame.quit()

            exit()
