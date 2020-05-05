import pygame

import sys
from math import sqrt, pi

# this module is used to graph the distance and velocity of each circle
# it was remove because it caused problems with compiling
##from graphs import show_plot

# global constants
UPDATETIME = 27


def transfer_energy(c1, c2):
    # change the velocity between two circles when hit

    # calculate x velocities
    vx1 = ((c1.x_vel * (c1.mass - c2.mass)) + (2 * c2.mass * c2.x_vel)) / (c1.mass + c2.mass)
    vx2 = ((c2.x_vel * (c2.mass - c1.mass)) + (2 * c1.mass * c1.x_vel)) / (c1.mass + c2.mass)

    # calculate y velocities
    vy1 = ((c1.y_vel * (c1.mass - c2.mass)) + (2 * c2.mass * c2.y_vel)) / (c1.mass + c2.mass)
    vy2 = ((c2.y_vel * (c2.mass - c1.mass)) + (2 * c1.mass * c1.y_vel)) / (c1.mass + c2.mass)

    # assign everything accordingly
    c1.x_vel = vx1
    c1.y_vel = vy1

    c2.x_vel = vx2
    c2.y_vel = vy2


def check_event(event, circles):
    """ check a single queued event"""
    if event.type == pygame.QUIT:
        pygame.quit()
        # show_plot(circles)  # unused in the final version
        sys.exit()
    if event.type == pygame.MOUSEBUTTONDOWN:
        circles.are_grabbed(event)
    if event.type == pygame.MOUSEBUTTONUP:
        circles.are_released(event)
    if event.type == UPDATETIME:
        circles.update()


def circles_overlap(c1, c2):
    # test if the two circles collide with each other
    return get_dis(c1.x, c1.y, c2.x, c2.y) <= (c1.radius + c2.radius)


def get_collide_circles(group):
    # get all circles in a group that collide with one another
    for index, c1 in enumerate(group):
        # a bit sloppy, checks to make sure we aren't testing the same circle
        for c2 in group[index + 1:]:
            if circles_overlap(c1, c2):
                yield c1, c2


def get_dis(x1, y1, x2, y2):
    # get the distance between two points
    disx = (x2 - x1) ** 2
    disy = (y2 - y1) ** 2
    return sqrt(disx + disy)


class Circles(pygame.sprite.Group):
    """ A sprite group to hold elastic balls """
    def __init__(self, screen, *sprites):
        super().__init__(*sprites)
        self.screen = screen
        self.t = [0.0]

    def are_grabbed(self, event):
        # is the mouse grabbing a circle?
        if event.button == 1:
            for circle in self:
                if circle.point_collide(event.pos):
                    circle.grabbed()

    def are_released(self, event):
        # did the mouse release a circle?
        if event.button == 1:
            for circle in self:
                if circle.held:
                    circle.release(event.pos)

    def update(self, *args):
        for circle in self:
            circle.update(*args)

        for collisions in get_collide_circles(self.sprites()):
            transfer_energy(*collisions)

        self.t.append(self.t[-1] + (33/1000))

    def draw(self, surf):
        for circle in self:
            circle.draw()


