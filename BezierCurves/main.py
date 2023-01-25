
import numpy as np
import numpy.typing as npt 

import pygame
import os 



class LinearBezierCurve:
    """
    Implements a linear bezier curve

    https://en.wikipedia.org/wiki/B%C3%A9zier_curve

    """

    @staticmethod
    def interpolate_points(t: float, p0: npt.NDArray, p1: npt.NDArray):

        return (1 - t) * p0 + t * p1

    @staticmethod
    def curve(t_points: npt.NDArray, points: npt.NDArray):

        curve = np.zeros((len(t_points), 2))

        for i, t in enumerate(t_points):

            new_points = points
            while len(new_points) > 1:

                new_points = tuple(
                    LinearBezierCurve.interpolate_points(t, new_points[k], new_points[k + 1])
                    for k in range(len(new_points) - 1)
                )

            curve[i] = new_points[0]

        return curve




class BezierCurve:
    def __init__(self, control_point_size = 15, starting_point=(0, 0), point_count = 4, t_point_step=0.01) -> None:

        self.control_point_size = control_point_size
        self.t_values = np.arange(0, 1, t_point_step)
        self.points = np.zeros((point_count, 2))
        self.rects = [pygame.Rect(0, 0, self.control_point_size, self.control_point_size) for i in range(point_count)]

        for i in range(0, point_count):

            if i % 2 == 0:
                self.update_point(i, (starting_point[0] + control_point_size * (i + 1), starting_point[1]))
            else:
                self.update_point(i, (starting_point[0] + control_point_size * (i + 1), starting_point[1] + control_point_size * 4))

        self.curve = LinearBezierCurve.curve(self.t_values, self.points)

        self.dragging = 0


    def get_rect(self, point, w, h):

        return pygame.Rect(point[0] - w // 2, point[1] - h // 2, w, h)

    def update_point(self, point_index, new_value):

        self.points[point_index] = new_value
        self.rects[point_index].update(
                self.points[point_index][0] - self.control_point_size // 2,
                self.points[point_index][1] - self.control_point_size // 2,
                self.control_point_size,
                self.control_point_size,
            )

    def calculate_curve(self):

        self.curve = LinearBezierCurve.curve(self.t_values, self.points)

    def render(self, DRAW_SURFACE: pygame.Surface):

        for rect in self.rects:
            pygame.draw.rect(DRAW_SURFACE, (255, 0, 0), rect)

        pygame.draw.lines(DRAW_SURFACE, (0, 255, 0), False, self.points)

        pygame.draw.lines(DRAW_SURFACE, (255, 255, 255), False, self.curve)


    def stop_drag(self):
        self.dragging = 0

    def start_drag(self, click_point: tuple[int, int], update_curve = True):

        if not self.dragging:

            for i, rect in enumerate(self.rects):

                if rect.collidepoint(pygame.mouse.get_pos()):

                    self.dragging = i + 1

        else:

            self.update_point(self.dragging - 1, click_point)

            if update_curve:
                self.calculate_curve()



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



def main():
    set_dpi_aware()

    # init pygame and load our assets
    pygame.init()

    WIDTH = 1324
    HEIGHT = 1000

    # set up window, important this comes before Sprites.init()
    GAME_WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED + pygame.RESIZABLE)
    GAME_WINDOW.fill((0, 0, 0))

    FRAME_RATE = 60
    game_time = 0

    mouse_down = False

    curve = BezierCurve(20, (50, 50))

    clock = pygame.time.Clock()

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

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False


        GAME_WINDOW.fill((0, 0, 0))
        curve.render(GAME_WINDOW)

        if mouse_down:

            curve.start_drag(pygame.mouse.get_pos())

        else:
            curve.stop_drag()



if __name__ == "__main__":
    main()