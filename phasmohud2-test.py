## version 1.7 - created by UndeadWolf23 3/27/2025 - Calibrated for Phasmophobia v0.12.0.2 ##

import pygame, sys, time, keyboard, win32gui, win32con, ctypes, math, os, configparser
import tkinter as tk
from tkinter import ttk, messagebox

# Initialize pygame
pygame.init()

# Get screen resolution
user32 = ctypes.windll.user32
screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# Default settings
DEFAULT_SETTINGS = {
    'General': {
        'ui_scale': '1.0',
        'position': 'bottom_right',
        'map_size': 'Small',
        'difficulty': 'Pro+',
        'show_footstep_pattern': 'True'
    },
    'Hotkeys': {
        'settings_key': 'ctrl+z',
        'hunt_timer_key': 'ctrl+x',
        'smudge_timer_key': 'ctrl+c',
        'evidence_tracker_key': 'ctrl+v'
    }
}

# Hunt durations in seconds based on map size and difficulty
HUNT_DURATIONS = {
    "Amateur": {"Small": 15, "Medium": 30, "Large": 40},
    "Intermediate": {"Small": 20, "Medium": 40, "Large": 50},
    "Pro+": {"Small": 30, "Medium": 50, "Large": 60}
}

# Evidence data
EVIDENCES = ["Freezing Temps", "UV", "Spirit Box", "Ghost Writing", "EMF 5", "Orbs", "D.O.T.S"]

# Ghost types and their evidences
GHOST_TYPES = {
    "Spirit": ["EMF 5", "Spirit Box", "Ghost Writing"],
    "Wraith": ["EMF 5", "Spirit Box", "D.O.T.S"],
    "Phantom": ["Spirit Box", "UV", "D.O.T.S"],
    "Poltergeist": ["Spirit Box", "UV", "Ghost Writing"],
    "Banshee": ["UV", "Orbs", "D.O.T.S"],
    "Jinn": ["EMF 5", "UV", "Freezing Temps"],
    "Mare": ["Spirit Box", "Orbs", "Ghost Writing"],
    "Revenant": ["Orbs", "Ghost Writing", "Freezing Temps"],
    "Shade": ["EMF 5", "Ghost Writing", "Freezing Temps"],
    "Demon": ["UV", "Ghost Writing", "Freezing Temps"],
    "Yurei": ["Orbs", "Freezing Temps", "D.O.T.S"],
    "Oni": ["EMF 5", "Freezing Temps", "D.O.T.S"],
    "Yokai": ["Spirit Box", "Orbs", "D.O.T.S"],
    "Hantu": ["UV", "Orbs", "Freezing Temps"],
    "Goryo": ["EMF 5", "UV", "D.O.T.S"],
    "Myling": ["EMF 5", "UV", "Ghost Writing"],
    "Onryo": ["Spirit Box", "Orbs", "Freezing Temps"],
    "The Twins": ["EMF 5", "Spirit Box", "Freezing Temps"],
    "Raiju": ["EMF 5", "Orbs", "D.O.T.S"],
    "Obake": ["EMF 5", "UV", "Orbs"],
    "The Mimic": ["Spirit Box", "UV", "Freezing Temps"],  # Special case: always has Orbs
    "Moroi": ["Spirit Box", "Ghost Writing", "Freezing Temps"],
    "Deogen": ["Spirit Box", "Ghost Writing", "D.O.T.S"],
    "Thaye": ["Orbs", "Ghost Writing", "D.O.T.S"]
}

# Special options and their effects on ghost types
SPECIAL_OPTIONS = {
    "Fast Footsteps": {"only": ["Jinn", "Revenant", "Hantu", "The Twins", "Raiju", "The Mimic", "Moroi", "Thaye"]},
    "Slow Footsteps": {"only": ["Revenant", "Hantu", "The Twins", "The Mimic", "Thaye"]},
    "Normal Footsteps": {"eliminate": ["Hantu", "Moroi", "Revenant", "Deogen", "The Twins", "Thaye"]},
    "Turned Off Breaker": {"eliminate": ["Jinn"]},
    "Turned On Breaker": {"eliminate": ["Hantu"]},
    "Turned On Light": {"eliminate": ["Mare"]},
    "Slammed Door": {"only": ["Yurei", "The Mimic"]},
    "Rapid Blink": {"only": ["Oni", "The Mimic"]},
    "Slow Blinks": {"only": ["Phantom", "The Mimic"]},
    "Shapeshift Blink": {"only": ["Obake", "The Mimic"]},
    "Special UV Prints": {"only": ["Obake", "The Mimic"]},
    "Did Airball Event": {"eliminate": ["Oni"]},
    "Parabolic Scream": {"only": ["Wraith", "The Mimic"]},
    "Invisible Ghost Photo": {"only": ["Phantom", "The Mimic"]},
    "Dumb": {"only": ["Yokai", "The Mimic"]},
    "Cam Only D.O.T.S": {"only": ["Goryo", "The Mimic"]},
    "Quiet": {"only": ["Myling", "The Mimic"]},
    "No Salt Steps": {"only": ["Wraith", "The Mimic"]},
    "No LoS": {"only": ["Thaye", "Deogen", "Hantu", "The Mimic"]},
    "No Room Change": {"only": ["Banshee", "Goryo"]},
    "Powerful Throw": {"only": ["Poltergeist", "The Mimic"]},
    "Can't Hide": {"only": ["Deogen", "The Mimic"]},
    "Spirit Box Growl": {"only": ["Deogen", "The Mimic"]},
    "Short Smudge": {"only": ["Demon", "The Mimic"]},
    "Long Smudge": {"only": ["Spirit"]}
}

# Special behaviors and their effects on ghost probabilities
SPECIAL_BEHAVIORS = {
    "Inconsistent": {"high_favor": ["The Mimic"], "some_favor": ["Thaye"]},
    "Changing Speed": {
        "high_favor": ["The Twins", "The Mimic"],
        "some_favor": ["Moroi", "Raiju"],
        "little_favor": ["Revenant", "Jinn", "Deogen"]
    },
    "Active": {
        "high_favor": ["Thaye"],
        "some_favor": ["The Twins"],
        "much_disfavor": ["Shade"]
    },
    "Passive": {
        "high_favor": ["Shade"],
        "some_disfavor": ["The Twins", "Thaye"]
    },
    "High Sanity Hunt": {
        "high_favor": ["Demon", "Thaye"],
        "some_favor": ["Raiju", "Onryo"],
        "some_disfavor": ["Deogen", "Shade"]
    },
    "Frequent Breaker": {"high_favor": ["Hantu"]},
    "Frequent Airball/Shadow": {"some_favor": ["Phantom", "Shade"]},
    "Targeted Wandering": {"high_favor": ["Banshee"]},
    "Frequent Singing": {"some_favor": ["Banshee"]},
    "Frequent Light Shatter": {"some_favor": ["Mare"]},
    "Frequent Para Whisper": {"some_favor": ["Myling"]},
    "Low Roaming": {
        "some_favor": ["Goryo"],
        "some_disfavor": ["Banshee", "Wraith"]
    },
    "High Sanity Drain": {
        "high_favor": ["Oni", "Yurei"],
        "some_favor": ["Moroi"],
        "little_favor": ["Phantom", "Yokai"],
        "some_disfavor": ["Shade"]
    },
    "Frequent Hunts": {
        "high_favor": ["Demon"],
        "little_favor": ["Thaye", "Yokai", "Raiju"],
        "some_disfavor": ["Shade"]
    },
    "Distant Interactions": {
        "high_favor": ["The Twins"],
        "some_favor": ["Banshee", "Wraith"],
        "much_disfavor": ["Goryo"]
    }
}

