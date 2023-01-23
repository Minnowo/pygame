
import pygame
import numpy.random as random

import math
from dataclasses import dataclass, field
from . import GameConstants as GC


@dataclass(unsafe_hash=True)
class Particle:

    x: float
    y: float
    decay_rate: int
    color: tuple[int, int, int]
    is_dead: bool = field(default=False, init=False)

    def render(self, DRAW_SURFACE: pygame.Surface):
        pass

    def update(self):
        pass


@dataclass(unsafe_hash=True)
class FallingSquareParticle(Particle):

    fall_speed: float
    rotation_rad: float
    size: float
    rotate_right: bool = True

    def render(self, DRAW_SURFACE):

        if self.is_dead:
            return

        pygame.draw.polygon(DRAW_SURFACE, self.color, self.get_draw_points(), 2)

    def update(self):

        if self.size < 1:
            self.is_dead = True
            return

        rotate_right = 1 if self.rotate_right else -1

        self.y += self.fall_speed
        self.rotation_rad += self.fall_speed * self.decay_rate * rotate_right
        self.size -= self.decay_rate

    def get_draw_points(self):

        return (
            (self.x + math.cos(self.rotation_rad) * self.size, self.y + math.sin(self.rotation_rad) * self.size),
            (
                self.x + math.cos(self.rotation_rad + GC.DEGREE_90_RAD) * self.size,
                self.y + math.sin(self.rotation_rad + GC.DEGREE_90_RAD) * self.size,
            ),
            (
                self.x + math.cos(self.rotation_rad + GC.DEGREE_180_RAD) * self.size,
                self.y + math.sin(self.rotation_rad + GC.DEGREE_180_RAD) * self.size,
            ),
            (
                self.x + math.cos(self.rotation_rad + GC.DEGREE_270_RAD) * self.size,
                self.y + math.sin(self.rotation_rad + GC.DEGREE_270_RAD) * self.size,
            ),
        )


@dataclass(unsafe_hash=True)
class CircleParticle(Particle):

    radius: float
    line_width: int
    expand_rate: float
    expand_rate_change: float

    def render(self, DRAW_SURFACE):

        if self.is_dead:
            return

        pygame.draw.circle(DRAW_SURFACE, self.color, (self.x, self.y), self.radius, int(self.line_width))

    def update(self):

        if self.line_width < 1:
            self.is_dead = True
            return

        self.radius += self.expand_rate
        self.line_width -= self.decay_rate
        self.expand_rate -= self.expand_rate_change


class ParticleEffect:
    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def render(self, DRAW_SURFACE: pygame.Surface):

        self.particles = list(filter(lambda x: not x.is_dead, self.particles))

        for particle in self.particles:

            particle.update()
            particle.render(DRAW_SURFACE)

    def create_particle_on_chance(self, chance_percent: float):

        if random.random() < chance_percent:
            self.create_particle()

    def create_many_in_bounds(self, amount: int, x: int, y: int, width: int, height: int, **kwargs):
        for i in range(amount):
            sx = random.randint(x, x + width)
            sy = random.randint(y, y + height)
            self.create_particle(x=sx, y=sy, **kwargs)

    def create_particle(self, **kwargs):
        pass

    def add_particle(self, particle: Particle):
        self.particles.append(particle)


class FallingSquareEffect(ParticleEffect):
    def __init__(self, color=(255, 255, 255)) -> None:
        super().__init__()
        self.color = color

    def create_particle(
        self,
        x: float = None,
        y: float = None,
        rotation: float = None,
        fall_speed: float = None,
        size: float = None,
        decay_rate: float = None,
        color: tuple[int, int, int] = None,
        rotate_right: bool = None,
    ):

        if x is None:
            x = random.randint(0, GC.WIDTH)

        if y is None:
            y = -80

        if rotation is None:
            rotation = math.radians(random.randint(0, 359))

        if fall_speed is None:
            fall_speed = random.randint(10, 30) / 20

        if size is None:
            size = random.randint(15, 40)

        if decay_rate is None:
            decay_rate = random.randint(10, 30) / 500

        if color is None:
            color = self.color

        if rotate_right is None:
            rotate_right = random.randint(1, 6) != 2

        particle = FallingSquareParticle(
            x=x,
            y=y,
            rotation_rad=rotation,
            fall_speed=fall_speed,
            size=size,
            decay_rate=decay_rate,
            color=color,
            rotate_right=rotate_right,
        )

        self.particles.append(particle)


class ExpandingCircle(ParticleEffect):
    def __init__(self, color=(255, 255, 255)) -> None:
        super().__init__()
        self.color = color

    def create_particle(
        self,
        x: float = None,
        y: float = None,
        radius: float = None,
        expand_rate: float = None,
        line_width: int = None,
        expand_rate_change: float = None,
        decay_rate: float = None,
        color: tuple[int, int, int] = None,
    ):

        if x is None:
            x = random.randint(0, GC.WIDTH)

        if y is None:
            y = random.randint(0, GC.HEIGHT)

        if radius is None:
            radius = random.randint(1, 10)

        if expand_rate is None:
            expand_rate = random.randint(10, 30)

        if line_width is None:
            line_width = random.randint(5, 10)

        if decay_rate is None:
            decay_rate = random.randint(10, 30) / 15

        if expand_rate_change is None:
            expand_rate_change = random.randint(10, 30) / 20

        if color is None:
            color = self.color

        particle = CircleParticle(
            x=x,
            y=y,
            decay_rate=decay_rate,
            radius=radius,
            line_width=line_width,
            expand_rate=expand_rate,
            expand_rate_change=expand_rate_change,
            color=color,
        )

        self.particles.append(particle)
