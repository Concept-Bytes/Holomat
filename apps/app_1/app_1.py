import pygame
from pygame import mixer
import sys
import time
import math
from camera_manager import CameraManager
from dotenv import load_dotenv
import os

load_dotenv()
# Initialize Pygame
pygame.init()
# Initialize the mixer
mixer.init()
SCREEN_WIDTH = int(os.getenv('SCREEN_WIDTH'))
SCREEN_HEIGHT = int(os.getenv('SCREEN_HEIGHT'))
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
WHITE = (255, 255, 255)
NAVY_BLUE = (20, 20, 40)
PIXEL_TO_MM = 0.4478  # Adjust this variable as needed
PINCH_RELEASE_DISTANCE = 60  # Distance to release the pinch
PINCH_HOLD_TIME = 0.2  # Minimum time to hold the pinch before releasing

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def play_sound(file_path):
        mixer.music.stop()
        mixer.music.load(file_path)
        mixer.music.play()

def draw_line_with_measurement(screen, start_point, end_point):
    if start_point and end_point:
        pygame.draw.line(screen, LIGHT_BLUE, start_point, end_point, 2)
        pygame.draw.circle(screen, LIGHT_BLUE, start_point, 5)
        pygame.draw.circle(screen, LIGHT_BLUE, end_point, 5)
        mid_line_point = ((start_point[0] + end_point[0]) // 2, (start_point[1] + end_point[1]) // 2)
        line_length = distance(start_point, end_point) * PIXEL_TO_MM
        font = pygame.font.Font(None, 36)
        text_surface = font.render(f'{line_length:.2f} mm', True, WHITE)
        screen.blit(text_surface, mid_line_point)

def run(screen, camera_manager):
    running = True
    drawing = False
    start_point = None
    end_point = None
    permanent_lines = []
    pinch_start_time = None

    home_button_center = (150, 100)  # Moved farther right and down
    home_button_radius = 50

    clear_button_rect = pygame.Rect((SCREEN_SIZE[0] // 2 - 150, SCREEN_SIZE[1] - 150, 300, 70))

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
                thumb_pos = (int(hand_landmarks[4][0]), int(hand_landmarks[4][1]))  # THUMB_TIP
                index_pos = (int(hand_landmarks[8][0]), int(hand_landmarks[8][1]))  # INDEX_FINGER_TIP

                mid_point = ((thumb_pos[0] + index_pos[0]) // 2, (thumb_pos[1] + index_pos[1]) // 2)
                pygame.draw.circle(screen, LIGHT_BLUE, mid_point, 10, 3)

                pygame.draw.circle(screen, WHITE, thumb_pos, 5)
                pygame.draw.circle(screen, WHITE, index_pos, 5)

                distance_between_fingers = distance(thumb_pos, index_pos)
                if distance_between_fingers < 50:  # Threshold for starting a pinch
                    pygame.draw.circle(screen, WHITE, mid_point, 10)
                    if not drawing:
                        play_sound('audio/quick_click.wav')
                        start_point = mid_point
                        drawing = True
                        pinch_start_time = time.time()
                        play_sound('audio/drawing.wav')
                    else:
                        end_point = mid_point
                else:
                    if drawing and (distance_between_fingers > PINCH_RELEASE_DISTANCE or (time.time() - pinch_start_time) > PINCH_HOLD_TIME):
                        if start_point and end_point:
                            play_sound('audio/quick_click.wav')
                            permanent_lines.append((start_point, end_point))
                        drawing = False

        for line in permanent_lines:
            draw_line_with_measurement(screen, line[0], line[1])

        if drawing and start_point and end_point:
            draw_line_with_measurement(screen, start_point, end_point)

        # Check if the cursor touches the home button or the clear button
        if index_pos and distance(index_pos, home_button_center) <= home_button_radius:
            running = False
            play_sound('audio/back.wav')
        elif index_pos and clear_button_rect.collidepoint(index_pos):
            permanent_lines = []

        # Draw home button
        pygame.draw.circle(screen, NAVY_BLUE, home_button_center, home_button_radius)
        pygame.draw.circle(screen, LIGHT_BLUE, home_button_center, home_button_radius, 5)
        font = pygame.font.Font(None, 36)
        text_surface = font.render('Home', True, WHITE)
        text_rect = text_surface.get_rect(center=home_button_center)
        screen.blit(text_surface, text_rect)

        # Draw clear button
        pygame.draw.rect(screen, NAVY_BLUE, clear_button_rect, border_radius=15)
        pygame.draw.rect(screen, LIGHT_BLUE, clear_button_rect, 5, border_radius=15)
        text_surface = font.render('Clear', True, WHITE)
        text_rect = text_surface.get_rect(center=clear_button_rect.center)
        screen.blit(text_surface, text_rect)

        pygame.display.flip()
        pygame.time.delay(1)

