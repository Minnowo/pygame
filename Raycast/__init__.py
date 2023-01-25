import numpy as np
import numpy.typing as npt

import pygame
import os

from . import RayMath as rMath
import math


"""
This is basically a python version of:
 - https://lodev.org/cgtutor/raycasting.html


"""



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


class Grid:
    def __init__(self, cell_x, cell_y, w, h) -> None:

        self.cell_x = cell_x
        self.cell_y = cell_y

        self.lines = np.zeros((int(np.ceil(w / self.cell_x) + np.ceil(h / self.cell_y)), 2, 2))

        k = 0
        for i in range(0, w, self.cell_x):

            self.lines[k] = ((i, 0), (i, h))
            k += 1

        for i in range(0, h, self.cell_y):

            self.lines[k] = ((0, i), (w, i))
            k += 1

    def render(self, DRAW_SURFACE: pygame.Surface):

        for line in self.lines:

            pygame.draw.line(DRAW_SURFACE, (255, 255, 255), *line)


class Player:
    def __init__(self) -> None:

        self.pos = np.array([0, 0])
        self.hitbox = pygame.Rect(0, 0, 10, 10)
        self.x_speed = 10
        self.y_speed = 10
        self.look = (0, 0)

    @property
    def x(self):
        return self.pos[0]

    @x.setter
    def x(self, value):
        self.pos[0] = value
        self.hitbox.x = value - self.hitbox.width//2

    @property
    def y(self):
        return self.pos[1]

    @y.setter
    def y(self, value):
        self.pos[1] = value 
        self.hitbox.y = value - self.hitbox.height//2

    def render(self, DRAW_SURFACE: pygame.Surface):

        pygame.draw.rect(DRAW_SURFACE, (255, 0, 0), self.hitbox)

        m = 100

        look_point = (self.x + self.look[0] * m, self.y + self.look[1] * m)
        pygame.draw.line(DRAW_SURFACE, (0, 255, 0), (self.x, self.y), look_point)

        plane_r1 = (look_point[0] + self.look_plane[0]*m, look_point[1] + self.look_plane[1]*m)
        plane_r2 = (look_point[0] - self.look_plane[0]*m, look_point[1] - self.look_plane[1]*m)
        pygame.draw.line(DRAW_SURFACE, (0, 255, 0), plane_r1, plane_r2)

        look_ray_1 = (self.x + m * self.fov_left_inner[0],
                      self.y + m * self.fov_left_inner[1])
        pygame.draw.line(DRAW_SURFACE, (0, 255, 0), (self.x, self.y), look_ray_1)

        look_ray_1 = (self.x + m * self.fov_right_inner[0],
                      self.y + m * self.fov_right_inner[1])
        pygame.draw.line(DRAW_SURFACE, (0, 255, 0), (self.x, self.y), look_ray_1)

        look_ray_1 = (self.x + m * self.fov_left_outer[0],
                      self.y + m * self.fov_left_outer[1])
        pygame.draw.line(DRAW_SURFACE, (0, 255, 0), (self.x, self.y), look_ray_1)

        look_ray_1 = (self.x + m * self.fov_right_outer[0],
                      self.y + m * self.fov_right_outer[1])
        pygame.draw.line(DRAW_SURFACE, (0, 255, 0), (self.x, self.y), look_ray_1)

    def update(self):

        # the direction of the camera 
        self.look = rMath.get_normalized_vector(self.x, self.y, *pygame.mouse.get_pos())

        # the direction perpendicular to the camera 
        self.look_plane = (self.look[1], -self.look[0])

        # left fov
        self.fov_left_outer = (self.look[0] + self.look_plane[0], self.look[1] + self.look_plane[1])
        self.fov_left_inner  = (self.look[0] + self.look_plane[0] * 1/3, self.look[1] + self.look_plane[1] * 1/3)
        
        # left fov
        self.fov_right_outer = (self.look[0] - self.look_plane[0], self.look[1] - self.look_plane[1])
        self.fov_right_inner = (self.look[0] - self.look_plane[0] * 1/3, self.look[1] - self.look_plane[1] * 1/3)

    def take_input(self, keys):

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

        self.x += x_motion
        self.y += y_motion





