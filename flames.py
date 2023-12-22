import datetime
import math
import struct

import pyaudio
import pygame
import os
import random
import time

SAMPLES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
pygame.init()
SCREEN_WIDTH = 150
SCREEN_HEIGHT = 650
FIRE_SIZE = 10
os.environ["SDL_VIDEO_WINDOW_POS"] = "%d, %d" % (150, 50)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("OutsideVoice")
FPS = 30
clock = pygame.time.Clock()


class FlameParticle:
    alpha_layer_qty = 2
    alpha_glow_difference_constant = 2

    def __init__(self, x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 4, r=15):
        self.x = x
        self.y = y
        self.r = r
        self.original_r = r
        self.alpha_layers = FlameParticle.alpha_layer_qty
        self.alpha_glow = FlameParticle.alpha_glow_difference_constant
        max_surf_size = (
            2 * self.r * self.alpha_layers * self.alpha_layers * self.alpha_glow
        )
        self.surf = pygame.Surface((max_surf_size, max_surf_size), pygame.SRCALPHA)
        self.burn_rate = 0.01 * random.randint(1, 10)

    def update(self):
        self.y -= 7 - self.r
        self.x += random.randint(-self.r, self.r)
        self.original_r -= self.burn_rate
        self.r = int(self.original_r)
        if self.r <= 0:
            self.r = 1

    def draw(self):
        max_surf_size = (
            2 * self.r * self.alpha_layers * self.alpha_layers * self.alpha_glow
        )
        self.surf = pygame.Surface((max_surf_size, max_surf_size), pygame.SRCALPHA)
        for i in range(self.alpha_layers, -1, -1):
            alpha = 255 - i * (255 // self.alpha_layers - 5)
            if alpha <= 0:
                alpha = 0
            radius = self.r * i * i * self.alpha_glow
            if self.r == 4 or self.r == 3:
                r, g, b = (255, 0, 255)
            elif self.r == 2:
                r, g, b = (255, 150, 0)
            else:
                r, g, b = (59, 7, 57)
            # r, g, b = (0, 0, 255)  # uncomment this to make the flame blue
            color = (r, g, b, alpha)
            pygame.draw.circle(
                self.surf,
                color,
                (self.surf.get_width() // 2, self.surf.get_height() // 2),
                radius,
            )
        screen.blit(self.surf, self.surf.get_rect(center=(self.x, self.y)))


class Flame:
    def __init__(self, x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT * 0.9):
        self.x = x
        self.y = y
        self.flame_intensity = 1
        self.flame_particles = []
        for i in range(self.flame_intensity * 25):
            self.flame_particles.append(
                FlameParticle(
                    self.x + random.randint(-1 * FIRE_SIZE, FIRE_SIZE),
                    self.y,
                    random.randint(1, FIRE_SIZE),
                )
            )

    def draw_flame(self):
        for i in self.flame_particles:
            if i.original_r <= 0:
                self.flame_particles.remove(i)
                self.flame_particles.append(
                    FlameParticle(
                        self.x + random.randint(-1 * FIRE_SIZE, FIRE_SIZE),
                        self.y,
                        random.randint(1, FIRE_SIZE),
                    )
                )
                del i
                continue
            i.update()
            i.draw()


flame = Flame()


def draw_game_over_screen():
    number_samples = len(SAMPLES)
    each_height = SCREEN_HEIGHT / number_samples
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont("arial", 40)
    title = font.render("Game Over", True, (255, 255, 255))
    restart_button = font.render("R - Restart", True, (255, 255, 255))
    quit_button = font.render("Q - Quit", True, (255, 255, 255))
    color = (0, 55, 255, 1)
    for i in range(number_samples):
        color = (0, SAMPLES[i], 255, 1)
        # data is 0-255 for sample of voice (byte)
        width = SCREEN_WIDTH * (255 / SAMPLES[i])
        pygame.draw.rect(screen, color, (0, i * each_height, width, each_height))
        pygame.display.update()


MODE = "running"


def rms(data_in):
    count = len(data_in) / 2
    format = "%dh" % (count)
    shorts = struct.unpack(format, data_in)
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0 / 32768)
        sum_squares += n * n
    level = math.sqrt(sum_squares / count) * 9000
    print("level ", level)
    return min(level, 255)


def check_events(events):
    for e in events:
        if e.type == pygame.QUIT:
            quit()


def empty_queue():
    for i in SAMPLES:
        if i > 25:
            print("QUEUE IS NOT EMPTY")
            return False
    return True


def main_window():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    DEVICE = 7
    RATE = 44100
    RECORD_SECONDS = 5

    if os.path.exists("production.txt"):
        DEVICE = 5

    start = time.time()
    p = pyaudio.PyAudio()
    print("----------------------record device list---------------------")
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get("deviceCount")
    for i in range(0, numdevices):
        if (
            p.get_device_info_by_host_api_device_index(0, i).get("maxInputChannels")
        ) > 0:
            print(
                "Input Device id ",
                i,
                " - ",
                p.get_device_info_by_host_api_device_index(0, i).get("name"),
            )
    print("USING ", DEVICE)
    RATE = int(p.get_device_info_by_index(DEVICE)["defaultSampleRate"])
    print(RATE)
    print("-------------------------------------------------------------")
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=DEVICE,
        frames_per_buffer=CHUNK,
    )
    while True:
        events = pygame.event.get()
        check_events(events)
        # sample mic
        data = stream.read(CHUNK, exception_on_overflow=False)
        # pop old
        SAMPLES.pop(0)
        # append new level sound level
        SAMPLES.append(rms(data))
        if time.time() - start > 2:
            global MODE
            if empty_queue() and MODE == "running":
                MODE = "attract"
            else:
                MODE = "running"
            start = time.time()
        if MODE == "attract":
            screen.fill((0, 0, 0))
            flame.draw_flame()
            pygame.display.update()
            clock.tick(FPS)
        else:
            draw_game_over_screen()
            clock.tick(1)


main_window()
