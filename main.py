# Importing Dependencies
import pygame
import sys
import os
import random
import numpy as np

# Initialize PyGame Module
pygame.init()
# Initialize PyGame's Font Module
pygame.font.init()
# Create Pygame Clock object to control FPS
clock = pygame.time.Clock()
# Set window's width and Height
WIN_WIDTH = 1200
WIN_HEIGHT = 300
# Set score and generation
score = 0
# Create a font for score and generation variables
stat_font = pygame.font.SysFont('timesnewroman', 20)
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
# Set window's name
pygame.display.set_caption('Dinosaur Game')
# Load dinosaur game's images
DINOSAUR_IMGS = [pygame.image.load(os.path.join('imgs', 'dinosaur1.png')).convert(), pygame.image.load(os.path.join('imgs', 'dinosaur2.png')).convert(), pygame.image.load(os.path.join('imgs', 'dinosaur3.png')).convert()]
BIRD_IMGS = [pygame.image.load(os.path.join('imgs', 'bird1.png')).convert(), pygame.image.load(os.path.join('imgs', 'bird2.png')).convert()]
LARGE_CACTI_IMGS = [pygame.image.load(os.path.join('imgs', 'largecactus.png')).convert(), pygame.image.load(os.path.join('imgs', '2largecacti.png')).convert(), pygame.image.load(os.path.join('imgs', '4largecacti.png')).convert()]
SMALL_CACTI_IMGS = [pygame.image.load(os.path.join('imgs', 'smallcactus.png')).convert(), pygame.image.load(os.path.join('imgs', '2smallcacti.png')).convert(), pygame.image.load(os.path.join('imgs', '3smallcacti.png')).convert()]
BASE_IMG = pygame.image.load(os.path.join('imgs', 'base.png'))
CLOUD_IMG = pygame.image.load(os.path.join('imgs', 'cloud.png'))


# Dinosaur Class
class Dinosaur:
    global score
    IMGS = DINOSAUR_IMGS
    # How long each image of dinosaur is displayed for
    ANIMATION_TIME = 20

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 0

        self.tick_count = 0
        self.img_count = 0
        self.img = self.IMGS[0]

    # Function to jump, can only jump if the dinosaur is touching the ground
    # -.2 pixel per second in the -y direction (up)
    def jump(self, base):
        if self.collide(base):
            self.vel = -.2
            self.tick_count = 0
        else:
            pass

    # Dinosaur moving physics
    def move(self):
        self.tick_count += 1
        # Displacement = v(i)*t + .5*a*t^2
        d = self.vel*self.tick_count + .5*.01*self.tick_count**2
        # Set terminal velocity
        if d >= 10:
            d = 10
        # A little boost to jumping to make animation look better
        if d < 0:
            d -= 2

        self.y += d
        # Set the floor as y = 260
        if self.y >= 260 - self.img.get_height():
            self.y = 260 - self.img.get_height()

    # Animate dinosaur
    def draw(self, win, base):
        self.img_count += 1
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 2 + 1:
            self.img = self.IMGS[1]
            self.img_count = 0
        # If dinosaur is not on the ground then display the first dinosaur's image
        # This is because it should not look like it's running when in the air
        if not self.collide(base):
            self.img = self.IMGS[0]
            self.img_count = 0
        # Draw image of dinosaur's img at self.x, self.y
        win.blit(self.img, (self.x, self.y))

    # Check if dinosaur is colliding with the ground/base
    def collide(self, base):
        dino_mask = self.get_mask()
        base_mask = base.get_mask()

        base_offset = (0, base.y - round(self.y))

        b_point = dino_mask.overlap(base_mask, base_offset)

        if b_point:
            return True
        else:
            return False

    # Get mask of dinosaur to check collision
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


# Base Class
class Base:
    vel = 1
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    # Create 2 base images to continuously loop back and forth when one is out of frame
    # Velocity is capped to prevent moving too quickly
    def move(self):
        if self.vel < 3:
            self.vel += .001
        self.x1 -= self.vel
        self.x2 -= self.vel
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    # Draw 2 base images
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

    # Get the mask of the base to check for collision with dinosaur
    def get_mask(self):
        return pygame.mask.from_surface(self.IMG)

    # Get velocity to sync with obstacles
    def get_vel(self):
        return self.vel


# Generate random obstacles
def generate_obstacle(base):
    # Randomly set bird's y position
    bird_y = random.choice((213 - BIRD_IMGS[0].get_height() - 30,
                            190 + BIRD_IMGS[0].get_height() - 5))
    # Only generate cacti when score is under 1000
    if score < 1000:
        obstacle_type = random.choice((0, 1))
        obstacle_ind = random.choice((0, 1, 2))
        if obstacle_type == 0:
            return Obstacle(213, 'lcacti', obstacle_ind)
        elif obstacle_type == 1:
            return Obstacle(225, 'scacti', obstacle_ind)
    # Start generating birds when score is more than 1000
    if score > 1000:
        obstacle_type = random.choice((0, 1, 2, 3, 4))
        obstacle_ind = random.choice((0, 1, 2))
        if obstacle_type == 0 or obstacle_type == 1:
            return Obstacle(213, 'lcacti', obstacle_ind)
        elif obstacle_type == 2 or obstacle_type == 3:
            return Obstacle(225, 'scacti', obstacle_ind)
        elif obstacle_type == 4:
            return Obstacle(bird_y, 'bird', 0)


