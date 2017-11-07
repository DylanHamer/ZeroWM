"""
 _____           __        ____  __
|__  /___ _ __ __\ \      / /  \/  |
  / // _ \ '__/ _ \ \ /\ / /| |\/| |
 / /|  __/ | | (_) \ V  V / | |  | |
/____\___|_|  \___/ \_/\_/  |_|  |_|

User startup file
This file is executed at startup. Modify this file to change WM preferences

Created by Dylan Hamer
"""

from ZeroWM import log            # Enable logging function
from ZeroWM import preferences    # Allow access to preferences
from ZeroWM import windowManager  # Allow direct control of window manager

"""This function will be executed when the window manager is ready."""
def onStart():
    #windowManager.runProcess(preferences.wallpaper.wallpaperCommand)    # Set wallpaper at startup
    pass

"""This function will be executed when the window manager shuts down cleanly"""
def onStop():
    pass  # Do nothing

if __name__ == "__main__":
    log(2, "This file is meant to be run by ZeroWM. This is not a standalone application...")  # Warn user if executed incorrectly
