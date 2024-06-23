# SPDX-License-Identifier: MIT
"""
    this is a better version of sphinx.py that uses the GPU
"""
import json
import os
import random
import re

import pygame
import time
import paho.mqtt.client as mqtt
from PIL import ImageFont
from PIL import Image, ImageColor
from PIL import ImageDraw
from thefuzz import fuzz

WHISPER = ""
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

# Define constants
WIDTH = 75
HEIGHT = 350
FADE_SPEED = 5
IMAGE_PATHS = {
    "attract": ["./static/brain.png", "./static/clippy.png"],
    "humans": ["./static/batteries.png", "./static/hooman.png"],
    "keyword": ["./static/shrimp.png", "./static/vegan.png"],
}


def sanitize_filename(input_string):
    # Define the maximum length for the filename
    max_length = 32

    # Remove invalid characters (anything that's not alphanumeric, space, dot, hyphen, or underscore)
    sanitized_string = re.sub(r"[^a-zA-Z0-9 ._-]", "", input_string)

    # Replace spaces with underscores
    sanitized_string = sanitized_string.replace(" ", "_")

    # Trim the string to the maximum length
    if len(sanitized_string) > max_length:
        sanitized_string = sanitized_string[:max_length]

    # Ensure it doesn't end with a dot or hyphen
    sanitized_string = sanitized_string.rstrip(".-")

    # If the string becomes empty after sanitization, return a default name
    if not sanitized_string:
        return "default_filename"

    return sanitized_string


def create_text_image(text: str):
    # Define image dimensions
    width, height = 350, 75

    # Create a new image with a random background color
    background_color = tuple(random.choices(range(256), k=3))
    image = Image.new("RGB", (width, height), background_color)

    # Initialize ImageDraw
    draw = ImageDraw.Draw(image)

    # Load a decorative font
    try:
        # Make sure you have a decorative TTF font file available in your system or specify a valid path
        font = ImageFont.truetype("Kristi-Regular.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    # Get the size of the text
    # text_size = draw.textsize(text, font=font)
    c_width, c_height = draw.textsize(text, font=font)
    # Calculate the position to center the text
    text_x = (width - c_width) // 2
    text_y = (height - c_height) // 2

    # Generate a random but contrasting text color
    def get_contrasting_color(bg_color):
        return tuple((255 - c) for c in bg_color)

    text_color = get_contrasting_color(background_color)

    # Draw the text onto the image
    draw.text((text_x, text_y), text, font=font, fill=text_color)

    # Save or display the image
    # image.show()
    name = os.path.join("./keywords", sanitize_filename(text) + ".png")
    image.save(name)


def add_files_to_array(directory):
    files_array = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            files_array.append(os.path.join(directory, filename))
    return files_array


# generate images
for slogan in SLOGANS:
    create_text_image(slogan)
IMAGE_PATHS["keyword"] = add_files_to_array("./keywords")
IMAGE_PATHS["attract"] = add_files_to_array("./static")
# Initialize Pygame
pygame.init()
os.environ["SDL_VIDEO_WINDOW_POS"] = "%d, %d" % (0, 0)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)

pygame.display.set_caption("Mondo Buys Cats Display")


# Load images
def load_images(image_paths):
    return [pygame.image.load(path) for path in image_paths]


images = {mode: load_images(paths) for mode, paths in IMAGE_PATHS.items()}


# MQTT setup
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        # we should always subscribe from on_connect callback to be sure
        # our subscribed is persisted across reconnections.
        client.subscribe("eventq")


def on_message(client, userdata, msg):
    global mode, WHISPER
    mode = msg.payload.decode()
    try:
        explode = json.loads(mode)
        if explode["type"] == "whisper":
            print("heard hoomans... ", explode["value"])
            WHISPER = explode["value"]
    except Exception as e:
        print(e)
        return


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost")
client.loop_start()


# Display functions
def fade_in(image):
    image = pygame.transform.rotate(image, 90)
    for alpha in range(0, 256, FADE_SPEED):
        image.set_alpha(alpha)
        screen.fill((0, 0, 0))
        screen.blit(image, (0, 1))
        pygame.display.flip()
        time.sleep(0.01)


def fade_out(image):
    image = pygame.transform.rotate(image, 90)
    for alpha in range(255, -1, -FADE_SPEED):
        image.set_alpha(alpha)
        screen.fill((0, 0, 0))
        screen.blit(image, (0, 1))
        pygame.display.flip()
        time.sleep(0.01)


# Main loop
mode = "attract"
current_image_index = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if WHISPER != "":
        best_match = ""
        best_match_fuzz = 0
        for w in SLOGANS:
            if fuzz.ratio(WHISPER, w) > best_match_fuzz:
                best_match = w
                best_match_fuzz = fuzz.ratio(WHISPER, w)
                break
        if best_match_fuzz > 0:
            WHISPER = ""
            print("best match", best_match)
            current_images = images["keywords"]
            current_image = current_images[w]
            fade_in(current_image)
            time.sleep(2)
    current_images = images[mode]
    current_image = current_images[current_image_index]

    fade_in(current_image)
    time.sleep(2)  # Display image for 2 seconds
    fade_out(current_image)

    current_image_index = (current_image_index + 1) % len(current_images)

client.loop_stop()
pygame.quit()
