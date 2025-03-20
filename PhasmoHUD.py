##Version 1.5 created by UndeadWolf 3/20/2025 - Calibrated for Phasmophobia v0.12.0.2 ##

import pygame
import sys
import time
import keyboard
import win32gui
import win32con
import ctypes
import math

# Initialize pygame
pygame.init()

# Set application icon - using path relative to the executable
try:
    import os
    import sys
    
    # Get the directory where the executable or script is located
    if getattr(sys, 'frozen', False):
        # If running as compiled executable
        application_path = os.path.dirname(sys.executable)
    else:
        # If running as script
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to the icon file
    icon_path = os.path.join(application_path, 'phasmo_hud_icon.png')
    
    # Load the icon
    app_icon = pygame.image.load(icon_path)
    pygame.display.set_icon(app_icon)
    print(f"Successfully loaded icon from: {icon_path}")
except Exception as e:
    print(f"Could not load icon file: {e}. Using default icon.")

# Get screen resolution
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

# Constants - adjusted size for smudge timer
WIDTH, HEIGHT = 200, 150  # Further increased height to accommodate smudge timer
BAR_WIDTH = 180
BAR_HEIGHT = 20
BAR_X = (WIDTH - BAR_WIDTH) // 2
BAR_Y = (HEIGHT - BAR_HEIGHT) // 2  # Adjusted position

# Hunt timer position
HUNT_BAR_Y = BAR_Y - 30

# Smudge timer position
SMUDGE_TIMER_Y = BAR_Y + 50

# Position in bottom right corner (with some padding)
WINDOW_X = screen_width - WIDTH - 20
WINDOW_Y = screen_height - HEIGHT - 40

# Colors
BACKGROUND = (20, 20, 20, 180)  # Dark with transparency
BAR_BACKGROUND = (50, 50, 50)
STAMINA_COLOR = (0, 255, 0)  # Green
RECOVERY_COLOR = (255, 0, 0)  # Red
DELAY_COLOR = (255, 100, 100)  # Light red for delay
RAMPING_COLOR = (255, 165, 0)  # Orange for ramping regen
TEXT_COLOR = (255, 255, 255)  # White
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (100, 100, 100)
CAROUSEL_BG = (40, 40, 40)
SMUDGE_COLOR = (100, 100, 255)  # Light blue for smudge timer
SPIRIT_COLOR = (255, 255, 0)  # Yellow for Spirit message
CONFIG_PANEL_BG = (10, 10, 10, 230)  # Very dark with high opacity. This is for the hunt timer config ui background for better visibility.

# ===== STAMINA MECHANICS - ADJUST THESE VALUES AS NEEDED =====
MAX_STAMINA = 100
# Sprint depletes 100% stamina in 3 seconds
SPRINT_DEPLETION_RATE = MAX_STAMINA / 3  
# Maximum regeneration rate (20% stamina per second when not sprinting)
MAX_RECOVERY_RATE = MAX_STAMINA * 0.35  
# Full recovery period when stamina is depleted (seconds)
RECOVERY_PERIOD = 5  
# Delay before regeneration begins after stopping sprint (seconds)
REGEN_DELAY = 1.35  
# Time it takes for regeneration to reach full speed after delay (seconds)
REGEN_RAMP_TIME = 2.75
# Minimum regeneration rate as a percentage of max rate (0.0 to 1.0)
# 0.0 means starting from zero regen, 0.5 means starting at half speed
MIN_REGEN_PERCENT = 0.1  
# ============================================================

# ===== HUNT TIMER SETTINGS =====
# Hunt durations in seconds based on map size and difficulty
HUNT_DURATIONS = {
    "Amateur": {"Small": 15, "Medium": 30, "Large": 40},
    "Intermediate": {"Small": 20, "Medium": 40, "Large": 50},
    "Pro+": {"Small": 30, "Medium": 50, "Large": 60}
}
# Default settings
current_map_size = "Small"
current_difficulty = "Pro+"
# ==============================

# ===== SMUDGE TIMER SETTINGS =====
MAX_SMUDGE_TIME = 180  # Maximum time to display (Spirit - 180s)
SPIRIT_MESSAGE_DURATION = 3  # Duration to show "Likely Spirit" message
# ================================

# Create the window with transparency
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME | pygame.SRCALPHA)
pygame.display.set_caption("Phasmophobia Overlay")

# Set window to be always on top and positioned at bottom right
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, WINDOW_X, WINDOW_Y, WIDTH, HEIGHT, 0)

