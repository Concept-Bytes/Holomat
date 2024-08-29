import pygame
import sys
import time
import math
from datetime import datetime, timedelta
import calendar
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path

# Initialize Pygame and set up some basic screen properties and colors
pygame.init()
SCREEN_SIZE = (1280, 720)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
WHITE = (255, 255, 255)
NAVY_BLUE = (20, 20, 40)
RED = (255, 0, 0)
PIXEL_TO_MM = 0.4478 

# Font and Layout Settings
HEADER_FONT = pygame.font.Font(None, 40)
DAY_FONT = pygame.font.Font(None, 32)
CALENDAR_FONT = pygame.font.Font(None, 28)
CLOCK_FONT = pygame.font.Font(None, 60)
DATE_FONT = pygame.font.Font(None, 40)
EVENT_FONT = pygame.font.Font(None, 30) 

CENTER_X = SCREEN_SIZE[0] // 2
CENTER_Y = SCREEN_SIZE[1] // 2

PINCH_THRESHOLD = 50  # Threshold for detecting a pinch
pinch_active = False

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def play_sound(file_path):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

#   draw the current time and date on the screen
def draw_clock_and_date(screen):
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%a, %b %d, %Y")

    time_surface = CLOCK_FONT.render(current_time, True, WHITE)
    time_rect = time_surface.get_rect(center=(CENTER_X, CENTER_Y - 260))
    screen.blit(time_surface, time_rect)

    date_surface = DATE_FONT.render(current_date, True, WHITE)
    date_rect = date_surface.get_rect(center=(CENTER_X, CENTER_Y - 310))
    screen.blit(date_surface, date_rect)

#   draw the calendar's header, including month and year
def draw_calendar_header(screen, month, year):
    header_surface = HEADER_FONT.render(f"{calendar.month_name[month]} {year}", True, WHITE)
    header_rect = header_surface.get_rect(center=(CENTER_X, CENTER_Y - 160))
    screen.blit(header_surface, header_rect)

    # Draw navigation arrows
    pygame.draw.polygon(screen, WHITE, [(CENTER_X - 150, CENTER_Y - 160), (CENTER_X - 135, CENTER_Y - 170), (CENTER_X - 135, CENTER_Y - 150)])
    pygame.draw.polygon(screen, WHITE, [(CENTER_X + 150, CENTER_Y - 160), (CENTER_X + 135, CENTER_Y - 170), (CENTER_X + 135, CENTER_Y - 150)])

#   draw the days of the week on the screen
def draw_days_of_week(screen):
    days = ["S", "M", "T", "W", "T", "F", "S"]
    for i, day in enumerate(days):
        day_surface = DAY_FONT.render(day, True, WHITE)
        day_rect = day_surface.get_rect(center=(CENTER_X - 225 + i * 75, CENTER_Y - 110))
        screen.blit(day_surface, day_rect)

#   draw the calendar grid and highlight the current or selected day
def draw_calendar(screen, month, year, selected_day=None):
    cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
    days = cal.monthdayscalendar(year, month)

    today = datetime.today()
    current_day = today.day if today.month == month and today.year == year else None
    day_positions = {}

    for row, week in enumerate(days):
        for col, day in enumerate(week):
            if day == 0:
                continue 

            x = CENTER_X - 225 + col * 75
            y = CENTER_Y - 50 + row * 60 
            day_positions[day] = (x, y)

            if day == current_day:
                pygame.draw.circle(screen, RED, (x, y), 20)  # Red circle for current day

            if day == selected_day:
                pygame.draw.circle(screen, LIGHT_BLUE, (x, y), 25, 3)  # Highlight selected day

            day_surface = CALENDAR_FONT.render(str(day), True, WHITE)
            day_rect = day_surface.get_rect(center=(x, y))
            screen.blit(day_surface, day_rect)

    return day_positions

#   draw the list of events on the screen
def draw_events(screen, events):
    y_offset = CENTER_Y - 260
    x_offset = CENTER_X + 300

    heading_surface = HEADER_FONT.render("Events", True, WHITE)
    heading_rect = heading_surface.get_rect(topleft=(x_offset, y_offset))
    screen.blit(heading_surface, heading_rect)
    y_offset += 60

    for event in events:
        event_surface = EVENT_FONT.render(event, True, WHITE)
        event_rect = event_surface.get_rect(topleft=(x_offset, y_offset))
        screen.blit(event_surface, event_rect)
        y_offset += 40