# Impossible evidence combinations
IMPOSSIBLE_COMBINATIONS = [
    ['UV', 'Spirit Box', 'Orbs'],
    ['UV', 'Spirit Box', 'EMF 5'],
    ['UV', 'Orbs', 'Ghost Writing'],
    ['UV', 'Freezing Temps', 'D.O.T.S'],
    ['UV', 'D.O.T.S', 'Ghost Writing'],
    ['Spirit Box', 'Orbs', 'EMF 5'],
    ['Spirit Box', 'Freezing Temps', 'D.O.T.S'],
    ['Orbs', 'Freezing Temps', 'EMF 5'],
    ['Orbs', 'Ghost Writing', 'EMF 5'],
    ['Freezing Temps', 'D.O.T.S', 'Ghost Writing'],
    ['D.O.T.S', 'Ghost Writing', 'EMF 5']
]

# Settings file path
def get_settings_path():
    application_path = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
    return os.path.join(application_path, 'settings.ini')

# Function to load settings
def load_settings():
    config = configparser.ConfigParser()
    settings_path = get_settings_path()
    
    # Load default settings
    for section, options in DEFAULT_SETTINGS.items():
        if not config.has_section(section):
            config.add_section(section)
        for key, value in options.items():
            config.set(section, key, value)
    
    # Override with saved settings if file exists
    if os.path.exists(settings_path):
        config.read(settings_path)
    else:
        # Create the file with default settings
        save_settings(config)
    
    return config

# Function to save settings
def save_settings(config):
    with open(get_settings_path(), 'w') as configfile:
        config.write(configfile)

# Settings window class
class SettingsWindow:
    def __init__(self, parent_hwnd, current_settings, callback):
        self.root = tk.Tk()
        self.root.title("Phasmophobia HUD Settings")
        self.root.geometry("600x800")
        self.root.resizable(False, False)
        
        self.settings = current_settings
        self.callback = callback
        self.parent_hwnd = parent_hwnd
        
        # Make this window stay on top of the game
        self.root.attributes("-topmost", True)
        
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.general_tab = ttk.Frame(self.notebook)
        self.hotkeys_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.general_tab, text="General Settings")
        self.notebook.add(self.hotkeys_tab, text="Hotkeys")
        
        # Setup the UI elements
        self.setup_general_tab()
        self.setup_hotkeys_tab()
        
        # Add save and cancel buttons at the bottom
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(self.button_frame, text="Save", command=self.save_settings).pack(side='right', padx=5)
        ttk.Button(self.button_frame, text="Cancel", command=self.cancel).pack(side='right', padx=5)
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # Center the window on screen
        self.center_window()
    
    def center_window(self):
        self.root.update_idletasks()
        width, height = self.root.winfo_width(), self.root.winfo_height()
        x, y = (screen_width - width) // 2, (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_general_tab(self):
        # Create a frame with padding
        frame = ttk.LabelFrame(self.general_tab, text="Display Settings")
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # UI Scale
        ttk.Label(frame, text="UI Scale:").grid(row=0, column=0, sticky='w', padx=10, pady=10)
        self.scale_var = tk.StringVar(value=self.settings.get('General', 'ui_scale'))
        scale_combo = ttk.Combobox(frame, textvariable=self.scale_var, width=10, values=('0.75', '1.0', '1.25', '1.5', '1.75', '2.0'))
        scale_combo.grid(row=0, column=1, sticky='w', padx=10, pady=10)
        
        # UI Position
        ttk.Label(frame, text="UI Position:").grid(row=1, column=0, sticky='w', padx=10, pady=10)
        self.position_var = tk.StringVar(value=self.settings.get('General', 'position'))
        position_combo = ttk.Combobox(frame, textvariable=self.position_var, width=15, 
                                      values=('top_left', 'top_right', 'bottom_left', 'bottom_right'))
        position_combo.grid(row=1, column=1, sticky='w', padx=10, pady=10)
        
        # Hunt Timer Settings
        hunt_frame = ttk.LabelFrame(self.general_tab, text="Hunt Timer Settings")
        hunt_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Map Size
        ttk.Label(hunt_frame, text="Map Size:").grid(row=0, column=0, sticky='w', padx=10, pady=10)
        self.map_size_var = tk.StringVar(value=self.settings.get('General', 'map_size'))
        map_combo = ttk.Combobox(hunt_frame, textvariable=self.map_size_var, width=10, values=('Small', 'Medium', 'Large'))
        map_combo.grid(row=0, column=1, sticky='w', padx=10, pady=10)
        
        # Difficulty
        ttk.Label(hunt_frame, text="Difficulty:").grid(row=1, column=0, sticky='w', padx=10, pady=10)
        self.difficulty_var = tk.StringVar(value=self.settings.get('General', 'difficulty'))
        diff_combo = ttk.Combobox(hunt_frame, textvariable=self.difficulty_var, width=15, values=('Amateur', 'Intermediate', 'Pro+'))
        diff_combo.grid(row=1, column=1, sticky='w', padx=10, pady=10)
        
        # Show Footstep Pattern
        self.footstep_var = tk.BooleanVar(value=self.settings.get('General', 'show_footstep_pattern').lower() == 'true')
        ttk.Checkbutton(hunt_frame, text="Show Footstep Pattern", variable=self.footstep_var).grid(
            row=2, column=0, columnspan=2, sticky='w', padx=10, pady=10)
        
        # Hunt Duration Preview
        self.hunt_duration_label = ttk.Label(hunt_frame, text="")
        self.hunt_duration_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        
        # Update hunt duration when map size or difficulty changes
        map_combo.bind("<<ComboboxSelected>>", self.update_hunt_duration)
        diff_combo.bind("<<ComboboxSelected>>", self.update_hunt_duration)
        
        # Initial update
        self.update_hunt_duration(None)
    
    def update_hunt_duration(self, event):
        map_size = self.map_size_var.get()
        difficulty = self.difficulty_var.get()
        
        if map_size in HUNT_DURATIONS.get(difficulty, {}):
            duration = HUNT_DURATIONS[difficulty][map_size]
            self.hunt_duration_label.config(text=f"Hunt Duration: {duration} seconds")
        else:
            self.hunt_duration_label.config(text="Invalid map size or difficulty")
    
    def setup_hotkeys_tab(self):
        frame = ttk.LabelFrame(self.hotkeys_tab, text="Keyboard Shortcuts")
        frame.pack(fill='both', expand=True, padx=10, pady=10)
            
        # Settings hotkey
        ttk.Label(frame, text="Open Settings:").grid(row=0, column=0, sticky='w', padx=10, pady=10)
        self.settings_key_var = tk.StringVar(value=self.settings.get('Hotkeys', 'settings_key'))
        settings_entry = ttk.Entry(frame, textvariable=self.settings_key_var, width=15)
        settings_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)
        ttk.Label(frame, text="(Type key directly)").grid(row=0, column=2, padx=5, pady=10)
            
        # Hunt timer hotkey
        ttk.Label(frame, text="Hunt Timer:").grid(row=1, column=0, sticky='w', padx=10, pady=10)
        self.hunt_key_var = tk.StringVar(value=self.settings.get('Hotkeys', 'hunt_timer_key'))
        hunt_entry = ttk.Entry(frame, textvariable=self.hunt_key_var, width=15)
        hunt_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)
        ttk.Label(frame, text="(Type key directly)").grid(row=1, column=2, padx=5, pady=10)
            
        # Smudge timer hotkey
        ttk.Label(frame, text="Smudge Timer:").grid(row=2, column=0, sticky='w', padx=10, pady=10)
        self.smudge_key_var = tk.StringVar(value=self.settings.get('Hotkeys', 'smudge_timer_key'))
        smudge_entry = ttk.Entry(frame, textvariable=self.smudge_key_var, width=15)
        smudge_entry.grid(row=2, column=1, sticky='w', padx=10, pady=10)
        ttk.Label(frame, text="(Type key directly)").grid(row=2, column=2, padx=5, pady=10)
            
        # Evidence tracker hotkey
        ttk.Label(frame, text="Evidence Tracker:").grid(row=3, column=0, sticky='w', padx=10, pady=10)
        self.evidence_key_var = tk.StringVar(value=self.settings.get('Hotkeys', 'evidence_tracker_key'))
        evidence_entry = ttk.Entry(frame, textvariable=self.evidence_key_var, width=15)
        evidence_entry.grid(row=3, column=1, sticky='w', padx=10, pady=10)
        ttk.Label(frame, text="(Type key directly)").grid(row=3, column=2, padx=5, pady=10)
            
        # Instructions
        instructions = (
            "Type the key name directly in the entry fields.\n"
            "Examples: f1, f2, home, end, insert, delete, page_up, page_down\n"
            "For letters and numbers, just type the character: a, b, c, 1, 2, 3\n\n"
            "Note: Some key combinations may be reserved by Windows or other applications."
        )
        ttk.Label(frame, text=instructions, wraplength=500, justify='left').grid(
            row=4, column=0, columnspan=3, sticky='w', padx=10, pady=20)     
    
    def save_settings(self):
        # Update the settings
        self.settings.set('General', 'ui_scale', self.scale_var.get())
        self.settings.set('General', 'position', self.position_var.get())
        self.settings.set('General', 'map_size', self.map_size_var.get())
        self.settings.set('General', 'difficulty', self.difficulty_var.get())
        self.settings.set('General', 'show_footstep_pattern', str(self.footstep_var.get()))
        
        self.settings.set('Hotkeys', 'evidence_tracker_key', self.evidence_key_var.get())
        self.settings.set('Hotkeys', 'settings_key', self.settings_key_var.get())
        self.settings.set('Hotkeys', 'hunt_timer_key', self.hunt_key_var.get())
        self.settings.set('Hotkeys', 'smudge_timer_key', self.smudge_key_var.get())
        
        # Save to file
        save_settings(self.settings)
        
        # Call the callback function to update the main application
        self.callback(self.settings)
        
        # Close the window
        self.root.destroy()
    
    def cancel(self):
        # Close without saving
        self.root.destroy()
    
    def run(self):
        # Start the Tkinter main loop
        self.root.mainloop()