# Make the window click-through
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                      win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | 
                      win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)

# Fonts
font = pygame.font.SysFont('Arial', 12)
font_small = pygame.font.SysFont('Arial', 10)
font_medium = pygame.font.SysFont('Arial', 13)  # Medium font for labels
font_large = pygame.font.SysFont('Arial', 14)  # Larger font for smudge timer

# Stamina state
stamina = MAX_STAMINA
in_recovery = False
recovery_start_time = 0
last_sprint_time = 0
was_sprinting = False
regen_start_time = 0

# Hunt timer state
hunt_active = False
hunt_start_time = 0
hunt_duration = HUNT_DURATIONS[current_difficulty][current_map_size]

# Smudge timer state
smudge_active = False
smudge_start_time = 0
smudge_reached_max = False
smudge_max_reached_time = 0

# Config UI state
show_config = False
temp_map_size = current_map_size
temp_difficulty = current_difficulty

# Carousel options
map_sizes = ["Small", "Medium", "Large"]
difficulties = ["Amateur", "Intermediate", "Pro+"]

# Button dimensions
button_width = 80
button_height = 25
button_x = (WIDTH - button_width) // 2
button_y = HEIGHT - button_height - 10

# Carousel dimensions
carousel_width = 100
carousel_height = 20
map_carousel_x = (WIDTH - carousel_width) // 2 + 15
map_carousel_y = 35
diff_carousel_x = (WIDTH - carousel_width) // 2 + 15
diff_carousel_y = 65

# Function to check if mouse is over a rect
def is_mouse_over_rect(mouse_pos, rect):
    return rect.collidepoint(mouse_pos)

