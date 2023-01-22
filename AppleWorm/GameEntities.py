import pygame
import random
import numpy as np
from typing import Sequence

from . import GameAssets as GA
from . import GameConstants as GC
from . import GameMath


class Entity:
    def __init__(
        self,
        sprite_sheet: dict[int, pygame.Surface],
        name: str,
        x: int = 0,
        y: int = 0,
        x_speed: int = 10,
        y_speed: int = 10,
        hitbox_width: int = 50,
        hitbox_height: int = 50,
        team: int = 0,
    ) -> None:

        self.name: str = name

        self.sprites: dict[str] = sprite_sheet
        self.sprite: pygame.Surface = sprite_sheet[GC.MOTION_NONE]
        self.sprite_rect: pygame.Rect = self.sprite.get_rect()
        self.width: int = self.sprite.get_width()
        self.height: int = self.sprite.get_height()
        self.random_target_point: tuple[int, int] = None
        self.x: float = x
        self.y: float = y
        self.x_speed: float = x_speed
        self.y_speed: float = y_speed
        self.hp = 100
        self.damage = 0
        self.motion: int = 0
        self.is_dead: bool = False
        self.dynamic_hitbox: bool = False
        self.draw_hitbox: bool = True
        self.draw_move_path: bool = True
        self.team = team
        self.team_color = GA.get_team_color(team)
        self.last_damage_time = 0
        self.damage_i_frames = 1 * 1000

        self.hitbox = pygame.Rect(x, y, hitbox_width, hitbox_height)

        self.update()

    @staticmethod
    def entity_is_dead(entity: 'Entity'):
        return entity.is_dead

    @staticmethod
    def entity_is_not_dead(entity: 'Entity'):
        return not entity.is_dead

    def set_team(self, team: int):

        self.team = team
        self.team_color = GA.get_team_color(team)

    def set_hitbox_dynamic(self, yes_no: bool):

        self.dynamic_hitbox = yes_no

    def get_x_motion(self):

        return self.motion & GC.X_MOTION_MASK

    def get_y_motion(self):

        return self.motion & GC.Y_MOTION_MASK

    def collides_with(self, entity: "Entity"):

        return not self.is_dead and self.hitbox.colliderect(entity.hitbox)

    def kill(self):
        self.is_dead = True

    def take_damage_no_i_frames(self, damage: int):
        """ returns a bool indicating if the entity is dead """

        self.hp -= damage

        if self.hp <= 0:
            self.kill()

        return self.is_dead 

    def take_damage_and_died(self, damage: int):
        """ returns a bool indicating if the entity is dead """
        
        if self.last_damage_time + self.damage_i_frames > pygame.time.get_ticks():
            return self.is_dead

        self.hp -= damage

        self.last_damage_time = pygame.time.get_ticks()

        if self.hp <= 0:
            self.kill()

        return self.is_dead 

    def perform_task(self):
        pass

    
    def get_entity_damage(self):
        return self.damage

    def update(self):

        self.sprite = self.sprites.get(self.motion, self.sprite)

        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()

        self.sprite_rect.width = self.width
        self.sprite_rect.height = self.height
        self.sprite_rect.centerx = self.x
        self.sprite_rect.centery = self.y

        if self.dynamic_hitbox:

            self.hitbox.width = self.width * 0.8
            self.hitbox.height = self.height * 0.8

        self.hitbox.y = self.y - self.hitbox.height // 2
        self.hitbox.x = self.x - self.hitbox.width // 2

    def render(self, GAME_WINDOW: pygame.Surface):

        if self.is_dead:
            return

        self.update()

        GAME_WINDOW.blit(self.sprite, self.sprite_rect)

        if self.last_damage_time + self.damage_i_frames > pygame.time.get_ticks():
            color = GameMath.invert_color(self.team_color)
                
        else:
            color = self.team_color

        if self.draw_hitbox:
            pygame.draw.rect(GAME_WINDOW, color, self.hitbox, 2, 1)

        if self.draw_move_path and self.random_target_point is not None:
            pygame.draw.line(
                GAME_WINDOW,
                color,
                (self.x, self.y),
                self.random_target_point,
                1,
            )

    def move_x(self, move_by: int):

        if move_by == 0:
            # keep only the y motion bits
            self.motion = self.motion & GC.Y_MOTION_MASK
            return

        self.x += move_by

        x_motion = 0

        if move_by < 0:
            x_motion |= GC.MOTION_HORIZONTAL_LEFT

        else:
            x_motion |= GC.MOTION_HORIZONTAL_RIGHT

        # update the x motion bits
        self.motion = (self.motion & GC.Y_MOTION_MASK) | x_motion

    def move_y(self, move_by: int):

        if move_by == 0:
            # keep only the x motion bits
            self.motion = self.motion & GC.X_MOTION_MASK
            return

        self.y += move_by

        y_motion = 0

        if move_by < 0:
            y_motion |= GC.MOTION_VERTICAL_UP

        else:
            y_motion |= GC.MOTION_VERTICAL_DOWN

        # update the y motion bits
        self.motion = (self.motion & GC.X_MOTION_MASK) | y_motion

    def move_direction_of_x(self, x:int):

        self.move_x(self.x_speed * x)

    def move_direction_of_y(self, y:int):

        self.move_y(self.y_speed * y)

    def move_towards(self, x: int, y: int):
        
        # # using vectors
        # x_dir, y_dir = GameMath.get_normalized_vector(self.x, self.y, x, y)

        # self.move_direction_of_x(x_dir)
        # self.move_direction_of_y(y_dir)
        
        x_change, y_change = GameMath.move_towards(
            x, y, self.x, self.y, self.x_speed, self.y_speed
        )

        self.move_x(x_change)
        self.move_y(y_change)

    def keep_in_bounds(self, x1, y1, x2, y2):

        if self.x < x1:
            self.move_x(self.x_speed)

        if self.x > x2:
            self.move_x(-self.x_speed)

        if self.y < y1:
            self.move_y(self.y_speed)

        if self.y > y2:
            self.move_y(-self.y_speed)

    def random_wander(self):

        if self.random_target_point is None:

            self.random_target_point = GameMath.get_random_point()

        x, y = self.random_target_point

        self.move_towards(x, y)

        if (
            np.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)
            < (self.x_speed + self.y_speed) / 2
        ):

            self.random_target_point = None


