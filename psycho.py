import datetime
import os
from time import sleep

import pygame
import random

ATTRACT = [
    "clippy has the answers",
    "ask for the answers",
    "don't listen to clippy",
    "clippy tiene las respuestas",
    "pide las respuestas",
    "no escucha clippy",
    "clippy hat die antworten",
    "fragen sie nach den antworten",
    "hören sie nicht auf clippy",
    "clippy a les réponses",
    "demandez les réponses",
    "n'écoutez pas clippy",
    "clippy tem as respostas",
    "peça as respostas",
    "não ouça clippy",
]
os.environ["SDL_VIDEO_WINDOW_POS"] = "%d, %d" % (0, 0)
# Initialize Pygame
pygame.init()

# Set the dimensions of the window
width = 75
height = 375

# Create the window
window = pygame.display.set_mode((width, height), pygame.NOFRAME)


# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the window with a random color
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    window.fill((r, g, b))
    if random.randint(0, 100) < 10:  # 10% chance each frame
        # Create a font object
        font = pygame.font.Font(None, 36)
        if random.randint(0, 100) > 10:
            text_content = random.choice(ATTRACT)
        else:
            text_content = str(datetime.datetime.now().time())
        # Create a surface with the text
        text = font.render(text_content, True, (0, 0, 0))
        text = pygame.transform.rotate(text, 90)
        # Fill the window with white
        window.fill((255, 255, 255))

        # Blit the text onto the window
        window.blit(
            text,
            (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2),
        )

        # Update the display
        pygame.display.flip()

        # Pause for 2 seconds
        pygame.time.wait(2000)

    # Update the display
    pygame.display.flip()
    sleep(0.5)

# Quit Pygame
pygame.quit()