# Set application icon - using path relative to the executable
def load_app_icon():
    try:
        application_path = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
        icon_path = os.path.join(application_path, '_internal', 'phasmo_hud_icon.png')
        app_icon = pygame.image.load(icon_path)
        print(f"Successfully loaded icon from: {icon_path}")
        return app_icon
    except Exception as e:
        print(f"Could not load icon file: {e}. Using default icon.")
        return None

# Load settings and set up initial values
config = load_settings()

# Constants and scaling
ui_scale = float(config.get('General', 'ui_scale'))
BASE_WIDTH, BASE_HEIGHT = 250, 180
BASE_BAR_WIDTH, BASE_BAR_HEIGHT = 220, 24
BASE_FONT_SIZES = {
    'small': 12,
    'normal': 14,
    'medium': 15,
    'large': 16
}

# Apply UI scale
WIDTH, HEIGHT = int(BASE_WIDTH * ui_scale), int(BASE_HEIGHT * ui_scale)
BAR_WIDTH, BAR_HEIGHT = int(BASE_BAR_WIDTH * ui_scale), int(BASE_BAR_HEIGHT * ui_scale)
BAR_X, BAR_Y = (WIDTH - BAR_WIDTH) // 2, (HEIGHT - BAR_HEIGHT) // 2
HUNT_BAR_Y = BAR_Y - int(35 * ui_scale)
SMUDGE_TIMER_Y = BAR_Y + int(60 * ui_scale)

# Footstep pattern helper constants
FOOTSTEP_Y = HUNT_BAR_Y - int(25 * ui_scale)
FOOTSTEP_SIZE = int(10 * ui_scale)
FOOTSTEP_COLOR = (200, 200, 255)
FOOTSTEP_HIGHLIGHT_COLOR = (255, 255, 255)
FOOTSTEP_STEP_INTERVAL = 0.5

# Position based on settings
position = config.get('General', 'position')
position_map = {
    'top_left': (10, 10),
    'top_right': (screen_width - WIDTH - 10, 10),
    'bottom_left': (10, screen_height - HEIGHT - 10),
    'bottom_right': (screen_width - WIDTH - 10, screen_height - HEIGHT - 10)
}
WINDOW_X, WINDOW_Y = position_map.get(position, position_map['bottom_right'])

# Colors
BACKGROUND = (20, 20, 20, 180)
BAR_BACKGROUND = (50, 50, 50)
STAMINA_COLOR = (0, 255, 0)
RECOVERY_COLOR = (255, 0, 0)
DELAY_COLOR = (255, 100, 100)
RAMPING_COLOR = (255, 165, 0)
TEXT_COLOR = (255, 255, 255)
SMUDGE_COLOR = (100, 100, 255)
SPIRIT_COLOR = (255, 255, 0)

# Stamina mechanics
MAX_STAMINA = 100
SPRINT_DEPLETION_RATE = MAX_STAMINA / 3  # Sprint depletes 100% stamina in 3 seconds
MAX_RECOVERY_RATE = MAX_STAMINA * 0.35  # Maximum regeneration rate (35% stamina per second)
RECOVERY_PERIOD = 5  # Full recovery period when stamina is depleted (seconds)
REGEN_DELAY = 1.35  # Delay before regeneration begins after stopping sprint (seconds)
REGEN_RAMP_TIME = 2.75  # Time it takes for regeneration to reach full speed after delay
MIN_REGEN_PERCENT = 0.1  # Minimum regeneration rate as a percentage of max rate

# Smudge timer settings
MAX_SMUDGE_TIME = 180  # Maximum time to display (Spirit - 180s)
SPIRIT_MESSAGE_DURATION = 3  # Duration to show "Likely Spirit" message

# Evidence Tracker UI Constants
TRACKER_WIDTH = 1300
TRACKER_HEIGHT = 800
TRACKER_X = (screen_width - TRACKER_WIDTH) // 2
TRACKER_Y = (screen_height - TRACKER_HEIGHT) // 2

# Colors for evidence tracker
EVIDENCE_BG = (30, 30, 40, 220)
EVIDENCE_BORDER = (100, 100, 120)
EVIDENCE_SELECTED = (0, 200, 0)
EVIDENCE_ELIMINATED = (200, 0, 0)
EVIDENCE_TEXT = (220, 220, 220)
GHOST_ELIMINATED = (80, 80, 80)
GHOST_POSSIBLE = (220, 220, 220)
GHOST_LIKELY = (150, 255, 150)
GHOST_VERY_LIKELY = (50, 255, 50)
GHOST_UNLIKELY = (255, 150, 150)
GHOST_VERY_UNLIKELY = (255, 50, 50)

# Section dimensions
SECTION_PADDING = int(10 * ui_scale)
SECTION_A_HEIGHT = int(80 * ui_scale)  # Evidence section - reduced height
SECTION_B_HEIGHT = int(250 * ui_scale)  # Ghost types section
SECTION_C_HEIGHT = int(165 * ui_scale)  # Special options
SECTION_D_HEIGHT = int(150 * ui_scale)  # Special behaviors

