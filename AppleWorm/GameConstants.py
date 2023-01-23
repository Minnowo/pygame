import pygame
import math

WIDTH = 1324
HEIGHT = 1000

SCREEN_RECT = pygame.Rect(0, 0, WIDTH, HEIGHT)
SCREEN_RECT_EXTENDED = pygame.Rect(-250, -250, WIDTH + 250, HEIGHT + 250)

MOTION_NONE = 0
# these values are used to denote movement in a direction
MOTION_HORIZONTAL_NONE = 0b_0000
MOTION_HORIZONTAL_LEFT = 0b_0001
MOTION_HORIZONTAL_RIGHT = 0b_0010

MOTION_VERTICAL_NONE = 0b_0000
MOTION_VERTICAL_UP = 0b_0100
MOTION_VERTICAL_DOWN = 0b_1000

# used to extract the x and y motion from a direction integer
X_MOTION_MASK = 0b_0011
Y_MOTION_MASK = 0b_1100


PLAYER_TEAM = 1
ENEMY_TEAM = 2
NEUTRAL_TEAM = 3


DEGREE_90_RAD = math.radians(90)
DEGREE_180_RAD = math.radians(180)
DEGREE_270_RAD = math.radians(270)