class WanderingEntity(Entity):
    def __init__(
        self,
        sprite_sheet: dict[int, pygame.Surface],
        name: str,
        x: int = 0,
        y: int = 0,
        x_speed: int = 10,
        y_speed: int = 10,
        hitbox_width: int = 50,
        hitbox_height: int = 50,
        team: int = 0,
    ) -> None:
        super().__init__(
            sprite_sheet,
            "wandering " + name,
            x,
            y,
            x_speed,
            y_speed,
            hitbox_width,
            hitbox_height,
            team,
        )

    def perform_task(self):

        self.random_wander()


class ShooterEntity(Entity):
    def __init__(
        self,
        sprite_sheet: dict[int, pygame.Surface],
        name: str,
        x: int = 0,
        y: int = 0,
        x_speed: int = 10,
        y_speed: int = 10,
        hitbox_width: int = 50,
        hitbox_height: int = 50,
        team: int = 0,
        shoot_delay_ms: int = 4000,
        bullet_speed: int = 10,
        bullet_life_ms: int = 6000,
        bullet_sprite: pygame.Surface = GA.Sprites.BULLET_1_SPRITE,
    ) -> None:

        if bullet_sprite is None:
            bullet_sprite = GA.Sprites.BULLET_1_SPRITE

        super().__init__(
            sprite_sheet,
            name,
            x,
            y,
            x_speed,
            y_speed,
            hitbox_width,
            hitbox_height,
            team,
        )

        self.bullet_life = bullet_life_ms
        self.render_bullet_path = False
        self.bullets: list[EntityBullet] = []
        self.bullet_speed = bullet_speed
        self.shoot_delay = shoot_delay_ms
        self.last_shoot_time = 0
        self.bullet_sprite = bullet_sprite
        self.bullet_clearout_interval = 30 * 1000
        self.last_clear_bullet_time = (
            pygame.time.get_ticks() + self.bullet_clearout_interval
        )

    def shoot_bullet(self, target_x, target_y):

        if (
            self.last_shoot_time + self.shoot_delay > pygame.time.get_ticks()
            or self.bullet_sprite is None
        ):
            return

        bullet = EntityBullet(
            self.bullet_sprite,
            self.name,
            self.x,
            self.y,
            bullet_speed=self.bullet_speed,
            team=self.team,
            shoot_at_x=target_x,
            shoot_at_y=target_y,
            bullet_life_ms=self.bullet_life,
        )

        bullet.draw_bullet_path = self.render_bullet_path

        self.bullets.append(bullet)

        self.last_shoot_time = pygame.time.get_ticks()

    def get_bullet_collided_with(self, entity: Entity) -> 'EntityBullet':

        for bullet in self.bullets:

            if bullet.collides_with(entity):
                return bullet 

        return None 

    def bullets_collid_with(self, entity: Entity):
        
        for bullet in self.bullets:

            if bullet.collides_with(entity):
                return True 

        return False 

    def render(self, GAME_WINDOW: pygame.Surface):

        super().render(GAME_WINDOW)

        for bullet in self.bullets:
            bullet.render(GAME_WINDOW)

    def perform_task(self):

        super().perform_task()

        for bullet in self.bullets:
            bullet.perform_task()

        if (
            self.last_clear_bullet_time + self.bullet_clearout_interval
            < pygame.time.get_ticks()
        ):

            self.last_clear_bullet_time = pygame.time.get_ticks()

            _ = len(self.bullets)
            self.bullets = [b for b in filter(lambda x: not x.is_dead, self.bullets)]

            print(f"Cleared out dead bullets: {_ - len(self.bullets)}")


