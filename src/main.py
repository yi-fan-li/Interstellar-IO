import math 
import numpy as np
import pygame as pg
from Body import Body
import random
from Camera import Camera
from Spawner import Spawner
from GravitySlider import GravitySlider
import Body as BodyFile
from TimeSlider import TimeSlider
from ParticlesSlider import ParticlesSlider

DT = 0.5 # Delta time for the physics engine
UPDATES_PER_FRAME = 1 # Number of iterations of the physics engine for each frame

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
NUM_OF_PARTICLES = 25
MIN_ZOOM = 0.1
MAX_ZOOM = 20
SLIDER_LENGTH = 200
SLIDER_HEIGHT = 5


pg.init()
FONT1 = pg.font.Font(None, 30)
FONT2 = pg.font.Font(None, 20)

BLACK = (0,0,0)
WHITE = (255,255,255)

gravitySlider = GravitySlider(20, 20, SLIDER_LENGTH, SLIDER_HEIGHT, 1, 20, BodyFile.G)
timeSlider = TimeSlider(20, 50, SLIDER_LENGTH, SLIDER_HEIGHT, 0.01, 3, DT)
particlesSlider = ParticlesSlider(20, 80, SLIDER_LENGTH, SLIDER_HEIGHT, 1, 100, NUM_OF_PARTICLES)

def create_text_surface(text, font, color):
    text_surface = font.render(text, True, color)
    return text_surface

def draw_grid(surface, grid_color, cell_size, offset):
    """
    Draws a grid on the given surface.
    Args:
    - surface: The Pygame surface to draw on.
    - grid_color: The color of the grid lines.
    - cell_size: The size of each cell in the grid.
    """
    width, height = surface.get_size()
    # Draw vertical lines
    for x in range(0, 64 * width, cell_size):
        pg.draw.line(surface, grid_color, (x - offset[0], 0), (x - offset[0], height))
    # Draw horizontal lines
    for y in range(0, 64 * height, cell_size):
        pg.draw.line(surface, grid_color, (0, y - offset[1]), (width, y - offset[1]))

# Usage example within your game loop:
# Define your grid color and cell size
grid_color = (200, 200, 200)  # Light grey color for the grid lines
cell_size = 40  # Adjust the cell size as per your requirement
window_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pg.display.set_mode(window_size)
# In your main game loop, before drawing anything else:
screen.fill((0, 0, 0))  # Fill the screen with black or your desired background color

def set_gravitational_constant(value):
    global G
    BodyFile.G = value

def main():
    global DT
    global NUM_OF_PARTICLES
    print("interstellarIO")

    pg.init()
    

    pg.display.set_caption("Interstellar IO")

    screen = pg.display.set_mode(window_size)

    bodies = []

    first_player = Body(100, np.array([WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2]), np.array([0.0, 0.0]), 0)
    next_player_uid = 1

    bodies.append(first_player)
    
    clock = pg.time.Clock()
    camera = Camera(bodies[0], screen)
    targetZoom = camera.calculate_zoom_based_on_mass()
    spawner = Spawner(bodies[0])
    
    running = True
    # pygame main loop
    while running:
        screen.fill((255, 255, 255))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            gravitySlider.handle_event(event)
            timeSlider.handle_event(event)
            particlesSlider.handle_event(event)
            if event.type == pg.MOUSEWHEEL:
                sensitivity = 0.1
                if camera.zoom + event.y * sensitivity > MIN_ZOOM and camera.zoom + event.y * sensitivity < MAX_ZOOM: 
                    camera.zoom += event.y * sensitivity
                    
            if pg.key.get_pressed()[pg.K_SPACE]:
                direction = np.array([pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]]) - np.array([WINDOW_WIDTH/2, WINDOW_HEIGHT/2])
                if np.linalg.norm(direction) != 0:
                    direction = direction / np.linalg.norm(direction)
                else:
                    direction = np.array([0.0, 0.0])
                ejectedMass = camera.obj.mass / 250
                relMassVelocity = 4 * math.sqrt(camera.obj.mass)
                camera.obj.mass -= ejectedMass
                dforce = camera.obj.mass * ejectedMass * relMassVelocity
                dforce /= (DT * (1 - ejectedMass))

                camera.obj.add_force(direction, dforce)
            
        draw_grid(screen, grid_color, cell_size, camera.offset)
        gravitySlider.draw(screen)
        timeSlider.draw(screen)
        particlesSlider.draw(screen)

        for i in range(UPDATES_PER_FRAME):
            for j in bodies:
                 current = 0
            body_count = len(bodies)
            while current < body_count:
                merges = bodies[current].update(DT / UPDATES_PER_FRAME, bodies, current + 1, (bodies[current].uid == camera.obj.uid), spawner.newRadius(camera.obj))
                for m in merges:

                    if m[0] == -1:
                        # Self was deleted
                        current -= 1
                    if m[0] == camera.obj.uid:
                        # Camera needs change
                        
                        for b in bodies:
                            if b.uid == m[1]:
                                camera.obj = b
                                ntargetZoom = camera.calculate_zoom_based_on_mass()
                                if ntargetZoom != targetZoom:
                                    print("a")
                                break

                body_count -= len(merges)
                current += 1

        gValueText = create_text_surface(str(round(BodyFile.G, 2)), FONT1, BLACK)
        timeValueText = create_text_surface(str(round(DT, 2)), FONT1, BLACK)
        numParticlesText = create_text_surface(str(NUM_OF_PARTICLES), FONT1, BLACK)

        gText = create_text_surface("Gravitational Constant", FONT2, BLACK)
        timeFactor = create_text_surface("Time Factor", FONT2, BLACK)
        numParticles = create_text_surface("Number of particles", FONT2, BLACK)

        screen.blit(gValueText, (230, 15))
        screen.blit(timeValueText, (230, 45))
        screen.blit(numParticlesText, (230, 75))

        screen.blit(gText, (60, 25))
        screen.blit(timeFactor, (90, 55))
        screen.blit(numParticles, (70, 90))

        n_particles = len(bodies)
        for i in range(NUM_OF_PARTICLES - n_particles):
            bodies.append(spawner.spawnParticle(camera.obj, next_player_uid))
            next_player_uid += 1
        set_gravitational_constant(gravitySlider.get_value())
        DT = timeSlider.get_value()
        NUM_OF_PARTICLES = int(particlesSlider.get_value())
        
        camera.update(targetZoom)
        camera.draw(bodies)
        pg.display.flip()
        clock.tick(60)
    
    pg.quit()

if __name__ == "__main__":
    main()