# Button dimensions
EVIDENCE_BTN_WIDTH = int(150 * ui_scale)
EVIDENCE_BTN_HEIGHT = int(40 * ui_scale)
GHOST_BTN_WIDTH = int(180 * ui_scale)
GHOST_BTN_HEIGHT = int(30 * ui_scale)
SPECIAL_BTN_WIDTH = int(220 * ui_scale)  # Increased width for longer text
SPECIAL_BTN_HEIGHT = int(30 * ui_scale)
RESET_BTN_WIDTH = int(120 * ui_scale)
RESET_BTN_HEIGHT = int(40 * ui_scale)

# Load settings
current_map_size = config.get('General', 'map_size')
current_difficulty = config.get('General', 'difficulty')
show_footstep_pattern = config.getboolean('General', 'show_footstep_pattern')
settings_key = config.get('Hotkeys', 'settings_key')
hunt_timer_key = config.get('Hotkeys', 'hunt_timer_key')
smudge_timer_key = config.get('Hotkeys', 'smudge_timer_key')
evidence_tracker_key = config.get('Hotkeys', 'evidence_tracker_key')
hunt_duration = HUNT_DURATIONS[current_difficulty][current_map_size]

# Create the window with transparency
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME | pygame.SRCALPHA)
pygame.display.set_caption("Phasmophobia Overlay")

# Load application icon
app_icon = load_app_icon()

# Set window to be always on top and positioned correctly
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, WINDOW_X, WINDOW_Y, WIDTH, HEIGHT, 0)

# Make sure it's really on top
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

# Make the window click-through
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                      win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | 
                      win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)

# Fonts - scaled based on UI scale
fonts = {}
for name, size in BASE_FONT_SIZES.items():
    fonts[name] = pygame.font.SysFont('Arial', int(size * ui_scale))

# State variables
stamina = MAX_STAMINA
in_recovery = False
recovery_start_time = 0
last_sprint_time = 0
was_sprinting = False
regen_start_time = 0
hunt_active = False
hunt_start_time = 0
smudge_active = False
smudge_start_time = 0
smudge_reached_max = False
smudge_max_reached_time = 0
settings_window_open = False
last_hotkey_press = {'settings': 0, 'hunt': 0, 'smudge': 0, 'evidence': 0}
# Evidence tracker state variables
evidence_tracker_active = False
selected_evidence = {"positive": set(), "negative": set()}
selected_special_options = set()
selected_special_behaviors = set()
ghost_probabilities = {ghost: 1.0 for ghost in GHOST_TYPES}  # Default probability

# Button class for evidence tracker UI
class Button:
    def __init__(self, x, y, width, height, text, font, type="evidence", ghost_type=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.type = type  # evidence, ghost, special_option, special_behavior, reset, close
        self.ghost_type = ghost_type
        self.state = "normal"  # normal, selected, eliminated
    
    def draw(self, surface, selected_evidence, selected_special_options, selected_special_behaviors, ghost_states):
        # Determine button colors based on state and type
        bg_color = EVIDENCE_BG
        border_color = EVIDENCE_BORDER
        text_color = EVIDENCE_TEXT
        
        if self.type == "evidence":
            if self.text in selected_evidence["positive"]:
                bg_color = EVIDENCE_SELECTED
                border_color = EVIDENCE_SELECTED
            elif self.text in selected_evidence["negative"]:
                bg_color = EVIDENCE_ELIMINATED
                border_color = EVIDENCE_ELIMINATED
                
        elif self.type == "ghost":
            if self.ghost_type in ghost_states["eliminated"]:
                bg_color = GHOST_ELIMINATED
                text_color = (150, 150, 150)
            elif self.ghost_type in ghost_states["confirmed"]:
                bg_color = GHOST_LIKELY
                border_color = EVIDENCE_SELECTED
                text_color = (0, 0, 0)
            else:
                # Apply probability coloring
                probability = ghost_states["probabilities"].get(self.ghost_type, 1.0)
                if probability > 1.5:
                    text_color = GHOST_VERY_LIKELY
                elif probability > 1.2:
                    text_color = GHOST_LIKELY
                elif probability < 0.5:
                    text_color = GHOST_UNLIKELY
                elif probability < 0.2:
                    text_color = GHOST_VERY_UNLIKELY
                    
        elif self.type in ["special_option", "special_behavior"]:
            if (self.type == "special_option" and self.text in selected_special_options) or \
               (self.type == "special_behavior" and self.text in selected_special_behaviors):
                bg_color = EVIDENCE_SELECTED
                border_color = EVIDENCE_SELECTED
                
        elif self.type == "reset":
            bg_color = (80, 30, 30)
            border_color = (150, 50, 50)
            
        elif self.type == "close":
            bg_color = (60, 30, 80)
            border_color = (120, 50, 150)
        
        # Draw button background
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 2)
        
        # Draw text
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Draw strikethrough for eliminated ghosts or evidence
        if (self.type == "ghost" and self.ghost_type in ghost_states["eliminated"]) or \
           (self.type == "evidence" and self.text in selected_evidence["negative"]):
            pygame.draw.line(surface, EVIDENCE_ELIMINATED,
                             (self.rect.left + 5, self.rect.centery),
                            (self.rect.right - 5, self.rect.centery), 2)
    
    def handle_click(self, pos, button, selected_evidence, selected_special_options, selected_special_behaviors):
        if self.rect.collidepoint(pos):
            if self.type == "evidence":
                # Left click (button 1) - select/deselect
                if button == 1:
                    if self.text in selected_evidence["positive"]:
                        selected_evidence["positive"].remove(self.text)
                    elif self.text in selected_evidence["negative"]:
                        # If it's currently eliminated, do nothing on left click
                        pass
                    else:
                        selected_evidence["positive"].add(self.text)
                        # Check for impossible combinations immediately
                        check_impossible_combinations(selected_evidence)
                
                # Right click (button 3) - eliminate/uneliminate
                elif button == 3:
                    if self.text in selected_evidence["negative"]:
                        selected_evidence["negative"].remove(self.text)
                    elif self.text in selected_evidence["positive"]:
                        # If it's currently selected, do nothing on right click
                        pass
                    else:
                        selected_evidence["negative"].add(self.text)
                        # Check for impossible combinations immediately
                        check_impossible_combinations(selected_evidence)
                
                return True
                
            elif self.type == "special_option":
                if button == 1:  # Only respond to left click
                    if self.text in selected_special_options:
                        selected_special_options.remove(self.text)
                    else:
                        selected_special_options.add(self.text)
                    return True
                
            elif self.type == "special_behavior":
                if button == 1:  # Only respond to left click
                    if self.text in selected_special_behaviors:
                        selected_special_behaviors.remove(self.text)
                    else:
                        selected_special_behaviors.add(self.text)
                    return True
                
            elif self.type == "reset":
                if button == 1:  # Only respond to left click
                    selected_evidence["positive"].clear()
                    selected_evidence["negative"].clear()
                    selected_special_options.clear()
                    selected_special_behaviors.clear()
                    return True
                
            elif self.type == "close":
                if button == 1:  # Only respond to left click
                    global evidence_tracker_active
                    evidence_tracker_active = False
                    return True
                
        return False

        
        
