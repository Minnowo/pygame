import pygame
import time
import random
import math
import os
from typing import Sequence, Tuple

from . import GameEntities
from . import GameMath
from . import GameAssets as GA
from . import GameConstants as GC
from . import GameParticles


def set_dpi_aware():
    if os.name == "nt":
        try:
            import ctypes

            awareness = ctypes.c_int()
            error_Code = ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))
            error_Code = ctypes.windll.shcore.SetProcessDpiAwareness(2)
            success = ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass


def game_loop_menu():
    pass


def game_loop_gameplay():
    pass


def delay(func, *, delay=400, delay_map={}):

    delay_map[func.__hash__()] = 0

    def wrapper(*args, **kwargs):

        if kwargs.get("skip", False) or delay_map[func.__hash__()] + delay < pygame.time.get_ticks():

            delay_map[func.__hash__()] = pygame.time.get_ticks()

            if "skip" in kwargs:
                del kwargs["skip"]

            return func(*args, **kwargs)

        return None

    return wrapper


@delay
def get_enemy(wander=True, x=800, y=800):

    if wander:
        e = GameEntities.WanderingEntity(GA.Sprites.WATA_SPRITE_SHEET, "watamelon", x, y, 30, 30)
    else:
        e = GameEntities.Entity(GA.Sprites.WATA_SPRITE_SHEET, "watamelon", x, y, 30, 30)

    e.set_hitbox_dynamic(True)
    e.set_team(GC.ENEMY_TEAM)
    e.damage = 10
    # e.x, e.y = GameMath.get_random_point()
    return e


@delay
def spawn_circle(list):
    list.create_particle()


def advance(loc, angle, amt):
    new_loc = loc.copy()
    new_loc[0] += math.cos(math.radians(angle)) * amt
    new_loc[1] += math.sin(math.radians(angle)) * amt
    return new_loc


def create_enemy_death_explosion(circle_effect: GameParticles.ExpandingCircle, x: int, y: int):

    circle_effect.create_particle(x=x, y=y, decay_rate=1, radius=10, expand_rate=20, expand_rate_change=0.15, line_width=5)

    circle_effect.create_particle(x=x, y=y, decay_rate=1, radius=80, expand_rate=-10, expand_rate_change=2, line_width=5)


def create_player_death_explosion(
    circle_effect: GameParticles.ExpandingCircle, square_effect: GameParticles.FallingSquareEffect, player: GameEntities.Entity
):
    circle_effect.create_many_in_bounds(
        15, player.x - player.width // 2, player.y - player.height // 2, player.width, player.height
    )
    square_effect.create_many_in_bounds(
        15,
        player.x - player.width // 2,
        player.y - player.height // 2,
        player.width,
        player.height,
        color=GA.Colors.WHITE,
        decay_rate=1.5,
    )


display = pygame.Surface((300, 200))
display_bg = (255, 255, 255)  # (20, 19, 39)


def render_side_fog(GAME_WINDOW, game_time):

    w, h = display.get_width(), display.get_height()

    # spans the entire width, and 33% of the height
    effect_1_percent = 0.33
    effect1_width, effect1_height = w, h * effect_1_percent
    effect1_color1 = (15, 10, 24)
    effect1_color2 = (0, 0, 0)
    var1 = effect1_height / 4

    # spans the entire width, and 12.5% of the height
    effect_2_percent = 0.125
    effect_2_percent *= 2
    effect2_width, effect2_height = w, h * effect_2_percent
    effect2_color1 = (0, 0, 0)
    effect2_color2 = (0, 2, 4)
    var2 = effect2_height / 2

    # clear old effects and set background
    display.fill(display_bg)

    # effect 1

    b2_points = (
        ((effect1_width, var1),)
        + tuple(
            (
                effect1_width - (effect1_width / 30 * (i + 1) + math.sin((game_time + i * 120) / 10) * 8),
                3 * (var1 + math.sin((game_time + i * 10) / 10) * 4),
            )
            for i in range(29)
        )
        + ((0, var1), (0, 0), (w, 0))
    )
    back_surf = pygame.Surface((effect1_width, effect1_height))
    pygame.draw.polygon(back_surf, effect1_color1, b2_points)
    back_surf.set_colorkey(effect1_color2)
    display.blit(back_surf, (0, 0))
    display.blit(pygame.transform.flip(back_surf, False, True), (0, h - effect1_height))

    # effect 2
    b_points = (
        ((0, var2),)
        + tuple(
            (w / 30 * (i + 1) + math.sin((game_time + i * 120) / 4) * 8, var2 + math.sin((game_time + i * 10) / 10) * 4)
            for i in range(29)
        )
        + ((w, var2), (w, 0), (0, 0))
    )

    fog_surf = pygame.Surface((effect2_width, effect2_height))
    pygame.draw.polygon(fog_surf, effect2_color2, b_points)
    fog_surf.set_alpha(150)
    fog_surf.set_colorkey(effect2_color1)

    display.blit(pygame.transform.flip(fog_surf, True, False), (0, -6))
    display.blit(fog_surf, (0, 0))
    display.blit(pygame.transform.flip(fog_surf, True, True), (0, h - effect2_height + 6))
    display.blit(pygame.transform.flip(fog_surf, False, True), (0, h - effect2_height))

    side_fog = pygame.transform.scale(pygame.transform.rotate(fog_surf, 90), (effect2_height, h))
    display.blit(pygame.transform.flip(side_fog, False, True), (-6, 0))
    display.blit(side_fog, (0, 0))
    display.blit(pygame.transform.flip(side_fog, True, True), (w - effect2_height, 0))
    display.blit(pygame.transform.flip(side_fog, True, False), (w - effect2_height + 6, 0))

    # actually render the effect to the game window
    GAME_WINDOW.blit(pygame.transform.scale(display, GAME_WINDOW.get_size()), (0, 0))