class ElasticBall(pygame.sprite.Sprite):
    """ An elastic ball that can be bounced and thrown around """
    gravity = 0.5  # constant for all balls

    def __init__(self, screen, x, y, radius, color, *groups):
        super().__init__(*groups)

        self.screen = screen
        self.screct = self.screen.get_rect()
        self.color = color

        self.x = float(x)
        self.y = float(y)
        self.radius = radius

        self._x_vel = 0
        self._y_vel = 0

        self._held = False  # is the circle being held by the mouse?

        self.og_point = self.pos

        self.displacement = [0.0]
        self.speed = [0.0]

        self._mass = pi * (self.radius ** 2)

        self._air_re = 0.99

    @property
    def x_vel(self):
        return self._x_vel

    @x_vel.setter
    def x_vel(self, value):
        self._x_vel = int(value * 100) / 100

    @property
    def y_vel(self):
        return self._y_vel

    @y_vel.setter
    def y_vel(self, value):
        self._y_vel = int(value * 100) / 100

    @property
    def velocity(self):
        return sqrt((self.x_vel ** 2) + (self.y_vel ** 2))

    @property
    def held(self):
        return self._held

    @property
    def mass(self):
        return self._mass

    @property
    def pos(self):
        return int(self.x), int(self.y)

    @pos.setter
    def pos(self, cord):
        if len(cord) == 2:
            self.x, self.y = cord
        else:
            raise NameError("Only two numbers can be passed to coordinates(x, y) can be passed.")

    # gets the right, left, top, and bottom of a the circle
    # similar to the virtualized attributes in pygame's rect class, but for circles(and better because @property)
    @property
    def left(self):
        return self.x - self.radius

    @left.setter
    def left(self, value):
        self.x = value + self.radius

    @property
    def right(self):
        return self.x + self.radius

    @right.setter
    def right(self, value):
        self.x = value - self.radius

    @property
    def top(self):
        return self.y - self.radius

    @top.setter
    def top(self, value):
        self.y = self.radius + value

    @property
    def bottom(self):
        return self.y + self.radius

    @bottom.setter
    def bottom(self, value):
        self.y = value - self.radius

    def grabbed(self):
        # the circle is grabbed by the mouse
        self._held = True
        self.x_vel, self.y_vel = 0, 0
        self.og_point = self.pos

    def release(self, point):
        # the circle is released by the mouse
        self._held = False
        self.change_vel(point)

    def point_collide(self, point):
        # check if a point collides with the circle
        return get_dis(self.x, self.y, *point) <= self.radius

    def calc_gravity(self):
        # move the ball downwards according to gravity
        if not self._held:
            self.y_vel += self.gravity

    def calc_air_resist(self):
        # to keep things simple, air resistance is constant
        if not self._held:
            self.x_vel *= self._air_re
            self.y_vel *= self._air_re

    def get_vel(self, pos):
        return (self.og_point[0] - pos[0]) // 12, (self.og_point[1] - pos[1]) // 6

    def change_vel(self, point):
        # change the velocity of the circle based off the mouse's relative movement
        self.x_vel, self.y_vel = self.get_vel(point)

    def move_hori(self):
        # move the sphere horizontally
        self.x += self.x_vel

        # make sure the sphere is within screen boundaries
        if self.left < self.screct.left:
            self.left = self.screct.left
            self.x_vel *= -1
        if self.right > self.screct.right:
            self.right = self.screct.right
            self.x_vel *= -1

    def move_vert(self):
        # move the sphere vertically
        self.y += self.y_vel

        # make sure the sphere is within screen boundaries
        if self.top < self.screct.top:
            self.top = self.screct.top
            self.y_vel *= -1
        if self.bottom > self.screct.bottom:
            self.bottom = self.screct.bottom
            self.y_vel *= -1

    def update(self):
        # update the circle
        # test if the sphere is being grabbed or not
        dis = self.x, self.y

        if self.held:
            self.x, self.y = pygame.mouse.get_pos()

        # drop the sphere according to gravity
        self.calc_gravity()

        # slow the sphere down base on air resistance
        self.calc_air_resist()

        # change the sphere's position
        self.move_hori()
        self.move_vert()

        # old values for graphing. Because they take up space, they are removed
        # self.speed.append(self.velocity)
        # self.displacement.append(get_dis(*dis, self.x, self.y) + self.displacement[-1])

    def draw(self):
        # draw the circle on the screen
        pygame.draw.circle(self.screen, self.color, self.pos, self.radius)

        if self.held:
            pygame.draw.line(self.screen, [255, 0, 0], self.pos, self.og_point)

    def __str__(self):
        return "Circle of radius {} at ({}, {})".format(self.radius, self.x, self.y)


def main():
    # Initialize pygame
    pygame.init()

    # Title the window
    pygame.display.set_caption("Physics Simulator")

    # creates the game's main display
    screen = pygame.display.set_mode([800, 600])

    # the group holding all of the circles
    circles = Circles(screen)

    # all of the circles in the simulation
    ElasticBall(screen, 400, 300, 50, (255, 255, 0), circles)
    ElasticBall(screen, 400, 100, 25, (64, 255, 0), circles)
    ElasticBall(screen, 100, 300, 20, (0, 127, 255), circles)
    ElasticBall(screen, 600, 300, 25, (127, 0, 255), circles)

    # create a timer for when an update should occur
    pygame.time.set_timer(UPDATETIME, 33)

    # begin the main game loop
    while True:
        # check all events(mouse buttons/movement, exit events, key strokes, ect)
        for event in pygame.event.get():
            check_event(event, circles)

        # ALL DRAWING DONE BELOW THIS COMMENT
        screen.fill((0, 0, 0))
        circles.draw(screen)

        # ALL DRAWING DONE ABOVE THIS COMMENT

        # update the screen
        pygame.display.flip()


if __name__ == "__main__":
    main()
