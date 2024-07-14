import pygame
import random
import math

pygame.init()


WIDTH, HEIGHT = 800, 600
MAX_SPEED = 2
MAX_ACCELERATION = 0.03
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
pygame.display.set_caption("Boids")


class Boid:
    def __init__(self):
        self.get_color()
        self.get_initial_velocity()
        self.get_initial_points()
        self.get_initial_center()
        self.acceleration = pygame.Vector2(0, 0)

    def get_initial_points(self):
        base_length = 10
        height = 12
        x = random.randint(10, WIDTH - 10)
        y = random.randint(10, HEIGHT - 10)
        point1 = (x, y)
        point2 = (x + base_length // 2, y - height)
        point3 = (x + base_length, y)
        self.points = (point1,point2,point3)

    def get_initial_velocity(self):
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))

    def get_initial_center(self):
        points = self.points
        self.center = pygame.Vector2(self.circumcenter(points[0][0], points[0][1], points[1][0], points[1][1], points[2][0], points[2][1]))

    def get_color(self):
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def update(self, boids):
        self.update_angle()
        self.update_position()

        self.update_acceeration(self.cohesion(boids))
        self.update_acceeration(self.separation(boids))
        self.update_acceeration(self.alignment(boids))

        points = self.points

        self.update_velocity()
        self.center = pygame.Vector2(self.circumcenter(points[0][0], points[0][1], points[1][0], points[1][1], points[2][0], points[2][1]))

    def update_position(self):
        points = self.points
        velocity = self.velocity
        self.points = ((points[0][0] + velocity[0], points[0][1] + velocity[1]), (points[1][0] + velocity[0], points[1][1] + velocity[1]), (points[2][0] + velocity[0],points[2][1] + velocity[1]))

    def update_angle(self):
        points = self.points
        center = self.center
        if str(self.get_angle((self.velocity[0], self.velocity[1])))[:7] != str(self.get_angle((points[1][0] - center[0], points[1][1] - center[1])))[:7]:
            self.points = self.rotate_boid(points, self.get_angle(self.velocity), center)

    def update_acceeration(self, influence):
        self.acceleration += influence

    def update_velocity(self):
        self.velocity = self.velocity + self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity.scale_to_length(MAX_SPEED)

    def get_angle(self, vector):
        angle = math.degrees(math.atan2(vector[0], vector[1]))
        if angle > 0 and angle > 90:
            angle = 90 - (angle - 90)
        elif angle > 0 and angle <= 90:
            angle = 90 + (90 - angle)
        elif angle < 0 and angle < -90:
            x = angle + 90
            angle = -90 - x
        else:
            x = 90 + angle
            angle = -90 - x
        angle = angle*(math.pi / 180)
        return angle

    def rotate_point(self, point, angle):
        ox, oy = self.center
        px, py = point

        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return qx, qy

    def rotate_boid(self, boid, angle, pivot):
        return [self.rotate_point(point, angle) for point in boid]

    def circumcenter(self, x1, y1, x2, y2, x3, y3):
        D = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))

        if D == 0:
            return None

        center_x = ((x1 ** 2 + y1 ** 2) * (y2 - y3) + (x2 ** 2 + y2 ** 2) * (y3 - y1) + (x3 ** 2 + y3 ** 2) * (y1 - y2)) / D
        center_y = ((x1 ** 2 + y1 ** 2) * (x3 - x2) + (x2 ** 2 + y2 ** 2) * (x1 - x3) + (x3 ** 2 + y3 ** 2) * (x2 - x1)) / D

        return (center_x, center_y)

    def distance(self, vector1, vector2):
         return math.dist(vector1, vector2)

    def get_center(self):
        return self.center

    def alignment(self, boids):
        perception = 100
        influence_vector = pygame.Vector2(0, 0)
        counter = 0

        for different_boid in boids:
            if different_boid != self and self.distance(self.center, different_boid.center) <= perception:
                influence_vector += different_boid.velocity
                counter += 1

        if counter != 0:
            influence_vector /= counter

            influence_vector -= self.velocity


        return influence_vector

    def separation(self, boids):
        perception = 40
        influence_vector = pygame.Vector2(0, 0)
        counter = 0

        for different_boid in boids:
            distance = self.distance(self.center, different_boid.center)
            if different_boid != self and distance < perception:
                diff = self.center - different_boid.center
                diff /= distance
                influence_vector += diff
                counter += 1

        if counter > 0:
            influence_vector /= counter


        return influence_vector

    def cohesion(self, boids):
        perception_radius = 100
        influence_vector = pygame.Vector2(0, 0)
        counter = 0
        center_of_mass = pygame.Vector2(0, 0)

        for different_boid in boids:
            if different_boid != self and self.distance(self.center, different_boid.center) < perception_radius:
                center_of_mass += different_boid.center
                counter += 1

        if counter > 0:
            center_of_mass /= counter
            desired = center_of_mass - self.center

            influence_vector = desired - self.velocity


        return influence_vector

    def show(self, screen):
        pygame.draw.polygon(screen, self.color, self.points)



running = True

boids = [Boid() for _ in range(50)]
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    for boid in boids:
        boid.update(boids)
        boid.show(screen)

    pygame.display.flip()
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()