def create_evidence_tracker_ui():
    buttons = []
    
    # Calculate better spacing and layout
    evidence_btn_spacing = 10
    ghost_btn_spacing = 8
    special_btn_spacing = 8
    
    # Section A: Evidence buttons
    section_a_y = SECTION_PADDING
    evidence_per_row = 7  # Increased to fit all evidence in one row
    evidence_rows = math.ceil(len(EVIDENCES) / evidence_per_row)
    
    # Calculate evidence button width to fit all in one row
    evidence_width = min(EVIDENCE_BTN_WIDTH,
                         (TRACKER_WIDTH - (2 * SECTION_PADDING) - (evidence_per_row - 1) * evidence_btn_spacing) / evidence_per_row)
    
    for i, evidence in enumerate(EVIDENCES):
        row = i // evidence_per_row
        col = i % evidence_per_row
        x = SECTION_PADDING + (col * (evidence_width + evidence_btn_spacing))
        y = section_a_y + 35 + (row * (EVIDENCE_BTN_HEIGHT + 10))
        buttons.append(Button(x, y, evidence_width, EVIDENCE_BTN_HEIGHT, evidence, fonts['normal'], "evidence"))
    
    # Section B: Ghost types
    section_b_y = section_a_y + SECTION_A_HEIGHT + SECTION_PADDING
    ghost_cols = 6  # 6 columns for ghost types
    ghost_rows = math.ceil(len(GHOST_TYPES) / ghost_cols)
    
    # Calculate ghost button width to fit all columns
    ghost_width = min(GHOST_BTN_WIDTH,
                      (TRACKER_WIDTH - (2 * SECTION_PADDING) - (ghost_cols - 1) * ghost_btn_spacing) / ghost_cols)
    
    for i, ghost in enumerate(GHOST_TYPES.keys()):
        row = i // ghost_cols
        col = i % ghost_cols
        x = SECTION_PADDING + (col * (ghost_width + ghost_btn_spacing))
        y = section_b_y + 35 + (row * (GHOST_BTN_HEIGHT + 8))
        buttons.append(Button(x, y, ghost_width, GHOST_BTN_HEIGHT, ghost, fonts['normal'], "ghost", ghost))
    
    # Section C: Special options
    section_c_y = section_b_y + SECTION_B_HEIGHT + SECTION_PADDING
    special_cols = 5  # Reduced columns for better fit
    special_rows = math.ceil(len(SPECIAL_OPTIONS) / special_cols)
    
    # Calculate special option button width
    special_width = min(SPECIAL_BTN_WIDTH,
                        (TRACKER_WIDTH - (2 * SECTION_PADDING) - (special_cols - 1) * special_btn_spacing) / special_cols)
    
    for i, option in enumerate(SPECIAL_OPTIONS.keys()):
        row = i // special_cols
        col = i % special_cols
        x = SECTION_PADDING + (col * (special_width + special_btn_spacing))
        y = section_c_y + 35 + (row * (SPECIAL_BTN_HEIGHT + 8))
        buttons.append(Button(x, y, special_width, SPECIAL_BTN_HEIGHT, option, fonts['small'], "special_option"))
    
    # Section D: Special behaviors
    section_d_y = section_c_y + (special_rows * (SPECIAL_BTN_HEIGHT + 8)) + 70  # Adjust based on actual special options height
    behavior_cols = 5  # Reduced columns for better fit
    behavior_rows = math.ceil(len(SPECIAL_BEHAVIORS) / behavior_cols)
    
    # Calculate behavior button width
    behavior_width = min(SPECIAL_BTN_WIDTH,
                         (TRACKER_WIDTH - (2 * SECTION_PADDING) - (behavior_cols - 1) * special_btn_spacing) / behavior_cols)
    
    for i, behavior in enumerate(SPECIAL_BEHAVIORS.keys()):
        row = i // behavior_cols
        col = i % behavior_cols
        x = SECTION_PADDING + (col * (behavior_width + special_btn_spacing))
        y = section_d_y + 35 + (row * (SPECIAL_BTN_HEIGHT + 8))
        buttons.append(Button(x, y, behavior_width, SPECIAL_BTN_HEIGHT, behavior, fonts['small'], "special_behavior"))
    
    # Reset button - moved to top right corner
    reset_x = TRACKER_WIDTH - RESET_BTN_WIDTH - SECTION_PADDING
    reset_y = SECTION_PADDING
    buttons.append(Button(reset_x, reset_y, RESET_BTN_WIDTH, RESET_BTN_HEIGHT, "Reset", fonts['medium'], "reset"))
    
    # Close button - positioned right below reset button
    close_x = TRACKER_WIDTH - RESET_BTN_WIDTH - SECTION_PADDING
    close_y = SECTION_PADDING + RESET_BTN_HEIGHT + 10
    buttons.append(Button(close_x, close_y, RESET_BTN_WIDTH, RESET_BTN_HEIGHT, "Close", fonts['medium'], "close"))
    
    return buttons


def determine_ghost_states(selected_evidence, selected_special_options, selected_special_behaviors):
    ghost_states = {
        "eliminated": set(),
        "confirmed": set(),
        "probabilities": {ghost: 1.0 for ghost in GHOST_TYPES}
    }
    
    # Process evidence selections
    for ghost, evidences in GHOST_TYPES.items():
        # Check positive evidence
        for evidence in selected_evidence["positive"]:
            if evidence not in evidences:
                ghost_states["eliminated"].add(ghost)
                break
                
        # Check negative evidence
        for evidence in selected_evidence["negative"]:
            if evidence in evidences:
                ghost_states["eliminated"].add(ghost)
                break
    
    # Process special options
    for option in selected_special_options:
        if option in SPECIAL_OPTIONS:
            option_data = SPECIAL_OPTIONS[option]
            
            # Handle "only" constraints
            if "only" in option_data:
                for ghost in GHOST_TYPES:
                    if ghost not in option_data["only"] and ghost not in ghost_states["eliminated"]:
                        ghost_states["eliminated"].add(ghost)
            
            # Handle "eliminate" constraints
            if "eliminate" in option_data:
                for ghost in option_data["eliminate"]:
                    if ghost not in ghost_states["eliminated"]:
                        ghost_states["eliminated"].add(ghost)
    
    # Process special behaviors (probability adjustments)
    for behavior in selected_special_behaviors:
        if behavior in SPECIAL_BEHAVIORS:
            behavior_data = SPECIAL_BEHAVIORS[behavior]
            
            # Apply high favor (multiply by 2.0)
            if "high_favor" in behavior_data:
                for ghost in behavior_data["high_favor"]:
                    if ghost not in ghost_states["eliminated"]:
                        ghost_states["probabilities"][ghost] *= 2.0
            
            # Apply some favor (multiply by 1.5)
            if "some_favor" in behavior_data:
                for ghost in behavior_data["some_favor"]:
                    if ghost not in ghost_states["eliminated"]:
                        ghost_states["probabilities"][ghost] *= 1.5
            
            # Apply little favor (multiply by 1.2)
            if "little_favor" in behavior_data:
                for ghost in behavior_data["little_favor"]:
                    if ghost not in ghost_states["eliminated"]:
                        ghost_states["probabilities"][ghost] *= 1.2
            
            # Apply some disfavor (multiply by 0.5)
            if "some_disfavor" in behavior_data:
                for ghost in behavior_data["some_disfavor"]:
                    if ghost not in ghost_states["eliminated"]:
                        ghost_states["probabilities"][ghost] *= 0.5
            
            # Apply much disfavor (multiply by 0.2)
            if "much_disfavor" in behavior_data:
                for ghost in behavior_data["much_disfavor"]:
                    if ghost not in ghost_states["eliminated"]:
                        ghost_states["probabilities"][ghost] *= 0.2
    
    # Check if only one ghost remains
    possible_ghosts = [g for g in GHOST_TYPES if g not in ghost_states["eliminated"]]
    if len(possible_ghosts) == 1:
        ghost_states["confirmed"].add(possible_ghosts[0])
    
    # Special case for The Mimic (always has Ghost Orbs)
    if "The Mimic" not in ghost_states["eliminated"]:
        if "Ghost Orbs" in selected_evidence["negative"]:
            ghost_states["eliminated"].add("The Mimic")
    
    return ghost_states

