import numpy as np
import pygame

from . import GameConstants as GC


def get_random_wait_time(min, max):

    return np.random.randint(min, max)


def get_random_point(x: int = 50, y: int = 50, width: int = GC.WIDTH - 50, height: int = GC.HEIGHT - 50):

    return (np.random.randint(x, width), np.random.randint(y, height))


def get_vector(bullet_x: int, bullet_y: int, target_x: int, target_y: int, strength: int):

    x, y = get_normalized_vector(bullet_x, bullet_y, target_x, target_y)

    return target_x + x * strength, target_y + y * strength


def is_rect_off_screen(rect: pygame.Rect):

    return not GC.SCREEN_RECT.colliderect(rect)


def is_rect_off_screen_extended(rect: pygame.Rect):

    return not GC.SCREEN_RECT_EXTENDED.colliderect(rect)


def get_normalized_vector(px1, py1, px2, py2):

    dist = distance_between(px1, py1, px2, py2)

    return (px2 - px1) / dist, (py2 - py1) / dist


def distance_between(x1, y1, x2, y2):

    return ((x1 - x2) ** 2 + (y1 - y2) ** 2.0) ** (0.5)


def move_towards(x1: int, y1: int, x2: int, y2: int, x_speed: float, y_speed: float):

    dist_x = x1 - x2
    dist_y = y1 - y2

    steps_number = max(abs(dist_x), abs(dist_y))

    if steps_number == 0:
        return 0, 0

    stepx = float(dist_x) / (steps_number / x_speed)
    stepy = float(dist_y) / (steps_number / y_speed)

    return stepx, stepy


def invert_color(color: tuple[int, int, int]):

    return (255 - color[0], 255 - color[1], 255 - color[2])
