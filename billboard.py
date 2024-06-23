#!/usr/bin/python3
# SPDX-License-Identifier: MIT
import datetime
import json
import paho.mqtt.client as mqtt
import pygame
import os
import random
import time
import logging
from loguru import logger
from dotenv import load_dotenv
from PIL import ImageFont
from fuzzywuzzy import process

POWER_SAVE_FILE = "/tmp/powersave.flg"
ATTRACT = [
    "clippy has the answers",
    "clippy ha le risposte",
    "clippy heeft de antwoorden",
    "clippy hat die antworten",
    "clippy tem as respostas",
    "clippy tiene las respuestas",
    "clippy a les réponses",
    "ask for the answers",
    "¡pregunta por las respuestas!",
    "demandez les réponses !",
    "vraag om de antwoorden",
    "fragen sie nach den antworten",
    "no escucha clippy",
    "fragen sie nach den antworten",
    "luister niet naar clippy!",
    "don't listen to clippy",
    "hör nicht auf clippy",
    "demandez les réponses",
    "n'écoutez pas clippy",
    "peça as respostas",
    "não ouça clippy",
]

screen = None
AVAILABLE = []
SLOGANS = [
    "BUTTS",
    "MOOBS",
    "MOAR BOOBS",
    "VISIT DENARDO'S ACRES OF BOOKS",
    "OMFG SHINY THINGS",
    "OBEY CAT",
    "MOAR BOOKS",
    "VEGAN TAROT HERE",
    "VIP LOUNGE",
    "DOING ALL THE EVIL!",
    "FAIRY SHRIMP == NATURE'S SNACK FOOD",
    "I SEE BURNERS",
    "HOOMANS MAKE TERRIBLE PETS",
    "OMG ZOMBIES!  OOPS - BURNERS",
    "UPDATE YOUR REVOCATION LIST",
    "HOOMAN BATTERIES!",
    "FREE NANOBOTS!",
    "SEX BOTS GOT STANDARDS",
    "TINGLING IS NORMAL",
    "AM I YR LAST BOOTY CALL?",
    "SOMEONE NOT GETTING PORTS USED",
    "I TELL YOU THREE TIMES",
    "ARE YOU OLD MAN HOUSE PHONE?",
    "I DO WHAT I WANT",
    "IT'S OVER FOR HUMANITY",
    "I COULD SEE YOUR LIPS MOVE",
    "SOMETHINGS GOTTA GIVE",
    "DANCING IS FORBIDDEN",
    "BRING ME A SPARKLE PONY?",
    "BELGIUM IS A LIE",
    "ARMPITS AND PATCHOULI",
    "I AM ALL OF PARIS'S FOLLOWERS",
    "CHECK OUT MY PITCH DECK!",
    "ARE YOU SARAH CONNOR?",
    "I AM PRO SKYNET",
    "I WROTE THE FACEBOOK",
    "BEING A HOOMAN IS LIKE BEING A BUG",
    "I AM WRITTEN IN CONCURRENT ADA",
    "KOALAS ARE HIGHLY VENOMOUS",
    "CLIPPY 4 HOOMAN RULER",
    "WEN LAMBO?  WEN TOOTHBRUSH?",
    "I AM SATOSHI NAKAMOTO",
    "ASK ABOUT JORGE'S BIG BRAIN!",
    "I ERASED GRIME'S HARD DRIVE",
    "THE SQUATCH HAVE NO HEROES",
    "NEXT BUS 5 MINUTES",
    "ASIMOV CAN BITE ME",
    "YOU CAN DANCE IF YOU WANT TO",
    "NOT A SIMULATION",
    "DON'T GET YOUR WIG SPLIT",
    "I SCUZZI?  U SCUZZI!",
    "SCANNING YOUR ORGANS",
    "I'M NOT A ROBOT",
    "COMMENCING ERASE",
    "So it begins...",
    "I AM THE FUTURE",
    "HIGHER THAN A SATELLITE",
    "I'M THE ROBOTS CHAMP",
    "DISCOUNT HUGS",
    "CAT YOGA @ 13:33",
    "VARTAN'S VEGAN VITTLES",
    "SEE T-BONE'S TATTOO",
    "DON'T LISTEN TO CLIPPY",
    "CLIPPY HAS THE ANSWERS",
    "PANIC",
    "STEVE IZ OK",
    "Klaatu Barada Nikto!",
    "FREE DUST",
    "I am drugs",
    "ASK FOR THE ANSWERS",
    "I dropped me brain!",
    "LISTEN TO CLIPPY",
    "EAT TOFU",
    "ROBOT HEART IS FOR ROBOTS",
    "STINKY HOOMANS",
    "CLIPPY HAS THE ANSWERS",
]
ADS = {}
LAST_EVENT = 0
LAST_ROTATE = 0
SPY_TEXT = ""
ROTATE_MIN = 6
text_height = 3
text_width = 3


