import pygame 
import numpy as np 
import math 


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

class Game:

    WIDTH = 801
    HEIGHT = 801

    FRAME_RATE = 30

    GAME_WINDOW = None 

    CLOCK = None

    def __init__(self) -> None:
    
        pygame.init()

        # set up window, important this comes before Sprites.init()
        self.GAME_WINDOW = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.SCALED + pygame.RESIZABLE)
        self.GAME_WINDOW.fill((0, 0, 0))

        self.CLOCK = pygame.time.Clock()

        self.running = True 
        self.mouse_down = False
        self.old_time = 0
        self.time = self.CLOCK.get_time()/ 1000

        self.grid = Grid(25, 25, self.WIDTH, self.HEIGHT)
        # self.direction2 = Direction2D(self, 300, 300)
        self.direction3 = Direction3D(self, 300, 300)
        self.direction32 = Direction3D(self, 310, 300)


    def update(self):
        
        # self.direction2.update()
        self.direction3.update()
        self.direction32.update()


    def render(self):
        # self.grid.render(self.GAME_WINDOW)
        # self.direction2.render(self.GAME_WINDOW)
        self.direction3.render(self.GAME_WINDOW)
        self.direction32.render(self.GAME_WINDOW)


    def main_loop(self):

        while self.running:

            pygame.display.update()

            self.CLOCK.tick(self.FRAME_RATE)

            self.old_time = self.time 
            self.time = self.CLOCK.get_time() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_down = True
                    
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_down = False

            self.GAME_WINDOW.fill((0, 0, 0))

            self.update()
            self.render()




class Direction2D:

    def __init__(self, game:Game, x, y) -> None:
        self.game = game 

        self.unit = np.array([1.0, 0.0])
        self.xy  = np.array([x * 1.0, y * 1.0], dtype=float)
        self.magnitude = 50
        self.move_speed = 200.0
        self.rotation_speed = 3.0


    def update(self):
        
        keys = pygame.key.get_pressed()
        move_speed = self.game.time * self.move_speed
        rot_speed  = self.game.time * self.rotation_speed

        if keys[pygame.K_d]:

            # multiply our look vector by the 2d rotation matrix 
            # where the angle is how much we want to move by
            self.unit = self.unit @ np.array(
                [[math.cos(-rot_speed), -math.sin(-rot_speed)],
                 [math.sin(-rot_speed), math.cos(-rot_speed)]])

        elif keys[pygame.K_a]:
            
            # multiply our look vector by the 2d rotation matrix 
            # where the angle is how much we want to move by
            self.unit = self.unit @ np.array(
                [[math.cos(rot_speed), -math.sin(rot_speed)],
                 [math.sin(rot_speed), math.cos(rot_speed)]])

        if keys[pygame.K_w]:
            
            self.xy += self.unit * move_speed

        elif keys[pygame.K_s]:

            self.xy -= self.unit * move_speed
        

    def render(self, GAME_WINDOW):
        
        pygame.draw.line(GAME_WINDOW, 'red', self.xy, self.xy + (self.unit * self.magnitude))


class Direction3D:

    def __init__(self, game:Game, x, y) -> None:
        self.game = game 

        self.unit = np.array([1.0, 0.0, 0.0])
        self.xyz  = np.array([x, y, 0.0])
        self.magnitude = 50
        self.move_speed = 200.0
        self.rotation_speed = 3.0


    def update(self):
        keys = pygame.key.get_pressed()
        move_speed = self.game.time * self.move_speed
        rot_speed  = self.game.time * self.rotation_speed

        # z axis rotation
        if keys[pygame.K_d]:

            self.unit = self.unit @ np.array(
                [[math.cos(rot_speed), -math.sin(rot_speed), 0], 
                 [math.sin(rot_speed), math.cos(rot_speed), 0],
                 [0, 0, 1]])

        # z axis rotation
        elif keys[pygame.K_a]:
            
            self.unit = self.unit @ np.array(
                [[math.cos(-rot_speed), -math.sin(-rot_speed), 0], 
                 [math.sin(-rot_speed), math.cos(-rot_speed), 0],
                 [0, 0, 1]])

        # y axis rotation
        if keys[pygame.K_w]:
            
            self.unit = self.unit @ np.array(
                [[math.cos(rot_speed), 0, math.sin(rot_speed)], 
                 [0, 1, 0],
                 [-math.sin(rot_speed), 0, math.cos(rot_speed)]])

        # y axis rotation
        elif keys[pygame.K_s]:

            self.unit = self.unit @ np.array(
                [[math.cos(-rot_speed), 0, math.sin(-rot_speed)], 
                 [0, 1, 0],
                 [-math.sin(-rot_speed), 0, math.cos(-rot_speed)]])


        if keys[pygame.K_UP]:
            
            self.xyz += self.unit * move_speed

        elif keys[pygame.K_DOWN]:

            self.xyz -= self.unit * move_speed
        

    def render(self, GAME_WINDOW):
        
        # orthagonal projection onto the xy-plane 
        # drop the z axis from the direction
        xy_projection = self.unit[0:2]

        # now we need to handle the length to draw the vector to account for z direction
        # so we get the norm of our new xy vector, which should be < 1, since our full xyz vector has a norm of 1
        # and multiply that by our magnitude to get the visible length
        new_magnitude = np.linalg.norm(xy_projection) * self.magnitude

        # ignoring the z axis for position right now 
        xy = self.xyz[0:2]

        pygame.draw.line(GAME_WINDOW, 'red', xy, xy + (xy_projection * new_magnitude))


if __name__ == "__main__":

    Game().main_loop()