import pygame
import time
import random
import math
from typing import Sequence, Tuple

from . import GameEntities
from . import GameMath
from . import GameAssets as GA
from . import GameConstants as GC


def game_loop_menu():
    pass


def game_loop_gameplay():
    pass


def get_enemy():

    e = GameEntities.WanderingEntity(GA.Sprites.WATA_SPRITE_SHEET, "watamelon", 800, 800, 25, 15)
    e.set_hitbox_dynamic(True)
    e.set_team(GC.ENEMY_TEAM)
    # e.x, e.y = GameMath.get_random_point()
    return e


def main():

    # init pygame and load our assets
    pygame.init()
    GA.Fonts.init()
    GA.Sprites.init()

    player = GameEntities.Player(GA.Sprites.SEXY_SPRITE_SHEET, 0, 0, 40, 40)
    player.set_hitbox_dynamic(True)
    player.set_team(GC.PLAYER_TEAM)
    player.shoot_delay = 200
    player.render_bullet_path = True 
    player.bullet_speed = 90
    player.bullet_life = 500
    

    # set up window
    GAME_WINDOW = pygame.display.set_mode((GC.WIDTH, GC.HEIGHT))
    GAME_WINDOW.fill((0, 0, 0))

    FRAME_TIME = 30

    time_increment = 500
    time_until_new_enemy = time_increment

    last_dead_clearout_interval = 30 * 1000
    last_dead_clearout = 0

    entities: Sequence[GameEntities.Entity] = [get_enemy() for i in range(5)]

    play_game = True
    while play_game:

        pygame.display.update()
        pygame.time.delay(FRAME_TIME)

        game_ticks = pygame.time.get_ticks()

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

        text = GA.Fonts.FONT_CONSOLAS.render(
            f"Objective: Survive {game_ticks//1000}", True, (255, 255, 255)
        )
        text_rect = text.get_rect(x=0, y=0)

        GAME_WINDOW.blit(GA.Sprites.BACKGROUND1_SPRITE, GA.Sprites.BACKGROUND1_RECT)
        GAME_WINDOW.blit(text, text_rect)

        player.handle_input(keys)
        player.perform_task()
        player.render(GAME_WINDOW)

        for entity in filter(GameEntities.Entity.entity_is_not_dead, entities):
            
            bullet = player.get_bullet_collided_with(entity)
            
            if bullet:

                if entity.take_damage_and_died(bullet.get_entity_damage()):
                    continue

            entity.perform_task()
            entity.render(GAME_WINDOW)

            if entity.collides_with(player):

                player.take_damage_and_died(entity.get_entity_damage())


