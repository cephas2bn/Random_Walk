# random_walk.py
# Visual random walk demo (2D) with live stats.
# Requirements: Python 3.10+, pygame (pip install pygame)

import math
import random
import pygame
from collections import deque

# -------------------- Config --------------------
pygame.init()
info = pygame.display.Info()
W, H = info.current_w // 2, info.current_h // 2   # adaptive window size
FPS = 240                       # update rate (higher -> smoother/faster)
STEP_PIXELS = 2                 # step length (pixels)
EIGHT_DIR = True                # True: 8 directions, False: 4 (N,E,S,W)
TRAIL_LEN = 100000              # max points kept in trail (for memory)
DOT_RADIUS = 3                  # walker radius
BG_COLOR = (18, 18, 22)         # background
TRAIL_COLOR = (80, 180, 255)    # trail line
DOT_COLOR = (255, 70, 70)       # walker
ORIGIN_COLOR = (240, 240, 240)  # origin cross-hair
BOUND_MARGIN = 20               # soft margin before bounce
FONT_SIZE = 18
SHOW_GRID = False               # togglable (press G)
GRID_SPACING = 60


 # half your screen size

# ------------------------------------------------

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("2D Random Walk — Probability & Stochastic Processes")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", FONT_SIZE)

# Walk state
origin = (W // 2, H // 2)
x, y = origin
trail = deque(maxlen=TRAIL_LEN)
trail.append((x, y))
steps = 0
squared_displacements_sum = 0.0  # for running MSD
paused = False
show_grid = SHOW_GRID

def step():
    global x, y
    # Choose a unit step direction
    if EIGHT_DIR:
        dirs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    else:
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    dx, dy = random.choice(dirs)
    # Normalize diagonals to keep step length ~ STEP_PIXELS
    if dx != 0 and dy != 0:
        norm = math.sqrt(2)
        nx, ny = (dx/ norm, dy/ norm)
    else:
        nx, ny = dx, dy

    return x + nx * STEP_PIXELS, y + ny * STEP_PIXELS

def soft_bounce(nx, ny):
    # Keep the walker within the window by reflecting at the edges.
    bx, by = nx, ny
    if bx < BOUND_MARGIN: bx = 2*BOUND_MARGIN - bx
    if bx > W-BOUND_MARGIN: bx = 2*(W-BOUND_MARGIN) - bx
    if by < BOUND_MARGIN: by = 2*BOUND_MARGIN - by
    if by > H-BOUND_MARGIN: by = 2*(H-BOUND_MARGIN) - by
    return bx, by

def draw_grid():
    for gx in range(0, W, GRID_SPACING):
        pygame.draw.line(screen, (35,35,40), (gx,0), (gx,H))
    for gy in range(0, H, GRID_SPACING):
        pygame.draw.line(screen, (35,35,40), (0,gy), (W,gy))

def reset():
    global x, y, trail, steps, squared_displacements_sum
    x, y = origin
    trail = deque([(x, y)], maxlen=TRAIL_LEN)
    steps = 0
    squared_displacements_sum = 0.0

def save_frame():
    pygame.image.save(screen, "random_walk_frame.png")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: reset()
            elif event.key == pygame.K_p: paused = not paused
            elif event.key == pygame.K_s: save_frame()
            elif event.key == pygame.K_g: show_grid = not show_grid

    if not paused:
        nx, ny = step()
        nx, ny = soft_bounce(nx, ny)
        x, y = nx, ny
        trail.append((x, y))
        steps += 1
        # update running MSD
        dx = x - origin[0]
        dy = y - origin[1]
        r2 = dx*dx + dy*dy
        squared_displacements_sum += r2
        msd = squared_displacements_sum / steps

    # ---- draw ----
    screen.fill(BG_COLOR)
    if show_grid:
        draw_grid()

    # origin crosshair
    pygame.draw.line(screen, ORIGIN_COLOR, (origin[0]-8, origin[1]), (origin[0]+8, origin[1]), 1)
    pygame.draw.line(screen, ORIGIN_COLOR, (origin[0], origin[1]-8), (origin[0], origin[1]+8), 1)

    # trail
    if len(trail) > 1:
        pygame.draw.lines(screen, TRAIL_COLOR, False, trail, 2)

    # walker
    pygame.draw.circle(screen, DOT_COLOR, (int(x), int(y)), DOT_RADIUS)

    # stats text
    dist = math.sqrt((x-origin[0])**2 + (y-origin[1])**2)
    lines = [
        f"Steps: {steps:,}",
        f"Distance from origin: {dist:7.1f}px",
        f"Mean Squared Displacement (MSD): {msd:10.1f}" if steps else "MSD: n/a",
        f"Controls: [P]ause  [R]eset  [S]creenshot  [G]rid  [Esc] quit",
        "Theory: For a simple random walk in 2D, E[r^2] ≈ c * t (linear in time)."
    ]
    ytext = 10
    for line in lines:
        surf = font.render(line, True, (220, 220, 230))
        screen.blit(surf, (10, ytext))
        ytext += FONT_SIZE + 4

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
