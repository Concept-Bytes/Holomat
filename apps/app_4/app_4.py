import pygame
from pygame import mixer
import sys
import time
import math
from camera_manager import CameraManager
from dotenv import load_dotenv
import os

load_dotenv()
pygame.init()
mixer.init()

SCREEN_WIDTH = int(os.getenv('SCREEN_WIDTH'))
SCREEN_HEIGHT = int(os.getenv('SCREEN_WIDTH'))
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
WHITE = (255, 255, 255)
NAVY_BLUE = (20, 20, 40)
PINCH_RELEASE_DISTANCE = 60  
PINCH_HOLD_TIME = 0.2  

PADDLE_WIDTH = 150
PADDLE_HEIGHT = 20
BALL_RADIUS = 10
BRICK_WIDTH = 125
BRICK_HEIGHT = 30
BRICKS_PER_ROW = SCREEN_SIZE[0] // BRICK_WIDTH
BRICK_ROWS = 5
ball_dx = 7  
ball_dy = -7

RED = (255, 0, 0)
BLUE = (0, 0, 255)

def create_bricks():
    bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICKS_PER_ROW):
            brick = pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT + 50, BRICK_WIDTH - 5, BRICK_HEIGHT - 5)
            bricks.append(brick)
    return bricks

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def run(screen, camera_manager):
    global ball_dx, ball_dy
    running = True

    paddle = pygame.Rect(SCREEN_SIZE[0] // 2 - PADDLE_WIDTH // 2, SCREEN_SIZE[1] - 100, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
    bricks = create_bricks()

    home_button_center = (100, SCREEN_SIZE[1] - 100)
    home_button_radius = 50

    while running:
        if not camera_manager.update():
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                camera_manager.release()
                sys.exit()

        screen.fill(BLACK)

        transformed_landmarks = camera_manager.get_transformed_landmarks()
        if transformed_landmarks:
            for hand_landmarks in transformed_landmarks:
                index_pos = (int(hand_landmarks[8][0]), int(hand_landmarks[8][1]))  # INDEX_TIP

                # Move the paddle to follow the index finger
                paddle.centerx = index_pos[0]
                paddle.clamp_ip(screen.get_rect())

                pygame.draw.circle(screen, WHITE, index_pos, 5)  # Draw index finger

        ball.x += ball_dx
        ball.y += ball_dy

        if ball.left <= 0 or ball.right >= SCREEN_SIZE[0]:
            ball_dx *= -1
        if ball.top <= 0:
            ball_dy *= -1
        if ball.bottom >= SCREEN_SIZE[1]:
            paddle = pygame.Rect(SCREEN_SIZE[0] // 2 - PADDLE_WIDTH // 2, SCREEN_SIZE[1] - 50, PADDLE_WIDTH, PADDLE_HEIGHT)
            ball = pygame.Rect(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
            bricks = create_bricks()
            ball_dx, ball_dy = 7, -7

        if ball.colliderect(paddle):
            ball_dy *= -1

        for brick in bricks[:]:
            if ball.colliderect(brick):
                bricks.remove(brick)
                ball_dy *= -1
                break

        pygame.draw.rect(screen, WHITE, paddle)
        pygame.draw.ellipse(screen, BLUE, ball)
        for brick in bricks:
            pygame.draw.rect(screen, RED, brick)

        pygame.draw.circle(screen, NAVY_BLUE, home_button_center, home_button_radius)
        pygame.draw.circle(screen, LIGHT_BLUE, home_button_center, home_button_radius, 5)
        font = pygame.font.Font(None, 36)
        text_surface = font.render('Home', True, WHITE)
        text_rect = text_surface.get_rect(center=home_button_center)
        screen.blit(text_surface, text_rect)

        if transformed_landmarks:
            if distance(index_pos, home_button_center) <= home_button_radius:
                running = False

        pygame.display.flip()
        pygame.time.delay(10)