# Cloud class for background
class Cloud:
    vel = .5
    GAP = 500
    IMG = CLOUD_IMG

    # Loops through 4 images of cloud to make the background look like it's continuous
    def __init__(self, x, y):
        self.x1 = x
        self.x2 = self.x1 + self.GAP
        self.x3 = self.x2 + self.GAP
        self.x4 = self.x3 + self.GAP
        self.x_array = [self.x1, self.x2, self.x3, self.x4]
        self.y = y
        self.img = CLOUD_IMG

    # Move clouds in the -x direction, capped and increases by .001 pixel per frame
    def move(self):
        if self.vel < 2:
            self.vel += .001

        self.x1 -= self.vel
        self.x2 -= self.vel
        self.x3 -= self.vel
        self.x4 -= self.vel
        # Returns the index of the cloud that is the farthest in the back
        last_cloud_ind = np.argmax(self.x_array)
        # Conveyor belt
        if self.x1 + self.img.get_width() < 0:
            self.x1 = self.x_array[last_cloud_ind] + self.img.get_width()
        if self.x2 + self.img.get_width() < 0:
            self.x2 = self.x_array[last_cloud_ind] + self.img.get_width()
        if self.x3 + self.img.get_width() < 0:
            self.x3 = self.x_array[last_cloud_ind] + self.img.get_width()
        if self.x4 + self.img.get_width() < 0:
            self.x4 = self.x_array[last_cloud_ind] + self.img.get_width()

    # Draw 4 clouds
    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))
        win.blit(self.img, (self.x3, self.y))
        win.blit(self.img, (self.x4, self.y))


# Obstacle class
class Obstacle:
    global score
    # How long each image of the bird should be displayed for
    ANIMATION_TIME = 40
    LCACTI_IMGS = LARGE_CACTI_IMGS
    SCACTI_IMGS = SMALL_CACTI_IMGS
    BIRD_IMGS = BIRD_IMGS

    def __init__(self, y, type, index):
        self.type = type
        self.img_count = 0
        self.index = index
        self.img = self.LCACTI_IMGS[0]
        self.x = 1200
        self.y = y
        self.passed = False

    # Draw image of obstacle based on self.type argument
    def draw(self, win):
        if self.type == 'lcacti':
            self.img = self.LCACTI_IMGS[self.index]
        elif self.type == 'scacti':
            self.img = self.SCACTI_IMGS[self.index]
        elif self.type == 'bird':
            self.img = self.BIRD_IMGS[self.index]
            self.img_count += 1
            if self.img_count < self.ANIMATION_TIME:
                self.img = self.BIRD_IMGS[0]
            elif self.img_count < self.ANIMATION_TIME * 2:
                self.img = self.BIRD_IMGS[1]
            elif self.img_count < self.ANIMATION_TIME * 2 + 1:
                self.img = self.BIRD_IMGS[0]
                self.img_count = 0
        win.blit(self.img, (self.x, self.y))

    # Move obstacle based on the base's velocity
    def move(self, vel):
        self.x -= vel

    # Check if obstacle is colliding with the dinosaur
    def collide(self, dinosaur):
        dinosaur_mask = dinosaur.get_mask()
        obstacle_mask = self.get_mask()

        obstacle_offset = (self.x - dinosaur.x, self.y - round(dinosaur.y))
        o_point = dinosaur_mask.overlap(obstacle_mask, obstacle_offset)

        if o_point:
            return True
        else:
            return False

    # Get mask of obstacle to check for collision
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


# Draw objects to display on the window
def draw_window(win, dinosaur, base, obstacles, cloud, score):
    base.draw(win)
    cloud.draw(win)
    # Loop through obstacle in obstacles
    for obstacle in obstacles:
        obstacle.draw(win)
    # Draw dinosaur
    dinosaur.draw(win, base)
    # Create score and generation texts
    text = stat_font.render(f"Score: {score}", True, (200, 200, 200))
    # Display score and generation texts
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 0))
    # Update the screen
    pygame.display.update()


# Main function that is called from p.run(main, 50)
def main():
    global score
    score = 0
    dinosaur = Dinosaur(25, 300)
    running = True
    # Create initial obstacle object, cloud, and base
    obstacles = [Obstacle(213, 'lcacti', 0)]
    cloud = Cloud(100, 100)
    base = Base(250)

    while running:
        # 165 FPS
        clock.tick(165)
        # Check if the window is closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    dinosaur.jump(base)
        # Set the window's background as white
        screen.fill((255, 255, 255))
        dinosaur.move()
        add_obstacle = False
        # Obstacles to remove
        rem = []
        # Loop through obstacles
        for obstacle in obstacles:
            # Loops through dinosaurs, if dinosaur collides with an obstacle then the game restarts
            if obstacle.collide(dinosaur):
                main()
            # If obstacle hasn't been passed and the latest obstacle generated range falls between 750-900
            if not obstacle.passed and obstacle.x < random.randrange(750, 900):
                obstacle.passed = True
                add_obstacle = True
            # If obstacle is out of frame, add it to array of obstacles to remove --> rem[]
            if obstacle.x + obstacle.img.get_width() < 0:
                rem.append(obstacle)
            # Move obstacle based on the base's velocity
            obstacle.move(base.get_vel())
            # Add obstacles whenever add_obstacle is true
        if add_obstacle:
            # Generate new obstacle
            obstacles.append(generate_obstacle(base))
        # Remove obstacles from obstacles array that are in the remove obstacle array.
        for r in rem:
            obstacles.remove(r)
        # One score is added for each frame
        score += 1
        # Move base and cloud
        base.move()
        cloud.move()
        # Draw objects on the screen
        draw_window(screen, dinosaur, base, obstacles, cloud, score)


main()