def draw_evidence_tracker(screen, buttons, selected_evidence, selected_special_options, selected_special_behaviors):
    # Clear the screen with semi-transparent background
    screen.fill(EVIDENCE_BG)
    
    # Add instructions for left/right click
    instructions_text = "Left-click: Select/Deselect Evidence | Right-click: Eliminate/Uneliminate Evidence"
    instructions_surface = fonts['normal'].render(instructions_text, True, (255, 255, 150))
    instructions_rect = instructions_surface.get_rect(center=(TRACKER_WIDTH // 2, 20))
    screen.blit(instructions_surface, instructions_rect)
    
    # Calculate section heights based on content
    evidence_rows = math.ceil(len(EVIDENCES) / 7)  # 7 per row
    ghost_rows = math.ceil(len(GHOST_TYPES) / 6)   # 6 per row
    special_rows = math.ceil(len(SPECIAL_OPTIONS) / 5)  # 5 per row
    behavior_rows = math.ceil(len(SPECIAL_BEHAVIORS) / 5)  # 5 per row
    
    # Calculate actual section heights
    section_a_height = 35 + (evidence_rows * (EVIDENCE_BTN_HEIGHT + 10)) + 10
    section_b_height = 35 + (ghost_rows * (GHOST_BTN_HEIGHT + 8)) + 10
    section_c_height = 35 + (special_rows * (SPECIAL_BTN_HEIGHT + 8)) + 10
    section_d_height = 35 + (behavior_rows * (SPECIAL_BTN_HEIGHT + 8)) + 10
    
    # Calculate section positions with added padding for separation
    section_a_y = SECTION_PADDING
    section_b_y = section_a_y + section_a_height + SECTION_PADDING
    section_c_y = section_b_y + section_b_height + SECTION_PADDING
    section_d_y = section_c_y + section_c_height + SECTION_PADDING
    
    # Draw section headers with larger font
    section_header_font = fonts['large']
    
    # Section A: Evidence
    header_a = section_header_font.render("Evidence", True, TEXT_COLOR)
    screen.blit(header_a, (SECTION_PADDING, section_a_y))
    
    # Section B: Ghost Types
    header_b = section_header_font.render("Ghost Types", True, TEXT_COLOR)
    screen.blit(header_b, (SECTION_PADDING, section_b_y))
    
    # Section C: Special Options
    header_c = section_header_font.render("Special Options", True, TEXT_COLOR)
    screen.blit(header_c, (SECTION_PADDING, section_c_y))
    
    # Section D: Special Behaviors
    header_d = section_header_font.render("Special Behaviors (Probability Modifiers)", True, TEXT_COLOR)
    screen.blit(header_d, (SECTION_PADDING, section_d_y))
    
    # Draw section backgrounds to visually separate them
    pygame.draw.rect(screen, (40, 40, 50, 180),
                     (SECTION_PADDING//2, section_a_y - 5,
                      TRACKER_WIDTH - SECTION_PADDING, section_a_height), 0, 5)
    
    pygame.draw.rect(screen, (40, 40, 50, 180),
                     (SECTION_PADDING//2, section_b_y - 5,
                      TRACKER_WIDTH - SECTION_PADDING, section_b_height), 0, 5)
    
    pygame.draw.rect(screen, (40, 40, 50, 180),
                     (SECTION_PADDING//2, section_c_y - 5,
                      TRACKER_WIDTH - SECTION_PADDING, section_c_height), 0, 5)
    
    pygame.draw.rect(screen, (40, 40, 50, 180),
                     (SECTION_PADDING//2, section_d_y - 5,
                      TRACKER_WIDTH - SECTION_PADDING, section_d_height), 0, 5)
    
    # Determine ghost states based on current selections
    ghost_states = determine_ghost_states(selected_evidence, selected_special_options, selected_special_behaviors)
    
    # Check for impossible evidence combinations and update selected_evidence
    check_impossible_combinations(selected_evidence)
    
    # Draw all buttons
    for button in buttons:
        button.draw(screen, selected_evidence, selected_special_options, selected_special_behaviors, ghost_states)
    
    # Draw border around the entire tracker
    pygame.draw.rect(screen, EVIDENCE_BORDER, (0, 0, TRACKER_WIDTH, TRACKER_HEIGHT), 2)

def check_impossible_combinations(selected_evidence):
    """Check for impossible evidence combinations and mark them as negative"""
    # Only proceed if we have at least 1 positive evidence
    if len(selected_evidence["positive"]) < 1:
        return
        
    # For each evidence not yet selected
    for evidence in EVIDENCES:
        if evidence not in selected_evidence["positive"] and evidence not in selected_evidence["negative"]:
            # Create a test combination with this evidence
            test_combination = list(selected_evidence["positive"]) + [evidence]
            
            # Check if this would create an impossible combination
            impossible = False
            
            # Check against known impossible combinations
            for combo in IMPOSSIBLE_COMBINATIONS:
                if all(item in test_combination for item in combo):
                    impossible = True
                    break
            
            # Check if this evidence would eliminate all remaining ghosts
            if not impossible:
                # Create a temporary set to test
                test_positive = selected_evidence["positive"].copy()
                test_positive.add(evidence)
                test_negative = selected_evidence["negative"].copy()
                
                # Check if any ghost would remain possible
                any_ghost_possible = False
                for ghost, evidences in GHOST_TYPES.items():
                    # A ghost is possible if it has all positive evidence and none of the negative evidence
                    if all(e in evidences for e in test_positive) and not any(e in evidences for e in test_negative):
                        any_ghost_possible = True
                        break
                
                if not any_ghost_possible:
                    impossible = True
            
            if impossible:
                # This evidence would create an impossible combination, mark it negative
                selected_evidence["negative"].add(evidence)
    
    # Also check if any ghosts are eliminated based on current evidence
    # and mark their unique evidence as impossible
    possible_ghosts = set()
    for ghost, evidences in GHOST_TYPES.items():
        if all(e in evidences for e in selected_evidence["positive"]) and not any(e in evidences for e in selected_evidence["negative"]):
            possible_ghosts.add(ghost)
    
    # If we have eliminated some ghosts, check for evidence that's no longer possible
    if possible_ghosts and len(possible_ghosts) < len(GHOST_TYPES):
        # Find all evidence that could still be valid
        possible_evidence = set()
        for ghost in possible_ghosts:
            possible_evidence.update(GHOST_TYPES[ghost])
        
        # Mark any evidence not in any possible ghost as negative
        for evidence in EVIDENCES:
            if (evidence not in selected_evidence["positive"] and 
                evidence not in selected_evidence["negative"] and 
                evidence not in possible_evidence):
                selected_evidence["negative"].add(evidence)    

# Initialize evidence tracker UI
evidence_tracker_buttons = create_evidence_tracker_ui()


# Function to update settings from the settings window
def update_settings(new_settings):
    global current_map_size, current_difficulty, show_footstep_pattern
    global settings_key, hunt_timer_key, smudge_timer_key, evidence_tracker_key
    global ui_scale, WIDTH, HEIGHT, BAR_WIDTH, BAR_HEIGHT, BAR_X, BAR_Y
    global HUNT_BAR_Y, SMUDGE_TIMER_Y, FOOTSTEP_Y, FOOTSTEP_SIZE
    global WINDOW_X, WINDOW_Y, fonts, hunt_duration, position
    
    # Update settings variables
    current_map_size = new_settings.get('General', 'map_size')
    current_difficulty = new_settings.get('General', 'difficulty')
    show_footstep_pattern = new_settings.getboolean('General', 'show_footstep_pattern')
    
    evidence_tracker_key = new_settings.get('Hotkeys', 'evidence_tracker_key')
    settings_key = new_settings.get('Hotkeys', 'settings_key')
    hunt_timer_key = new_settings.get('Hotkeys', 'hunt_timer_key')
    smudge_timer_key = new_settings.get('Hotkeys', 'smudge_timer_key')
    
    # Update hunt duration
    hunt_duration = HUNT_DURATIONS[current_difficulty][current_map_size]
    
    # Check if UI scale or position changed
    new_ui_scale = float(new_settings.get('General', 'ui_scale'))
    new_position = new_settings.get('General', 'position')
    
    if new_ui_scale != ui_scale or new_position != position:
        # Update UI scale and position
        ui_scale = new_ui_scale
        position = new_position
        
        # Recalculate dimensions
        WIDTH, HEIGHT = int(BASE_WIDTH * ui_scale), int(BASE_HEIGHT * ui_scale)
        BAR_WIDTH, BAR_HEIGHT = int(BASE_BAR_WIDTH * ui_scale), int(BASE_BAR_HEIGHT * ui_scale)
        BAR_X, BAR_Y = (WIDTH - BAR_WIDTH) // 2, (HEIGHT - BAR_HEIGHT) // 2
        HUNT_BAR_Y = BAR_Y - int(35 * ui_scale)
        SMUDGE_TIMER_Y = BAR_Y + int(60 * ui_scale)
        FOOTSTEP_Y = HUNT_BAR_Y - int(25 * ui_scale)
        FOOTSTEP_SIZE = int(10 * ui_scale)
        
        # Update fonts
        for name, size in BASE_FONT_SIZES.items():
            fonts[name] = pygame.font.SysFont('Arial', int(size * ui_scale))
        
        # Update position
        position_map = {
            'top_left': (10, 10),
            'top_right': (screen_width - WIDTH - 10, 10),
            'bottom_left': (10, screen_height - HEIGHT - 10),
            'bottom_right': (screen_width - WIDTH - 10, screen_height - HEIGHT - 10)
        }
        WINDOW_X, WINDOW_Y = position_map.get(position, position_map['bottom_right'])
        
        # Resize and reposition the window
        pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME | pygame.SRCALPHA)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, WINDOW_X, WINDOW_Y, WIDTH, HEIGHT, 0)

