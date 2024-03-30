import os
import random
import sys
import math
import pygame as pg

from particle import Emitter


CAPTION = "Fire Example"
MAX_X = 100
MAX_Y = 400


class Control(object):
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        pg.mouse.set_pos(self.screen_rect.center)
        self.clock = pg.time.Clock()
        self.done = False
        self.fps = 20.0
        self.generator = self.make_emitter()
        self.tick = pg.time.get_ticks()

    def make_emitter(self):
        kwarg_dict = {
            "texture": FUZZ,
            "angle": (math.pi / 3, 2 * math.pi / 3),
            "speed": (0.1, 0.5),
            "size": (15, 20),
            "life_span": 20.0,
            "start_color": (
                random.randint(2, 255),
                random.randint(2, 255),
                random.randint(2, 255),
            ),
        }
        return Emitter(self.screen_rect.center, 150, **kwarg_dict)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True

    def update(self):
        self.generator.pos = [
            random.randint(0, MAX_X),
            random.randint(0, MAX_Y),
        ]  # pg.mouse.get_pos()

        self.generator.set_kwargs(
            {
                "life_span": random.randint(5, 25),
                "start_color": (
                    random.randint(2, 255),
                    random.randint(2, 255),
                    random.randint(2, 255),
                ),
            }
        )
        self.screen.fill(0)
        self.generator.update(self.screen, self.tick)

    def main_loop(self):
        while not self.done:
            self.tick = pg.time.get_ticks()
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)
            caption = "{} - FPS: {:.2f}".format(CAPTION, self.clock.get_fps())
            pg.display.set_caption(caption)


if __name__ == "__main__":
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode((MAX_X, MAX_Y))
    PATH = os.path.join("resources", "fuzzball.png")
    FUZZ = pg.image.load(PATH).convert_alpha()
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