def main():
    set_dpi_aware()

    # init pygame and load our assets
    pygame.init()

    # set up window, important this comes before Sprites.init()
    GAME_WINDOW = pygame.display.set_mode((GC.WIDTH, GC.HEIGHT), pygame.SCALED + pygame.RESIZABLE)
    GAME_WINDOW.fill((0, 0, 0))

    GA.Fonts.init()
    GA.Sprites.init()

    player = GameEntities.Player(GA.Sprites.SEXY_SPRITE_SHEET, 0, 0, 20, 20)
    player.set_hitbox_dynamic(True)
    player.set_team(GC.PLAYER_TEAM)
    player.shoot_delay = 200
    player.render_bullet_path = True
    player.bullet_speed = 70
    player.bullet_life = 500
    player.bullet_damage = 40
    player.bullet_hp = 10000000

    FRAME_RATE = 24

    time_increment = 500
    time_until_new_enemy = time_increment

    last_dead_clearout_interval = 30 * 1000
    last_dead_clearout = 0

    entities: Sequence[GameEntities.Entity] = [get_enemy(False, 50 + i * 200, 500, skip=True) for i in range(5)]

    clock = pygame.time.Clock()

    square_effect = GameParticles.FallingSquareEffect(GA.Colors.BLACK)
    circle_effect = GameParticles.ExpandingCircle(GA.Colors.WHITE)
    player.bullet_effect_renders.append(circle_effect)

    game_time = 0

    play_game = True
    while play_game:

        pygame.display.update()
        clock.tick(FRAME_RATE)

        game_ticks = pygame.time.get_ticks()
        game_time += 1

        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        for event in events:
            if event.type == pygame.QUIT:
                play_game = False

        if last_dead_clearout + last_dead_clearout_interval < game_ticks:

            last_dead_clearout = game_ticks

            _ = len(entities)
            entities = list(filter(GameEntities.Entity.entity_is_not_dead, entities))

            print(f"Cleared out dead entities: {_ - len(entities)}")

        text = GA.Fonts.FONT_CONSOLAS.render(f"Objective: Survive {game_ticks//1000} HP: {player.hp}", True, (255, 255, 255))
        text_rect = text.get_rect(x=0, y=0)

        GAME_WINDOW.blit(GA.Sprites.BACKGROUND1_SPRITE, GA.Sprites.BACKGROUND1_RECT)

        render_side_fog(GAME_WINDOW, game_time)

        square_effect.create_particle_on_chance(0.6)
        square_effect.render(GAME_WINDOW)

        GAME_WINDOW.blit(text, text_rect)

        if keys[pygame.K_g]:
            e = get_enemy(True, *pygame.mouse.get_pos())
            if e:
                entities.append(e)

        if keys[pygame.K_h]:
            e = get_enemy(False, *pygame.mouse.get_pos())
            if e:
                entities.append(e)

        if keys[pygame.K_k]:
            spawn_circle(circle_effect)

        if keys[pygame.K_l]:
            create_player_death_explosion(circle_effect, square_effect, player)
        if keys[pygame.K_m]:

            mousex, mousey = pygame.mouse.get_pos()

            circle_effect.create_particle(
                x=mousex, y=mousey, radius=4, line_width=4, decay_rate=0.2, expand_rate=4, expand_rate_change=0.3
            )

        player.handle_input(keys)
        player.perform_task()
        player.render(GAME_WINDOW)

        for entity in filter(GameEntities.Entity.entity_is_not_dead, entities):

            if keys[pygame.K_j]:
                entity.move_towards(*pygame.mouse.get_pos())

            bullet = player.get_bullet_collided_with(entity)

            if bullet:

                bullet.take_damage_no_i_frames(entity.get_entity_damage())

                if entity.take_damage_and_died(bullet.get_entity_damage()):

                    circle_effect.create_many_in_bounds(
                        3, entity.x - entity.width // 2, entity.y - entity.height // 2, entity.width, entity.height
                    )
                    square_effect.create_many_in_bounds(
                        10,
                        entity.x - entity.width // 2,
                        entity.y - entity.height // 2,
                        entity.width,
                        entity.height,
                        color=GA.Colors.WHITE,
                        decay_rate=1.5,
                    )
                    continue

            entity.perform_task()
            entity.render(GAME_WINDOW)

            if entity.collides_with(player):

                if player.take_damage_and_died(entity.get_entity_damage()):

                    create_player_death_explosion(circle_effect, square_effect, player)

        circle_effect.render(GAME_WINDOW)