# Function to open settings window
def open_settings_window():
    global settings_window_open
    
    if not settings_window_open:
        settings_window_open = True
        
        # Make main window clickable while settings are open
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                              win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & 
                              ~win32con.WS_EX_TRANSPARENT)
        
        # Create and run settings window
        settings_window = SettingsWindow(hwnd, config, update_settings)
        settings_window.run()
        
        # After settings window closes
        settings_window_open = False
        
        # Make main window click-through again
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                              win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | 
                              win32con.WS_EX_TRANSPARENT)

# Function to draw the footstep pattern helper
def draw_footstep_pattern(current_time, hunt_start_time):
    # Calculate which step we're on based on elapsed time
    elapsed_time = current_time - hunt_start_time
    step_position = (elapsed_time % (FOOTSTEP_STEP_INTERVAL * 2)) / FOOTSTEP_STEP_INTERVAL
    
    # Draw footstep indicator text
    footstep_text = fonts['small'].render("Normal Ghost Footstep Metronome:", True, TEXT_COLOR)
    text_rect = footstep_text.get_rect(midleft=(BAR_X, FOOTSTEP_Y))
    screen.blit(footstep_text, text_rect)
    
    # Draw the two footstep indicators
    for i in range(2):
        # Calculate position
        x_pos = BAR_X + BAR_WIDTH - 50 + (i * 25)  # Adjusted spacing
        y_pos = FOOTSTEP_Y
        
        # Determine if this step is active
        is_active = (i == int(step_position))
        
        # Calculate bounce effect (only for active step)
        bounce_offset = 0
        if is_active:
            # Create a bounce effect that peaks in the middle of the step interval
            step_progress = step_position - int(step_position)
            # Sine wave for smooth bounce: sin(π*x) gives a nice arc from 0 to 1 and back to 0
            bounce_offset = -5 * math.sin(math.pi * step_progress)  # Increased bounce height
        
        # Draw the footstep indicator
        color = FOOTSTEP_HIGHLIGHT_COLOR if is_active else FOOTSTEP_COLOR
        pygame.draw.circle(screen, color, (x_pos, y_pos + bounce_offset), FOOTSTEP_SIZE)
        
        # Draw a small footprint shape inside the circle
        if is_active:
            # Draw a simple footprint shape (just a smaller oval)
            pygame.draw.ellipse(screen, BACKGROUND, 
                               (x_pos - 4, y_pos - 5 + bounce_offset, 8, 10))

# Function to check hotkeys with debounce
def check_hotkey(key, action_type, current_time, debounce_time=0.5):
    try:
        if keyboard.is_pressed(key):
            if current_time - last_hotkey_press[action_type] > debounce_time:
                last_hotkey_press[action_type] = current_time
                print(f"Hotkey pressed: {key} for {action_type}")  # Debug print
                return True
    except Exception as e:
        print(f"Error with {action_type} hotkey: {e}")
    return False

# Main game loop
clock = pygame.time.Clock()
last_time = time.time()
running = True
previous_tracker_state = evidence_tracker_active  # Track previous state
last_topmost_check = time.time()  # Track when we last checked topmost status

# Create the evidence tracker UI buttons once
evidence_tracker_buttons = create_evidence_tracker_ui()

