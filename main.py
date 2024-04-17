import pygame
import json
import time


# load the settings.json into a settings object
with open('settings.json') as json_file:
    settings = json.load(json_file)


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
font = pygame.font.Font(settings['font'], settings['fontSize'])

small_font = pygame.font.Font(settings['font'], settings['fontSize'] // 2)



while True:

    # fill the screen with black

    screen.fill((0, 0, 0))

    # build a clock string of the current time in the format HH:MM:SS AM/PM
    # using the time module
    # %p to get AM or PM
    clock_string = time.strftime("%I:%M:%S")




    # make the hundreds of a second the current time in milliseconds
    # and convert it to a string with a leading zero if needed

    hundredths = str(int(time.time() * 100) % 100)

    if len(hundredths) == 1:
        hundredths = '0' + hundredths


    # create text of a clock face like 12:34:56 AM using the font we have selected
    text_time = font.render(clock_string, True, (255, 255, 255))

    # blit the text to the screen
    screen.blit(text_time, (screen_size[0] // 2 - text_time.get_width() // 2, screen_size[1] // 2 - text_time.get_height() // 2))

    # create text of the hundredths of a second
    text_hundredths = small_font.render(hundredths, True, (255, 255, 255))

    # blit the text_hundredths to the screen next to text_time
    screen.blit(text_hundredths, (screen_size[0] // 2 + text_time.get_width() // 2, screen_size[1] // 2 - text_time.get_height() // 2))

    # update the screen

    pygame.display.flip()

    # run at 60 fps
    clock.tick(settings['fps'])


    # check for events

    for event in pygame.event.get():

        # quit for basically any reason...
        if event.type in [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN ]:

            pygame.quit()

            exit()




