import pygame
import numpy.random as random
from . import GameConstants as GC


def prepare_sprite_sheet(sprite: pygame.Surface, scale_to: bool = None, flip: bool = False):

    if scale_to:

        _ = pygame.transform.scale(sprite, scale_to)
        del sprite
        sprite = _

    if flip:
        _ = pygame.transform.flip(sprite, True, False)
        del sprite
        sprite = _

    sheet = {}

    sheet[GC.MOTION_VERTICAL_UP] = pygame.transform.rotate(sprite, 90)
    # sheet['up'] = pygame.transform.rotate(sprite, 90)
    sheet[GC.MOTION_VERTICAL_DOWN] = pygame.transform.rotate(sprite, 270)
    # sheet['down'] = pygame.transform.rotate(sprite, 270)

    sheet[GC.MOTION_NONE] = sprite

    sheet[GC.MOTION_HORIZONTAL_RIGHT] = sprite
    # sheet['right'] = sprite
    sheet[GC.MOTION_HORIZONTAL_RIGHT | GC.MOTION_VERTICAL_UP] = pygame.transform.rotate(sprite, 15)
    # sheet['rightup'] = pygame.transform.rotate(sprite, 15)
    sheet[GC.MOTION_HORIZONTAL_RIGHT | GC.MOTION_VERTICAL_DOWN] = pygame.transform.rotate(sprite, -15)
    # sheet['rightdown'] = pygame.transform.rotate(sprite, -15)

    sprite = pygame.transform.flip(sprite, True, False)
    sheet[GC.MOTION_HORIZONTAL_LEFT] = sprite
    # sheet['left'] = sprite
    sheet[GC.MOTION_HORIZONTAL_LEFT | GC.MOTION_VERTICAL_UP] = pygame.transform.rotate(sprite, -15)
    # sheet['leftup'] = pygame.transform.rotate(sprite, -15)
    sheet[GC.MOTION_HORIZONTAL_LEFT | GC.MOTION_VERTICAL_DOWN] = pygame.transform.rotate(sprite, 15)
    # sheet['leftdown'] = pygame.transform.rotate(sprite, 15)

    return sheet


def get_team_color(team: int):

    if team == 1:
        return Colors.TEAM_1

    if team == 2:
        return Colors.TEAM_2

    if team == 3:
        return Colors.TEAM_3

    return Colors.WHITE


class Colors:

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    TEAM_1 = GREEN
    TEAM_2 = RED
    TEAM_3 = BLUE

    @staticmethod
    def random_color():
        return (random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))


class Sprites:

    BACKGROUND1_SPRITE: pygame.Surface = None
    BACKGROUND1_RECT: pygame.Rect = None

    PLAYER_SPRITE_SHEET: dict[int, pygame.Surface] = None

    SEXY_SPRITE_SHEET: dict[int, pygame.Surface] = None

    WATA_SPRITE_SHEET: dict[int, pygame.Surface] = None

    BULLET_1_SPRITE: pygame.Surface = None

    @staticmethod
    def init():

        # .convert() for more performance, requires that pygame.display.set_mode(( has been called
        Sprites.BACKGROUND1_SPRITE = pygame.image.load("./assets/background.png").convert_alpha()
        Sprites.BACKGROUND1_RECT = Sprites.BACKGROUND1_SPRITE.get_rect()

        Sprites.PLAYER_SPRITE_SHEET = prepare_sprite_sheet(pygame.image.load("./assets/worm1.png").convert_alpha())

        Sprites.SEXY_SPRITE_SHEET = prepare_sprite_sheet(
            pygame.image.load("./assets/sexyworm.png").convert_alpha(), scale_to=(87, 223)
        )

        Sprites.WATA_SPRITE_SHEET = prepare_sprite_sheet(
            pygame.image.load("./assets/watamelon1.png").convert_alpha(), scale_to=(150, 135), flip=True
        )

        Sprites.BULLET_1_SPRITE = pygame.image.load("./assets/rock.png").convert_alpha()


class Fonts:

    FONT_CONSOLAS: pygame.font.Font = None

    @staticmethod
    def init():

        Fonts.FONT_CONSOLAS = pygame.font.Font("./assets/fonts/consolas.ttf", 32)