class EntityBullet(Entity):
    def __init__(
        self,
        sprite_sheet: dict[int, pygame.Surface],
        name: str,
        x: int = 0,
        y: int = 0,
        bullet_speed: int = 10,
        hitbox_width: int = 50,
        hitbox_height: int = 50,
        team: int = 0,
        shoot_at_x: int = 0,
        shoot_at_y: int = 0,
        bullet_damage:int = 10,
        bullet_life_ms: int = 4000,
    ) -> None:

        self.damage = bullet_damage
        self.draw_bullet_path = False
        self.shoot_at_x = shoot_at_x
        self.shoot_at_y = shoot_at_y
        self.alive_at = pygame.time.get_ticks()
        self.life = bullet_life_ms
        self.dir_x, self.dir_y = GameMath.get_normalized_vector(x, y, shoot_at_x, shoot_at_y)

        super().__init__(
            {GC.MOTION_NONE: sprite_sheet},
            "bullet " + name,
            x,
            y,
            bullet_speed,
            bullet_speed,
            hitbox_width,
            hitbox_height,
            team,
        )


        if self.dynamic_hitbox:
            self.hitbox.width = self.width * 0.8
            self.hitbox.height = self.height * 0.8

    def update(self):

        self.sprite_rect.centerx = self.x
        self.sprite_rect.centery = self.y

        self.hitbox.y = self.y - self.hitbox.height // 2
        self.hitbox.x = self.x - self.hitbox.width // 2

        if self.alive_at + self.life < pygame.time.get_ticks():
            self.kill()

    def render(self, GAME_WINDOW: pygame.Surface):

        if self.is_dead:
            return

        super().render(GAME_WINDOW)

        if self.draw_bullet_path:
            pygame.draw.line(
                GAME_WINDOW,
                self.team_color,
                (self.x, self.y),
                (self.x + self.dir_x * self.x_speed, self.y + self.dir_y * self.y_speed)
            )
    

    def perform_task(self):

        if self.is_dead:
            return
        
        self.move_direction_of_x(self.dir_x)
        self.move_direction_of_y(self.dir_y)

        if GameMath.is_rect_off_screen(self.hitbox):
            self.kill()


class Player(ShooterEntity):
    def __init__(
        self,
        sprite_sheet: dict[int, pygame.Surface],
        x: int = 0,
        y: int = 0,
        x_speed: int = 10,
        y_speed: int = 10,
        hitbox_width: int = 50,
        hitbox_height: int = 50,
        team: int = 1,
    ) -> None:
        super().__init__(
            sprite_sheet,
            "player",
            x,
            y,
            x_speed,
            y_speed,
            hitbox_width,
            hitbox_height,
            team,
        )

    def handle_input(self, keys: Sequence[int]):

        x_motion = 0
        y_motion = 0

        if keys[pygame.K_a]:
            x_motion -= self.x_speed

        elif keys[pygame.K_d]:
            x_motion += self.x_speed

        if keys[pygame.K_w]:
            y_motion -= self.x_speed

        elif keys[pygame.K_s]:
            y_motion += self.x_speed

        if keys[pygame.K_SPACE]:

            self.shoot_bullet(*pygame.mouse.get_pos())

        self.move_x(x_motion)
        self.move_y(y_motion)