while running:
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    
    # Periodically ensure window stays on top (every 5 seconds)
    if current_time - last_topmost_check > 5:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        last_topmost_check = current_time
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and evidence_tracker_active:
            # Instead of closing the program, just hide the evidence tracker
            evidence_tracker_active = False
        elif event.type == pygame.MOUSEBUTTONDOWN and evidence_tracker_active:
            for button in evidence_tracker_buttons:
                if button.handle_click(event.pos, event.button, selected_evidence, selected_special_options, selected_special_behaviors):
                    # Recalculate ghost states after a click
                    break
        if event.type == pygame.USEREVENT:
            # Delayed check for impossible combinations
            check_impossible_combinations(selected_evidence)
    
    # Check hotkeys
    if check_hotkey(settings_key, 'settings', current_time) and not settings_window_open:
        open_settings_window()
            
    if check_hotkey(evidence_tracker_key, 'evidence', current_time):
        evidence_tracker_active = not evidence_tracker_active
        
    # Toggle window properties when evidence tracker state changes
    if evidence_tracker_active != previous_tracker_state:
        previous_tracker_state = evidence_tracker_active
        
        if evidence_tracker_active:
            # Make window clickable and full screen when tracker is active
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                  win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) &
                                  ~win32con.WS_EX_TRANSPARENT)
                            
            # Make the tracker full screen
            tracker_width = screen_width
            tracker_height = screen_height
            
            # Resize and reposition the window for evidence tracker (full screen)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST,
                                  0, 0, tracker_width, tracker_height, 0)
                            
            # Recreate the pygame display surface with the new dimensions
            screen = pygame.display.set_mode((tracker_width, tracker_height), pygame.NOFRAME | pygame.SRCALPHA)
            hwnd = pygame.display.get_wm_info()["window"]  # Get the new window handle
            
            # Ensure window stays on top
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            
            # Recreate the evidence tracker UI with the new dimensions
            TRACKER_WIDTH = tracker_width
            TRACKER_HEIGHT = tracker_height
            evidence_tracker_buttons = create_evidence_tracker_ui()
        else:
            # Make window click-through when tracker is inactive
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                  win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) |
                                  win32con.WS_EX_TRANSPARENT)
                            
            # Restore original window size and position
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST,
                                  WINDOW_X, WINDOW_Y,
                                  WIDTH, HEIGHT, 0)
                            
            # Recreate the pygame display surface with the original dimensions
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME | pygame.SRCALPHA)
            hwnd = pygame.display.get_wm_info()["window"]  # Get the new window handle
            
            # Ensure window stays on top
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    
    if check_hotkey(hunt_timer_key, 'hunt', current_time):
        if hunt_active:
            hunt_active = False
        else:
            hunt_active = True
            hunt_start_time = current_time
            hunt_duration = HUNT_DURATIONS[current_difficulty][current_map_size]
    
    if check_hotkey(smudge_timer_key, 'smudge', current_time):
        if smudge_active:
            smudge_active = False
            smudge_reached_max = False
        else:
            smudge_active = True
            smudge_start_time = current_time
            smudge_reached_max = False
    
    # Update stamina
    if in_recovery:
        recovery_elapsed = current_time - recovery_start_time
        if recovery_elapsed >= RECOVERY_PERIOD:
            in_recovery = False
            stamina = MAX_STAMINA
    else:
        # Check if shift is pressed AND a movement key is pressed (sprinting)
        is_sprinting = keyboard.is_pressed('shift') and any(keyboard.is_pressed(key) for key in ('w', 'a', 's', 'd'))
                    
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
                eased_factor = 1 - (1 - ramp_factor) * (1 - ramp_factor)
                                        
                # Calculate current regen rate
                current_regen_rate = MAX_RECOVERY_RATE * (MIN_REGEN_PERCENT + (1 - MIN_REGEN_PERCENT) * eased_factor)
                                        
                # Apply regeneration
                stamina = min(stamina + current_regen_rate * dt, MAX_STAMINA)
                    
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
    screen.fill((0, 0, 0, 0))
    
    # Draw appropriate UI based on active state
    if evidence_tracker_active:
        # Draw the evidence tracker UI
        draw_evidence_tracker(screen, evidence_tracker_buttons, selected_evidence,
                              selected_special_options, selected_special_behaviors)
    else:
        # Draw the regular HUD
        screen.fill(BACKGROUND)
            
        # Draw hunt timer
        if hunt_active:
            # Draw hunt timer background and progress bar
            pygame.draw.rect(screen, BAR_BACKGROUND, (BAR_X, HUNT_BAR_Y, BAR_WIDTH, BAR_HEIGHT))
            hunt_progress = hunt_remaining / hunt_duration
            hunt_width = hunt_progress * BAR_WIDTH
            pygame.draw.rect(screen, RECOVERY_COLOR, (BAR_X, HUNT_BAR_Y, hunt_width, BAR_HEIGHT))
            pygame.draw.rect(screen, TEXT_COLOR, (BAR_X, HUNT_BAR_Y, BAR_WIDTH, BAR_HEIGHT), 1)
                        
            # Draw hunt timer text
            hunt_text = f"Hunt: {hunt_remaining:.1f}s"
            text_surface = fonts['normal'].render(hunt_text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HUNT_BAR_Y - 10))
            screen.blit(text_surface, text_rect)
                        
            # Draw footstep pattern helper if enabled
            if show_footstep_pattern:
                draw_footstep_pattern(current_time, hunt_start_time)
        else:
            # Draw instructional text when hunt timer is inactive
            hunt_text = f"Hunt Timer: Ready ({hunt_timer_key})"
            text_surface = fonts['normal'].render(hunt_text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HUNT_BAR_Y))
            screen.blit(text_surface, text_rect)
                        
            # Draw smaller text for config hint
            config_hint = f"Settings: {settings_key}"
            hint_surface = fonts['small'].render(config_hint, True, TEXT_COLOR)
            hint_rect = hint_surface.get_rect(center=(WIDTH // 2, HUNT_BAR_Y + 15))
            screen.blit(hint_surface, hint_rect)
            
        # Draw stamina bar
        pygame.draw.rect(screen, BAR_BACKGROUND, (BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT))
            
        if in_recovery:
            # Calculate recovery progress (0 to 1)
            recovery_progress = (current_time - recovery_start_time) / RECOVERY_PERIOD
            recovery_width = recovery_progress * BAR_WIDTH
            pygame.draw.rect(screen, RECOVERY_COLOR, (BAR_X, BAR_Y, recovery_width, BAR_HEIGHT))
        else:
            # Normal stamina bar
            stamina_width = (stamina / MAX_STAMINA) * BAR_WIDTH
                        
            # Determine bar color based on state
            if was_sprinting:
                bar_color = STAMINA_COLOR
            else:
                time_since_sprint_stopped = current_time - regen_start_time
                if time_since_sprint_stopped <= REGEN_DELAY:
                    bar_color = DELAY_COLOR  # In delay period
                elif time_since_sprint_stopped <= REGEN_DELAY + REGEN_RAMP_TIME:
                    bar_color = RAMPING_COLOR  # In ramp-up period
                else:
                    bar_color = STAMINA_COLOR
                        
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
                delay_left = REGEN_DELAY - time_since_sprint_stopped
                stamina_text = f"Stamina: {stamina:.1f}% (Delay: {delay_left:.1f}s)"
            elif time_since_sprint_stopped <= REGEN_DELAY + REGEN_RAMP_TIME:
                ramp_time = time_since_sprint_stopped - REGEN_DELAY
                ramp_percent = min(ramp_time / REGEN_RAMP_TIME * 100, 100)
                stamina_text = f"Stamina: {stamina:.1f}% (Ramp: {ramp_percent:.0f}%)"
            else:
                stamina_text = f"Stamina: {stamina:.1f}%"
        else:
            stamina_text = f"Stamina: {stamina:.1f}%"
            
        text_surface = fonts['normal'].render(stamina_text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, BAR_Y + BAR_HEIGHT + 10))
        screen.blit(text_surface, text_rect)
            
        # Draw smudge timer
        if smudge_active:
            if smudge_reached_max:
                # Show "Likely Spirit" message
                smudge_text = "Smudge Timer: LIKELY SPIRIT"
                text_surface = fonts['large'].render(smudge_text, True, SPIRIT_COLOR)
            else:
                smudge_elapsed = min(current_time - smudge_start_time, MAX_SMUDGE_TIME)
                                    
                # Add ghost type hints based on elapsed time
                if smudge_elapsed >= 60:
                    if smudge_elapsed < 90:
                        smudge_text = f"Smudge Timer: {smudge_elapsed:.1f}s (Demon?)"
                    elif smudge_elapsed < 180:
                        smudge_text = f"Smudge Timer: {smudge_elapsed:.1f}s (Not Spirit)"
                    else:
                        smudge_text = f"Smudge Timer: {smudge_elapsed:.1f}s"
                else:
                    smudge_text = f"Smudge Timer: {smudge_elapsed:.1f}s"
                                    
                text_surface = fonts['large'].render(smudge_text, True, SMUDGE_COLOR)
                        
            text_rect = text_surface.get_rect(center=(WIDTH // 2, SMUDGE_TIMER_Y))
            screen.blit(text_surface, text_rect)
        else:
            # Draw inactive smudge timer text
            smudge_text = f"Smudge Timer: Ready ({smudge_timer_key})"
            text_surface = fonts['large'].render(smudge_text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, SMUDGE_TIMER_Y))
            screen.blit(text_surface, text_rect)
    
    # Update display
    pygame.display.flip()
    
    # Cap at 60 FPS
    clock.tick(60)


# Ensure window is click-through when closing
if not win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_TRANSPARENT:
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                          win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) |
                          win32con.WS_EX_TRANSPARENT)
                          
pygame.quit()
sys.exit()

## version 1.7 - created by UndeadWolf23 3/27/2025 - Calibrated for Phasmophobia v0.12.0.2 ##