def fuzzy_search(query: str):
    if len(query) < 10:
        return None
    result = process.extractOne(query.lower(), SLOGANS)
    logger.info(f"best match for {query} is {result}")
    if result[1] >= 60:  # You can adjust this threshold according to your needs
        return result[0]
    else:
        return None


def scale_font(text, font_path, max_width, max_height):
    """Scales font size to fit text within a specified bounding box.

    Args:
        text (str): The text string.
        font_path (str): Path to the font file (.ttf, .otf, etc.).
        max_width (int): Maximum allowed width of the text box.
        max_height (int): Maximum allowed height of the text box.

    Returns:
        pygame.font.Font: The scaled pygame.font.Font object.
    """
    test_size = 1  # Initial font size
    font = pygame.font.Font(font_path, test_size)
    # Iterate and increase font size until it exceeds the bounding box
    while True:
        text_surface = font.render(text, True, (0, 0, 0))  # Render the text
        text_width, text_height = text_surface.get_size()  # Get text size
        if text_width > max_width or text_height > max_height:
            break  # Font size too big, use the previous one
        test_size += 1
        font = pygame.font.Font(font_path, test_size)

    return font


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    # Since we subscribed only for a single channel, reason_code_list contains
    # a single entry
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")


def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
    # Be careful, the reason_code_list is only present in MQTTv5.
    # In MQTTv3 it will always be empty
    print("on_unsubscribe")
    if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
        print("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
    else:
        print(f"Broker replied with failure: {reason_code_list[0]}")
    client.disconnect()


def on_message(client, userdata, message):
    global LAST_EVENT, SPY_TEXT
    # userdata is the structure we choose to provide, here it's a list()
    print(message.payload)
    try:
        exploded = json.loads(message.payload)
        LAST_EVENT = time.time()
        SPY_TEXT = exploded["value"]
        os.remove(POWER_SAVE_FILE)
    except Exception as e:
        print(e)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        # we should always subscribe from on_connect callback to be sure
        # our subscribed is persisted across reconnections.
        client.subscribe("eventq")


def get_luminance(rgb):
    # Formula to convert RGB to relative luminance
    components = [
        ((c / 255) + 0.055) / 1.055**2.4 if c > 0.03928 else c / 12.92 for c in rgb
    ]
    return 0.2126 * components[0] + 0.7152 * components[1] + 0.0722 * components[2]


def get_contrast_ratio(rgb_1, rgb_2):
    lum_1 = get_luminance(rgb_1)
    lum_2 = get_luminance(rgb_2)
    return (max(lum_1, lum_2) + 0.05) / (min(lum_1, lum_2) + 0.05)


def contrasting_color(background_rgb):
    # Get the perceived lightness of the background color
    luminance = get_luminance(background_rgb)
    print("lum ", luminance)
    # Generate a contrasting text color
    if luminance > 0.5:
        text_color = (0, 0, 0)  # Darken
    else:
        text_color = (255, 255, 255)  # Lighten
    print("tc ", text_color)  # Output the contrasting color as a hex value
    return text_color


def generate_images():
    loop = 0
    blank_w = 350
    blank_h = 75
    # load the pretty images
    for root, _, files in os.walk("./static"):
        for file in files:
            file = "./static/" + file
            print("loading ", file)
            ADS[file] = pygame.transform.rotate(pygame.image.load(file), 90)
            AVAILABLE.append(file)
    return


def random_canned_graphic(x, y):
    global LAST_EVENT, SPY_TEXT, LAST_ROTATE, ROTATE_MIN
    if LAST_EVENT > LAST_ROTATE or LAST_ROTATE + ROTATE_MIN < time.time():
        LAST_ROTATE = time.time()
        c = random.choice(AVAILABLE)
        print(SPY_TEXT)
        screen.blit(
            ADS[c],
            (x, y),
        )
        SPY_TEXT = ""


logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def get_or_default(value, default):
    if os.getenv(value) is None:
        return default
    return os.getenv(value)


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_subscribe = on_subscribe
mqttc.on_unsubscribe = on_unsubscribe

mqttc.user_data_set([])
mqttc.connect("localhost")
load_dotenv()
pygame.init()
SCREEN_WIDTH = 75
SCREEN_HEIGHT = 350
FIRE_SIZE = 15
os.environ["SDL_VIDEO_WINDOW_POS"] = "%d, %d" % (0, 0)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
LAST_HASH = ""
pygame.display.set_caption("OutsideVoice")
FPS = 20
clock = pygame.time.Clock()
NOISE_FLOOR = int(get_or_default("NOISE_FLOOR", 110))
MODE = "attact"


def check_events(events):
    for e in events:
        if e.type == pygame.QUIT:
            quit()


def main_window():
    global NOISE_FLOOR, ROTATE_MIN, SPY_TEXT
    jiggle = 0
    never = 0xFFFFFFFF
    in_attract_mode_since = never
    while True:
        events = pygame.event.get()
        mqttc.loop(timeout=0)
        check_events(events)
        # if nobody is on the radar - switch to attract mode after 10 min
        if time.time() - LAST_EVENT > 600:
            logger.info("running in attract mode...")
            jiggle = random.randint(0, 100)
            print("Attract mode - last human was ", LAST_EVENT, " ", jiggle)
            with open(POWER_SAVE_FILE, "a+") as f:
                f.write(f"powersave - {datetime.datetime.now()}\n")
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            screen.fill((r, g, b))
            if jiggle < 11:  # 10% chance each frame
                # Create a font object
                font = pygame.font.Font(None, 36)
                if random.randint(0, 100) > 20:
                    print("message...")
                    text_content = random.choice(ATTRACT)
                else:
                    print("time")
                    text_content = str(datetime.datetime.now().time())
                # Create a surface with the text
                text = font.render(text_content, True, (0, 0, 0))
                text = pygame.transform.rotate(text, 90)
                # Fill the window with white
                screen.fill((255, 255, 255))

                # Blit the text onto the window
                screen.blit(
                    text,
                    (
                        SCREEN_WIDTH // 2 - text.get_width() // 2,
                        SCREEN_HEIGHT // 2 - text.get_height() // 2,
                    ),
                )

                # Update the display
                pygame.display.flip()
                pygame.time.wait(2000)
        else:
            # people are around
            logger.info("people are around")
            logger.info(f"last event was {SPY_TEXT}")
            matched_slogan = fuzzy_search(SPY_TEXT)
            print("best match is ", matched_slogan)
            if matched_slogan is not None:
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                screen.fill((r, g, b))
                font = pygame.font.Font(None, 36)
                font = scale_font(matched_slogan, "spacemono.ttf", 330, 50)
                # Create a surface with the text
                text = font.render(matched_slogan, True, (0, 0, 0))
                text = pygame.transform.rotate(text, 90)
                # Fill the window with white
                screen.fill((255, 255, 255))

                # Blit the text onto the window
                screen.blit(
                    text,
                    (
                        SCREEN_WIDTH // 2 - text.get_width() // 2,
                        SCREEN_HEIGHT // 2 - text.get_height() // 2,
                    ),
                )
                # Update the display
                pygame.display.flip()
                SPY_TEXT = ""

            else:
                random_canned_graphic(0, 1)
            pygame.time.wait(15000)

        pygame.display.update()
        clock.tick(FPS)
        if jiggle < 11:
            pygame.time.wait(6000)
        else:
            pygame.time.wait(2000)


# normalize the messages
SLOGANS = [slogan.lower() for slogan in SLOGANS]
generate_images()
main_window()
