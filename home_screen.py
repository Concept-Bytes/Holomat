import pygame
from pygame import mixer
import time
import os
import sys
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
NAVY_BLUE = (20, 20, 40)
LIGHT_BLUE = (173, 216, 230)
HOME_TOGGLE_DELAY = 1.0  # Delay in seconds for home button toggle
APP_SELECT_DELAY = 1.0  # Delay to prevent immediate app launch

def play_sound(file_path):
        mixer.music.load(file_path)
        mixer.music.play()

class AppCircle:
    def __init__(self, center, radius, app_index, final_pos, is_main=False):
        self.center = center
        self.radius = radius
        self.app_index = app_index
        self.text = 'Home' if is_main else f'App {app_index}'
        self.hover_time = 0
        self.is_hovered_flag = False
        self.is_main = is_main
        self.visible = is_main
        self.final_pos = final_pos
        self.animation_start_time = None
        self.is_animating = False
        self.image = self.load_image()

    def load_image(self):
        if not self.is_main:
            image_path = f'./apps/app_{self.app_index}/app_{self.app_index}.jpg'
            if os.path.exists(image_path):
                image = pygame.image.load(image_path)
                return pygame.transform.scale(image, (2 * self.radius, 2 * self.radius))
        return None

    def draw(self, screen):
        if self.is_hovered_flag:
            current_radius = self.radius + min((time.time() - self.hover_time) * 10, self.radius * 0.5)
        else:
            current_radius = self.radius

        if self.animation_start_time is not None:
            elapsed_time = time.time() - self.animation_start_time
            if elapsed_time < 0.5:
                t = elapsed_time / 0.5
                if self.visible:
                    self.center = (
                        int((1 - t) * SCREEN_SIZE[0] // 2 + t * self.final_pos[0]),
                        int((1 - t) * SCREEN_SIZE[1] // 2 + t * self.final_pos[1])
                    )
                else:
                    self.center = (
                        int(t * SCREEN_SIZE[0] // 2 + (1 - t) * self.final_pos[0]),
                        int(t * SCREEN_SIZE[1] // 2 + (1 - t) * self.final_pos[1])
                    )
            else:
                self.center = self.final_pos if self.visible else (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
                self.animation_start_time = None
                self.is_animating = False

        if self.visible or self.is_animating:
            if self.image:
                top_left = (self.center[0] - self.radius, self.center[1] - self.radius)
                screen.blit(self.image, top_left)
            else:
                pygame.draw.circle(screen, NAVY_BLUE, self.center, int(current_radius))
            pygame.draw.circle(screen, LIGHT_BLUE, self.center, int(current_radius), 5)

            if not self.image:
                font = pygame.font.Font(None, 32)
                text_surface = font.render(self.text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=self.center)
                screen.blit(text_surface, text_rect)

    def is_hovered(self, pos):
        return math.hypot(pos[0] - self.center[0], pos[1] - self.center[1]) <= self.radius

def create_circles():
    circles = []
    num_circles = 8
    center_x, center_y = SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2
    main_circle_radius = 100
    app_circle_radius = 75
    distance = 250

    main_circle = AppCircle((center_x, center_y), main_circle_radius, 0, (center_x, center_y), is_main=True)
    circles.append(main_circle)

    angle_step = 360 / num_circles
    for i in range(num_circles):
        angle = math.radians(angle_step * i)
        x = center_x + int(distance * math.cos(angle))
        y = center_y + int(distance * math.sin(angle))
        circles.append(AppCircle((center_x, center_y), app_circle_radius, i + 1, (x, y)))
    return circles

def run_home_screen(screen, camera_manager):
    circles = create_circles()
    main_circle = circles[0]
    running = True
    apps_visible = False
    last_toggle_time = 0
    last_app_select_time = 0

    index_finger_pos = None
    play_sound("./audio/startup.wav")
    while running:
        if not camera_manager.update():
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                camera_manager.release()
                sys.exit()

        screen.fill((0, 0, 0))

        for circle in circles:
            circle.is_hovered_flag = False
            circle.draw(screen)

        transformed_landmarks = camera_manager.get_transformed_landmarks()
        if transformed_landmarks:
            for transformed_coords in transformed_landmarks:
                index_finger_tip = transformed_coords[camera_manager.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                screen_x = int(index_finger_tip[0])
                screen_y = int(index_finger_tip[1])
                index_finger_pos = (screen_x, screen_y)

                for circle in circles:
                    if circle.is_hovered((screen_x, screen_y)):
                        circle.is_hovered_flag = True
                        if circle.is_main:
                            print("Main circle hovered")
                            play_sound("./audio/home.wav")
                            if time.time() - last_toggle_time > HOME_TOGGLE_DELAY:
                                apps_visible = not apps_visible
                                print(f"Toggling apps visibility to: {apps_visible}")
                                last_toggle_time = time.time()
                                for app_circle in circles[1:]:
                                    app_circle.visible = apps_visible
                                    app_circle.animation_start_time = time.time()
                                    app_circle.is_animating = True
                                    # Set last_app_select_time to ensure delay before selecting app
                                    last_app_select_time = time.time() + APP_SELECT_DELAY
                        elif circle.visible and apps_visible:
                            if time.time() > last_app_select_time:
                                print(f"Circle {circle.app_index} hovered with visibility {circle.visible}")
                                try:
                                    app = f'app_{circle.app_index}.app_{circle.app_index}'
                                    print(f"Launching app: {app}")
                                    mod = __import__(f'apps.{app}', fromlist=[''])
                                    play_sound("./audio/confirmation.wav")
                                    mod.run(screen, camera_manager)  # Pass camera_manager to the app
                                    last_app_select_time = time.time()
                                except ModuleNotFoundError:
                                    print(f"Module 'apps.{app}' not found.")
                                    play_sound("./audio/reject.wav")
                    else:
                        circle.hover_time = time.time() if circle.visible else 0

        if index_finger_pos:
            pygame.draw.circle(screen, LIGHT_BLUE, index_finger_pos, 15, 3)

        main_circle.draw(screen)

        pygame.display.flip()
        pygame.time.delay(50)

if __name__ == '__main__':
    SCREEN_WIDTH = int(os.getenv('SCREEN_WIDTH'))
    SCREEN_HEIGHT = int(os.getenv('SCREEN_HEIGHT'))
    os.environ['SDL_VIDEO_WINDOW_POS'] = '-3440,0'
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption('Home Screen')
    camera_manager = CameraManager('./M.npy', SCREEN_WIDTH, SCREEN_HEIGHT)
    run_home_screen(screen, camera_manager)