#   fetch events from Google Calendar
def get_google_calendar_events(day=None, month=None, year=None):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r"pathtogooglecloudapi",
                SCOPES,
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    
    if day and month and year:
        start_time = datetime(year, month, day).isoformat() + "Z"
        end_time = (datetime(year, month, day) + timedelta(days=1)).isoformat() + "Z"
    else:
        start_time = datetime.utcnow().isoformat() + "Z"
        end_time = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_time,
            timeMax=end_time,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    event_list = []
    if not events:
        event_list.append("No events today.")
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        time = datetime.fromisoformat(start).strftime("%I:%M %p")
        summary = event["summary"]
        event_list.append(f"{time} - {summary}")

    return event_list

#   change the month being displayed on the calendar
def change_month(direction):
    global month, year
    month += direction
    if month > 12:
        month = 1
        year += 1
    elif month < 1:
        month = 12
        year -= 1

#   handle pinch gestures for changing months or selecting a day
def handle_pinch(mid_point, day_positions):
    global pinch_active, selected_day, events
    if not pinch_active:
        left_arrow_pos = (CENTER_X - 150, CENTER_Y - 160)
        right_arrow_pos = (CENTER_X + 150, CENTER_Y - 160)

        if distance(mid_point, left_arrow_pos) < PINCH_THRESHOLD:
            change_month(-1)  # Move the month backward
            pinch_active = True
        elif distance(mid_point, right_arrow_pos) < PINCH_THRESHOLD:
            change_month(1)  # Move the month forward
            pinch_active = True
        else:
            for day, pos in day_positions.items():
                if distance(mid_point, pos) < PINCH_THRESHOLD:
                    selected_day = day
                    events = get_google_calendar_events(day, month, year)
                    pinch_active = True
                    break

#   reset the pinch state
def reset_pinch():
    global pinch_active
    pinch_active = False

# Main   run the calendar application
def run(screen, camera_manager):
    global month, year, selected_day, events
    running = True
    home_button_center = (150, CENTER_Y)
    home_button_radius = 50

    month = datetime.now().month
    year = datetime.now().year

    selected_day = None
    day_positions = {}
    events = get_google_calendar_events()

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
        index_pos = None

        if transformed_landmarks:
            for hand_landmarks in transformed_landmarks:
                thumb_pos = (int(hand_landmarks[4][0]), int(hand_landmarks[4][1]))
                index_pos = (int(hand_landmarks[8][0]), int(hand_landmarks[8][1]))

                mid_point = ((thumb_pos[0] + index_pos[0]) // 2, (thumb_pos[1] + index_pos[1]) // 2)
                pygame.draw.circle(screen, LIGHT_BLUE, mid_point, 10, 3)

                pygame.draw.circle(screen, WHITE, thumb_pos, 5)
                pygame.draw.circle(screen, WHITE, index_pos, 5)

                distance_between_fingers = distance(thumb_pos, index_pos)
                if distance_between_fingers < PINCH_THRESHOLD:
                    handle_pinch(mid_point, day_positions)
                else:
                    reset_pinch()  # Reset the pinch when fingers are apart

        # Check if the cursor touches the home button
        if index_pos and distance(index_pos, home_button_center) <= home_button_radius:
            running = False
            play_sound("audio/back.wav")

        # Draw home button
        pygame.draw.circle(screen, NAVY_BLUE, home_button_center, home_button_radius)
        pygame.draw.circle(screen, LIGHT_BLUE, home_button_center, home_button_radius, 5)
        font = pygame.font.Font(None, 36)
        text_surface = font.render("Home", True, WHITE)
        text_rect = text_surface.get_rect(center=home_button_center)
        screen.blit(text_surface, text_rect)

        # Draw the clock, calendar, and events
        draw_clock_and_date(screen)
        draw_calendar_header(screen, month, year)
        draw_days_of_week(screen)
        day_positions = draw_calendar(screen, month, year, selected_day)
        draw_events(screen, events)

        pygame.display.flip()
        pygame.time.delay(1)

if __name__ == "__main__":
    screen = pygame.display.set_mode((1280, 720), pygame.NOFRAME | pygame.FULLSCREEN)
    pygame.display.set_caption("Hand Tracking Calendar")
    camera_manager = CameraManager("./M1.npy", 1920, 1200) 
    run(screen, camera_manager)
  #made by @r3z2
