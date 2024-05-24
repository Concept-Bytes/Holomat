import pygame
from pygame import mixer
import sys

# Initialize Pygame
pygame.init()
# Initialize the mixer
mixer.init()

SCREEN_SIZE = (1920, 1200)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230)
NAVY_BLUE = (20, 20, 40)

def play_sound(file_path):
    try:
        mixer.music.load(file_path)
        mixer.music.play()
    except pygame.error as e:
        print(f"Error playing sound {file_path}: {e}")

def run(screen, camera_manager):
    running = True
    count = 0

    circle_radius = 100
    increase_button_center = (SCREEN_SIZE[0] // 2 - 200, SCREEN_SIZE[1] // 2)
    reset_button_center = (SCREEN_SIZE[0] // 2 + 200, SCREEN_SIZE[1] // 2)
    home_button_center = (50 + circle_radius, SCREEN_SIZE[1] - 50 - circle_radius)

    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 72)

    while running:
        if not camera_manager.update():
            continue

        transformed_landmarks = camera_manager.get_transformed_landmarks()
        if transformed_landmarks:
            for hand_landmarks in transformed_landmarks:
                index_pos = (int(hand_landmarks[8][0]), int(hand_landmarks[8][1]))  # INDEX_FINGER_TIP

                if (index_pos[0] - increase_button_center[0])**2 + (index_pos[1] - increase_button_center[1])**2 <= circle_radius**2:
                    play_sound('audio/quick_click.wav')
                    count += 1
                elif (index_pos[0] - reset_button_center[0])**2 + (index_pos[1] - reset_button_center[1])**2 <= circle_radius**2:
                    play_sound('audio/confirmation.wav')
                    count = 0
                elif (index_pos[0] - home_button_center[0])**2 + (index_pos[1] - home_button_center[1])**2 <= circle_radius**2:
                    play_sound('audio/back.wav')
                    running = False

        screen.fill(BLACK)

        # Draw increase button
        pygame.draw.circle(screen, NAVY_BLUE, increase_button_center, circle_radius)
        pygame.draw.circle(screen, LIGHT_BLUE, increase_button_center, circle_radius, 5)
        text_surface = font.render('Increase', True, WHITE)
        text_rect = text_surface.get_rect(center=increase_button_center)
        screen.blit(text_surface, text_rect)

        # Draw reset button
        pygame.draw.circle(screen, NAVY_BLUE, reset_button_center, circle_radius)
        pygame.draw.circle(screen, LIGHT_BLUE, reset_button_center, circle_radius, 5)
        text_surface = font.render('Reset', True, WHITE)
        text_rect = text_surface.get_rect(center=reset_button_center)
        screen.blit(text_surface, text_rect)

        # Draw home button
        pygame.draw.circle(screen, NAVY_BLUE, home_button_center, circle_radius)
        pygame.draw.circle(screen, LIGHT_BLUE, home_button_center, circle_radius, 5)
        text_surface = font.render('Home', True, WHITE)
        text_rect = text_surface.get_rect(center=home_button_center)
        screen.blit(text_surface, text_rect)

        # Draw count
        count_surface = large_font.render(f'Count: {count}', True, WHITE)
        count_rect = count_surface.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 - 400))
        screen.blit(count_surface, count_rect)

        pygame.display.flip()
        pygame.time.delay(50)

if __name__ == '__main__':
    from camera_manager import CameraManager  # Assuming CameraManager is in the parent directory

    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Click Counter App')
    camera_manager = CameraManager('./M.npy', 1920, 1200)
    run(screen, camera_manager)
