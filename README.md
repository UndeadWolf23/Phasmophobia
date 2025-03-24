Version 1.6 Update: Added animated footstep metronome! Increased overall HUD size. Added toggle for metronome in settings UI.

====================================================
          PhasmoHUD - Visual Aid & Timer
====================================================

 ABOUT:
 --------
 PhasmoHUD is a lightweight **visual overlay** designed to 
 assist *Phasmophobia* players with in-game mechanics:

 - Accurate **stamina bar** to track movement endurance.
 - **Hunt timer** to estimate when ghosts stop hunting.
 - **Smudge timer** to track the time until the next hunt (for use in identifying or eliminating Demons and Spirits).

 This tool provides **real-time** assistance without interfering
 with the game, making your ghost hunts smoother and more efficient.

====================================================
 INSTALLATION & USAGE
====================================================

  [ Executable (.exe) Version ]
 ---------------------------------
 1. **Download & Extract**
    - Download the `.7z` file and extract it using **7-Zip** or **WinRAR**. https://www.7-zip.org/

 2. **Keep Files Together**
    - Do **NOT** move the `.exe` file from its extracted folder!
    - It must stay in the same directory as the **_internal** folder 
      to access the required **DLL files**.

 3. **Run PhasmoHUD**
    - Double-click the `.exe` file to start the overlay.

  *NOTE:* Since this executable is **not digitally signed**, 
  Windows or your antivirus may warn you. You can safely allow it.

  [ Python Version ]
 ---------------------
 1. **Install Python**
    - Download and install **Python 3.12** from:
      https://www.python.org/

 2. **Install Required Packages**
    - Open a command prompt and run:
      ```
      pip install pygame keyboard pywin32
      ```
    - Future updates may require additional packages.

 3. **Run the Script**
    - After installing the dependencies, you can execute 
      the Python script as normal.

====================================================
 HOW TO USE
====================================================

  - **Hunt Timer Controls:**
    - `Ctrl + Z` → Open hunt timer settings. Use the carousel menus to set the map size and difficulty level.
    - `Ctrl + X` → Start the hunt timer.
    - Pressing `Ctrl + X` again will **cancel/reset** the hunt timer.

  - **Smudge Timer Controls:**
    - `Ctrl + C` → Start the smudge timer after smudging a ghost.
    - Pressing `Ctrl + C` again will **cancel/reset** the smudge timer.
    - The timer will also indicate the likeliness of a Demon or Spirit.

  - **Stamina Bar Mechanics:**
    - The **sprint meter** visually tracks stamina usage.
    - The bar will show:
      - **Stamina regeneration delay.**
      - **Regen ramp-up speed.**
      - **Remaining stamina percentage**
      - **Stamina recovery period when out of breath**

  These tools help you predict movement limits, optimize survival
  during hunts, and track down ghost types.

====================================================
  AUTHOR & VERSION INFO
====================================================

  - **Developer:**   UndeadWolf
  - **Version:**     1.6
  - **Release Date:** 03/24/2025

New features are currently in the works. Stay tuned.

  Happy hunting! 👻
