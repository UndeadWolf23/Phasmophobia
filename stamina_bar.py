## created by UndeadWolf 3/14/2025 - Calibrated for Phasmophobia v0.12.0.2 ##
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

# Get screen resolution
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

# Constants - smaller size
WIDTH, HEIGHT = 200, 60
BAR_WIDTH = 180
BAR_HEIGHT = 20
BAR_X = (WIDTH - BAR_WIDTH) // 2
BAR_Y = (HEIGHT - BAR_HEIGHT) // 2

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

# Create the window with transparency
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME | pygame.SRCALPHA)
pygame.display.set_caption("Phasmophobia Stamina Meter")

# Set window to be always on top and positioned at bottom right
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, WINDOW_X, WINDOW_Y, WIDTH, HEIGHT, 0)

# Make the window click-through
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                      win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | 
                      win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)

# Font - smaller size
font = pygame.font.SysFont('Arial', 12)

# Stamina state
stamina = MAX_STAMINA
in_recovery = False
recovery_start_time = 0
last_sprint_time = 0
was_sprinting = False
regen_start_time = 0

# Main game loop
clock = pygame.time.Clock()
last_time = time.time()

running = True
while running:
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Check if in recovery period
    if in_recovery:
        recovery_elapsed = current_time - recovery_start_time
        if recovery_elapsed >= RECOVERY_PERIOD:
            in_recovery = False
            stamina = MAX_STAMINA
    else:
        # Check if shift is pressed (sprinting)
        is_sprinting = keyboard.is_pressed('shift')
        
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
    
    # Clear screen with transparent background
    screen.fill(BACKGROUND)
    
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
    
    # Update display
    pygame.display.flip()
    
    # Cap at 60 FPS
    clock.tick(60)

pygame.quit()
sys.exit()

## created by UndeadWolf 3/14/2025 - Calibrated for Phasmophobia v0.12.0.2 ##