# Function to draw a button
def draw_button(text, x, y, width, height, mouse_pos):
    button_rect = pygame.Rect(x, y, width, height)
    color = BUTTON_HOVER_COLOR if is_mouse_over_rect(mouse_pos, button_rect) else BUTTON_COLOR
    pygame.draw.rect(screen, color, button_rect)
    pygame.draw.rect(screen, TEXT_COLOR, button_rect, 1)
    
    text_surf = font.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=(x + width//2, y + height//2))
    screen.blit(text_surf, text_rect)
    
    return button_rect

# Function to draw a carousel
def draw_carousel(options, current_option, x, y, width, height, mouse_pos):
    # Draw background
    carousel_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, CAROUSEL_BG, carousel_rect)
    pygame.draw.rect(screen, TEXT_COLOR, carousel_rect, 1)
    
    # Draw current option
    text_surf = font.render(current_option, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=(x + width//2, y + height//2))
    screen.blit(text_surf, text_rect)
    
    # Draw arrows
    left_arrow_rect = pygame.Rect(x, y, height, height)
    right_arrow_rect = pygame.Rect(x + width - height, y, height, height)
    
    left_color = BUTTON_HOVER_COLOR if is_mouse_over_rect(mouse_pos, left_arrow_rect) else BUTTON_COLOR
    right_color = BUTTON_HOVER_COLOR if is_mouse_over_rect(mouse_pos, right_arrow_rect) else BUTTON_COLOR
    
    pygame.draw.rect(screen, left_color, left_arrow_rect)
    pygame.draw.rect(screen, right_color, right_arrow_rect)
    pygame.draw.rect(screen, TEXT_COLOR, left_arrow_rect, 1)
    pygame.draw.rect(screen, TEXT_COLOR, right_arrow_rect, 1)
    
    left_text = font.render("<", True, TEXT_COLOR)
    right_text = font.render(">", True, TEXT_COLOR)
    
    screen.blit(left_text, left_text.get_rect(center=left_arrow_rect.center))
    screen.blit(right_text, right_text.get_rect(center=right_arrow_rect.center))
    
    return left_arrow_rect, right_arrow_rect

# Main game loop
clock = pygame.time.Clock()
last_time = time.time()

# Keyboard hotkey tracking
last_ctrl_x_press = 0
last_ctrl_z_press = 0
last_ctrl_c_press = 0

# Set window to be click-through by default
click_through = True

running = True
while running:
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    
    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_clicked = True
    
    # Check for Ctrl+X to start/stop hunt timer
    if keyboard.is_pressed('ctrl') and keyboard.is_pressed('x'):
        if current_time - last_ctrl_x_press > 0.5:  # Debounce
            last_ctrl_x_press = current_time
            if hunt_active:
                hunt_active = False
            else:
                hunt_active = True
                hunt_start_time = current_time
                hunt_duration = HUNT_DURATIONS[current_difficulty][current_map_size]
    
    # Check for Ctrl+C to start/stop smudge timer
    if keyboard.is_pressed('ctrl') and keyboard.is_pressed('c'):
        if current_time - last_ctrl_c_press > 0.5:  # Debounce
            last_ctrl_c_press = current_time
            if smudge_active:
                smudge_active = False
                smudge_reached_max = False
            else:
                smudge_active = True
                smudge_start_time = current_time
                smudge_reached_max = False
    
    # Check for Ctrl+Z to show/hide config
    if keyboard.is_pressed('ctrl') and keyboard.is_pressed('z'):
        if current_time - last_ctrl_z_press > 0.5:  # Debounce
            last_ctrl_z_press = current_time
            show_config = not show_config
            
            if show_config:
                # Make window clickable when showing config
                click_through = False
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                      win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & 
                                      ~win32con.WS_EX_TRANSPARENT)
                
                # Initialize temp values
                temp_map_size = current_map_size
                temp_difficulty = current_difficulty
            else:
                # Make window click-through when hiding config
                click_through = True
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                      win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | 
                                      win32con.WS_EX_TRANSPARENT)
    
    # Check if in recovery period
    if in_recovery:
        recovery_elapsed = current_time - recovery_start_time
        if recovery_elapsed >= RECOVERY_PERIOD:
            in_recovery = False
            stamina = MAX_STAMINA
    else:
        # Check if shift is pressed AND a movement key is pressed (sprinting)
        is_sprinting = keyboard.is_pressed('shift') and (
            keyboard.is_pressed('w') or 
            keyboard.is_pressed('a') or 
            keyboard.is_pressed('s') or 
            keyboard.is_pressed('d')
        )
        
        if is_sprinting:
            stamina -= SPRINT_DEPLETION_RATE * dt
            was_sprinting = True
            last_sprint_time = current_time
            
            if stamina <= 0:
                stamina = 0
                in_recovery = True
                recovery_start_time = current_time
        else:
            # If we just stopped sprinting, record the time
            if was_sprinting:
                regen_start_time = current_time
                was_sprinting = False
            
            # Calculate time since stopped sprinting
            time_since_sprint_stopped = current_time - regen_start_time
            
            # Only regenerate if we're past the delay period
            if stamina < MAX_STAMINA and time_since_sprint_stopped > REGEN_DELAY:
                # Calculate time into the ramp-up period
                ramp_time = time_since_sprint_stopped - REGEN_DELAY
                
                # Calculate ramp factor (0.0 to 1.0) based on time since regen started
                ramp_factor = min(ramp_time / REGEN_RAMP_TIME, 1.0)
                
                # Use a smooth easing function (ease-out quad)
                # This makes the acceleration feel more natural
                eased_factor = 1 - (1 - ramp_factor) * (1 - ramp_factor)
                
                # Calculate current regen rate (from MIN_REGEN_PERCENT to 100% of MAX_RECOVERY_RATE)
                current_regen_rate = MAX_RECOVERY_RATE * (MIN_REGEN_PERCENT + (1 - MIN_REGEN_PERCENT) * eased_factor)
                
                # Apply regeneration
                stamina += current_regen_rate * dt
                stamina = min(stamina, MAX_STAMINA)
    
    # Update hunt timer if active
    if hunt_active:
        hunt_elapsed = current_time - hunt_start_time
        hunt_remaining = max(0, hunt_duration - hunt_elapsed)
        
        if hunt_remaining <= 0:
            hunt_active = False
    
    # Update smudge timer if active
    if smudge_active:
        smudge_elapsed = current_time - smudge_start_time
        
        # Check if we've reached max time
        if smudge_elapsed >= MAX_SMUDGE_TIME and not smudge_reached_max:
            smudge_reached_max = True
            smudge_max_reached_time = current_time
        
        # Check if we should reset after showing "Likely Spirit" message
        if smudge_reached_max and current_time - smudge_max_reached_time >= SPIRIT_MESSAGE_DURATION:
            smudge_active = False
            smudge_reached_max = False
    
    # Clear screen with transparent background
    screen.fill(BACKGROUND)
    
    # Draw hunt timer if active or if config is shown
    if hunt_active or show_config:
        # Draw hunt timer background
        pygame.draw.rect(screen, BAR_BACKGROUND, (BAR_X, HUNT_BAR_Y, BAR_WIDTH, BAR_HEIGHT))
        
        if hunt_active:
            # Draw hunt timer progress
            hunt_progress = hunt_remaining / hunt_duration
            hunt_width = hunt_progress * BAR_WIDTH
            pygame.draw.rect(screen, RECOVERY_COLOR, (BAR_X, HUNT_BAR_Y, hunt_width, BAR_HEIGHT))
            
            # Draw border around the bar
            pygame.draw.rect(screen, TEXT_COLOR, (BAR_X, HUNT_BAR_Y, BAR_WIDTH, BAR_HEIGHT), 1)
            
            # Draw hunt timer text
            hunt_text = f"Hunt: {hunt_remaining:.1f}s"
            text_surface = font.render(hunt_text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HUNT_BAR_Y - 10))
            screen.blit(text_surface, text_rect)
        else:
            # Draw empty hunt timer with text
            pygame.draw.rect(screen, TEXT_COLOR, (BAR_X, HUNT_BAR_Y, BAR_WIDTH, BAR_HEIGHT), 1)
            hunt_text = f"Hunt: Ready ({HUNT_DURATIONS[current_difficulty][current_map_size]}s)"
            text_surface = font.render(hunt_text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HUNT_BAR_Y - 10))
            screen.blit(text_surface, text_rect)
    
    # Draw stamina bar background
    pygame.draw.rect(screen, BAR_BACKGROUND, (BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT))
    
    # Draw stamina bar
    if in_recovery:
        # Calculate recovery progress (0 to 1)
        recovery_progress = (current_time - recovery_start_time) / RECOVERY_PERIOD
        recovery_width = recovery_progress * BAR_WIDTH
        pygame.draw.rect(screen, RECOVERY_COLOR, (BAR_X, BAR_Y, recovery_width, BAR_HEIGHT))
    else:
        # Normal stamina bar
        stamina_width = (stamina / MAX_STAMINA) * BAR_WIDTH
        
        # Determine bar color based on state
        bar_color = STAMINA_COLOR
        
        if not was_sprinting:
            time_since_sprint_stopped = current_time - regen_start_time
            
            if time_since_sprint_stopped <= REGEN_DELAY:
                # In delay period
                bar_color = DELAY_COLOR
            elif time_since_sprint_stopped <= REGEN_DELAY + REGEN_RAMP_TIME:
                # In ramp-up period
                bar_color = RAMPING_COLOR
        
        pygame.draw.rect(screen, bar_color, (BAR_X, BAR_Y, stamina_width, BAR_HEIGHT))
    
    # Draw border around the bar
    pygame.draw.rect(screen, TEXT_COLOR, (BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT), 1)
    
    # Draw stamina percentage text
    if in_recovery:
        time_left = RECOVERY_PERIOD - (current_time - recovery_start_time)
        stamina_text = f"RECOVERY: {time_left:.1f}s"
    elif not was_sprinting:
        time_since_sprint_stopped = current_time - regen_start_time
        
        if time_since_sprint_stopped <= REGEN_DELAY:
            # In delay period
            delay_left = REGEN_DELAY - time_since_sprint_stopped
            stamina_text = f"Stamina: {stamina:.1f}% (Delay: {delay_left:.1f}s)"
        elif time_since_sprint_stopped <= REGEN_DELAY + REGEN_RAMP_TIME:
            # In ramp-up period
            ramp_time = time_since_sprint_stopped - REGEN_DELAY
            ramp_percent = min(ramp_time / REGEN_RAMP_TIME * 100, 100)
            stamina_text = f"Stamina: {stamina:.1f}% (Ramp: {ramp_percent:.0f}%)"
        else:
            stamina_text = f"Stamina: {stamina:.1f}%"
    else:
        stamina_text = f"Stamina: {stamina:.1f}%"
    
    text_surface = font.render(stamina_text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, BAR_Y + BAR_HEIGHT + 10))
    screen.blit(text_surface, text_rect)
    
    # Draw smudge timer
    if smudge_active:
        if smudge_reached_max:
            # Show "Likely Spirit" message
            smudge_text = "Smudge Timer: LIKELY SPIRIT"
            text_surface = font_large.render(smudge_text, True, SPIRIT_COLOR)
        else:
            smudge_elapsed = current_time - smudge_start_time
            smudge_elapsed = min(smudge_elapsed, MAX_SMUDGE_TIME)
            
            # Draw smudge timer text with larger font
            smudge_text = f"Smudge Timer: {smudge_elapsed:.1f}s"
            
            # Add ghost type hints based on elapsed time
            if smudge_elapsed >= 60:
                if smudge_elapsed < 90:
                    smudge_text += " (Demon?)"
                elif smudge_elapsed < 180:
                    smudge_text += " (Not Spirit)"
            
            text_surface = font_large.render(smudge_text, True, SMUDGE_COLOR)
        
        text_rect = text_surface.get_rect(center=(WIDTH // 2, SMUDGE_TIMER_Y))
        screen.blit(text_surface, text_rect)
    else:
        # Draw inactive smudge timer text
        smudge_text = "Smudge Timer: Ready (Ctrl+C)"
        text_surface = font_large.render(smudge_text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, SMUDGE_TIMER_Y))
        screen.blit(text_surface, text_rect)
    
    # Draw configuration UI if showing
    if show_config:
        # Draw a dark background panel for the entire config area
        config_panel_rect = pygame.Rect(10, 5, WIDTH - 20, HEIGHT - 15)
        panel_surface = pygame.Surface((config_panel_rect.width, config_panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill(CONFIG_PANEL_BG)
        screen.blit(panel_surface, config_panel_rect)
        
        # Draw a title for the config panel
        config_title = font_large.render("Hunt Timer Settings", True, TEXT_COLOR)
        title_rect = config_title.get_rect(center=(WIDTH // 2, 10))
        screen.blit(config_title, title_rect)
        
        # Draw map size carousel
        map_left_arrow, map_right_arrow = draw_carousel(
            map_sizes, temp_map_size, map_carousel_x, map_carousel_y, 
            carousel_width, carousel_height, mouse_pos
        )
        
        # Draw difficulty carousel
        diff_left_arrow, diff_right_arrow = draw_carousel(
            difficulties, temp_difficulty, diff_carousel_x, diff_carousel_y, 
            carousel_width, carousel_height, mouse_pos
        )
        
        # Draw save button
        save_button_rect = draw_button("Save", button_x, button_y, button_width, button_height, mouse_pos)
        
        # Draw labels with larger font
        map_label = font_medium.render("Map Size:", True, TEXT_COLOR)
        diff_label = font_medium.render("Difficulty:", True, TEXT_COLOR)
        screen.blit(map_label, (map_carousel_x - 49, map_carousel_y + 3))  # Adjusted position for alignment
        screen.blit(diff_label, (diff_carousel_x - 49, diff_carousel_y + 3))  # Adjusted position for alignment
        
        # Draw hunt duration preview
        preview_duration = HUNT_DURATIONS[temp_difficulty][temp_map_size]
        preview_text = f"Hunt Duration: {preview_duration}s"
        preview_surface = font_medium.render(preview_text, True, TEXT_COLOR)
        preview_rect = preview_surface.get_rect(center=(WIDTH // 2, button_y - 15))
        screen.blit(preview_surface, preview_rect)
        
        # Handle clicks
        if mouse_clicked:
            # Map size carousel
            if is_mouse_over_rect(mouse_pos, map_left_arrow):
                current_index = map_sizes.index(temp_map_size)
                temp_map_size = map_sizes[(current_index - 1) % len(map_sizes)]
            elif is_mouse_over_rect(mouse_pos, map_right_arrow):
                current_index = map_sizes.index(temp_map_size)
                temp_map_size = map_sizes[(current_index + 1) % len(map_sizes)]
            
            # Difficulty carousel
            if is_mouse_over_rect(mouse_pos, diff_left_arrow):
                current_index = difficulties.index(temp_difficulty)
                temp_difficulty = difficulties[(current_index - 1) % len(difficulties)]
            elif is_mouse_over_rect(mouse_pos, diff_right_arrow):
                current_index = difficulties.index(temp_difficulty)
                temp_difficulty = difficulties[(current_index + 1) % len(difficulties)]
            
            # Save button
            if is_mouse_over_rect(mouse_pos, save_button_rect):
                current_map_size = temp_map_size
                current_difficulty = temp_difficulty
                hunt_duration = HUNT_DURATIONS[current_difficulty][current_map_size]
                
                # Hide config after saving
                show_config = False
                click_through = True
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                      win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | 
                                      win32con.WS_EX_TRANSPARENT)
    
    # Update display
    pygame.display.flip()
    
    # Cap at 60 FPS
    clock.tick(60)

pygame.quit()
sys.exit()

##Version 1.5 created by UndeadWolf 3/20/2025 - Calibrated for Phasmophobia v0.12.0.2 ##