class Raycaster():

    def __init__(self) -> None:
        

        self.room = np.array([
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,2,2,2,2,2,0,0,0,0,3,0,3,0,3,0,0,0,1],
            [1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,3,0,0,0,3,0,0,0,1],
            [1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,2,2,0,2,2,0,0,0,0,3,0,3,0,3,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,4,4,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,4,0,4,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,4,0,0,0,0,5,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,4,0,4,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,4,0,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,4,4,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
            ])

        self.colors = [
            (25, 25, 25),
            (255, 0, 0),
            (0, 255, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0)
        ]

        self.width = self.room.shape[0]
        self.height = self.room.shape[1]

        # starting position
        self.pos_x = 22
        self.pos_y = 12

        # initial look direction
        self.dir_x = -1
        self.dir_y = 0

        # 2d raycaster version of camera plane
        self.plane_x = 0
        self.plane_y = 0.66

        self.last_mouse_x = -1

    
    def render(self, DRAW_SURFACE: pygame.Surface):

        w, h = DRAW_SURFACE.get_size()

        for x in range(w):

            camera_x = 2 * x / w - 1 # x coordinate in camera space 

            ray_dir_x = self.dir_x + self.plane_x * camera_x
            ray_dir_y = self.dir_y + self.plane_y * camera_x


            if ray_dir_x == 0:
                delta_dist_x = 1e30
            else:
                delta_dist_x = abs(1 / ray_dir_x)

            if ray_dir_y == 0:
                delta_dist_y = 1e30
            else:
                delta_dist_y = abs(1 / ray_dir_y)

            map_x = int(self.pos_x)
            map_y = int(self.pos_y)


            if ray_dir_x < 0:
                step_x = -1
                side_dist_x = (self.pos_x - map_x) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (map_x + 1.0 - self.pos_x) * delta_dist_x

            if ray_dir_y < 0:
                step_y = -1
                side_dist_y = (self.pos_y - map_y) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (map_y + 1.0 - self.pos_y) * delta_dist_y

            hit = 0 # was there a wall hit

            # perform DDA
            while hit == 0:
                
                # jump to the next square in either x or y direction
                if side_dist_x < side_dist_y:

                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0

                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side = 1

                if self.room[map_x][map_y] > 0:
                    hit = 1
            

            # prevent the fish eye effect by not using the euclidean distance 
            if side == 0:
                perp_wall_dist = (side_dist_x - delta_dist_x)
            else:
                perp_wall_dist = (side_dist_y - delta_dist_y)


            if perp_wall_dist == 0:
                line_height = h 
            else:
                line_height = h // perp_wall_dist

            draw_start = -line_height / 2 + h / 2

            if draw_start < 0:
                draw_start = 0

            draw_end = line_height / 2 + h / 2

            if draw_end > h:
                draw_end = h - 1


            map_value = self.room[map_x][map_y]

            color = self.colors[map_value]

            if side == 1:
                color = (color[0] / 2, color[1] / 2, color[2] / 2)

            pygame.draw.line(DRAW_SURFACE, color, (x, draw_start), (x, draw_end))


        map_size = 10
        at_x, at_y = w - map_size*self.width, 0
        for x in range(self.width):
            for y in  range(self.height):

                map_value = self.room[x][y]

                color = self.colors[map_value]

                if x == int(self.pos_x) and y == int(self.pos_y):
                    color = (255, 255, 255)

                pygame.draw.rect(DRAW_SURFACE, color, pygame.Rect(at_x + x*map_size, at_y + y*map_size, map_size, map_size))




    def input(self, keys, is_mouse_down, frame_time, screen_width, screen_height):

        move_speed = frame_time * 5.0
        rot_speed  = frame_time * 3.0

        mouse_x, mouse_y = pygame.mouse.get_pos()
        look_change = 0

        if is_mouse_down:

            if mouse_x > screen_width // 2:
                look_change = -1
            elif mouse_x < screen_width // 2:
                look_change = 1

            pygame.mouse.set_pos(screen_width//2, screen_height//2)

        else:
            self.last_mouse_x = -1


        if keys[pygame.K_d] or look_change < 0:
            old_dir_x = self.dir_x
            self.dir_x = self.dir_x * math.cos(-rot_speed) - self.dir_y * math.sin(-rot_speed)
            self.dir_y = old_dir_x * math.sin(-rot_speed) + self.dir_y * math.cos(-rot_speed)

            old_plane_x = self.plane_x
            self.plane_x = self.plane_x * math.cos(-rot_speed) - self.plane_y * math.sin(-rot_speed)
            self.plane_y = old_plane_x * math.sin(-rot_speed) + self.plane_y * math.cos(-rot_speed)

        elif keys[pygame.K_a] or look_change > 0:
            old_dir_x = self.dir_x
            self.dir_x = self.dir_x * math.cos(rot_speed) - self.dir_y * math.sin(rot_speed)
            self.dir_y = old_dir_x * math.sin(rot_speed) + self.dir_y * math.cos(rot_speed)

            old_plane_x = self.plane_x
            self.plane_x = self.plane_x * math.cos(rot_speed) - self.plane_y * math.sin(rot_speed)
            self.plane_y = old_plane_x * math.sin(rot_speed) + self.plane_y * math.cos(rot_speed) 


        if keys[pygame.K_w]:
            
            if self.room[int(self.pos_x + self.dir_x * move_speed)][int(self.pos_y)] == 0:
                self.pos_x += self.dir_x * move_speed

            if self.room[int(self.pos_x)][int(self.pos_y + self.dir_y * move_speed)] == 0:
                self.pos_y += self.dir_y * move_speed

        elif keys[pygame.K_s]:
            if self.room[int(self.pos_x - self.dir_x * move_speed)][int(self.pos_y)] == 0:
                self.pos_x -= self.dir_x * move_speed

            if self.room[int(self.pos_x)][int(self.pos_y - self.dir_y * move_speed)] == 0:
                self.pos_y -= self.dir_y * move_speed


        if keys[pygame.K_SPACE]:
            print(self.room)
            print(int(self.pos_x), int(self.pos_y))

            





def render_top_down_view(DRAW_SURFACE: pygame.Surface, grid: Grid, player: Player):

    grid.render(DRAW_SURFACE)
    player.update()
    player.render(DRAW_SURFACE)




class Fonts:

    FONT_CONSOLAS: pygame.font.Font = None

    @staticmethod
    def init():
        try:
            Fonts.FONT_CONSOLAS = pygame.font.Font("./assets/fonts/consolas.ttf", 32)
        except Exception as e:
            print(f"Error loading font: {e}")

    @staticmethod
    def render_text(DRAW_SURFACE: pygame.Surface, text, x=0, y=0):
        
        if Fonts.FONT_CONSOLAS is None:
            return 

        text = Fonts.FONT_CONSOLAS.render(text, True, (255, 255, 255))

        DRAW_SURFACE.blit(text, text.get_rect(x=x, y=y))


def main():
    set_dpi_aware()

    # init pygame and load our assets
    pygame.init()
    Fonts.init()

    WIDTH = 801
    HEIGHT = 801

    # set up window, important this comes before Sprites.init()
    GAME_WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED + pygame.RESIZABLE)
    GAME_WINDOW.fill((0, 0, 0))

    FRAME_RATE = 60

    mouse_down = False

    grid = Grid(80, 80, WIDTH, HEIGHT)
    player = Player()
    raycaster = Raycaster()


    clock = pygame.time.Clock()

    time = 0
    old_time = 0

    play_game = True
    while play_game:

        pygame.display.update()
        clock.tick(FRAME_RATE)

        old_time = time 
        time = pygame.time.get_ticks()
        frame_time = (time - old_time) / 1000

        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        for event in events:
            if event.type == pygame.QUIT:
                play_game = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
                
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False

        GAME_WINDOW.fill((0, 0, 0))
        # render_top_down_view(GAME_WINDOW, grid, player)
        
        
        # player.take_input(keys)
        raycaster.render(GAME_WINDOW)
        raycaster.input(keys, mouse_down, frame_time, WIDTH, HEIGHT)

        Fonts.render_text(GAME_WINDOW, f"FPS: {clock.get_fps():.0f}")



