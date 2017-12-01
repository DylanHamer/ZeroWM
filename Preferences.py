"""
 _____           __        ____  __
|__  /___ _ __ __\ \      / /  \/  |
  / // _ \ '__/ _ \ \ /\ / /| |\/| |
 / /|  __/ | | (_) \ V  V / | |  | |
/____\___|_|  \___/ \_/\_/  |_|  |_|

User preferences file
This file is executed at startup. Modify this file to change WM preferences

Created by Dylan Hamer
"""

class preferences:
    class applicationDefaults:  # Default applications, change these to your preferred applications
        terminal = {"name":"Termite", "command":["/usr/bin/termite"]}
        launcher = {"name":"Rofi", "command":["/usr/bin/rofi", "-show", "run"]}
        browser = {"name":"Firefox", "command":["/usr/bin/firefox"]}

        """ Change this to X.Mod1Mask to set Alt default Button"""
        modkey = "Mod1" # Super Button

    class wallpaper:
        wallpaperFile = "Wallpapers/MountainLandscape.jpeg"  # File of wallpaper
        wallpaperCommand = {"name":"Feh", "command":["/usr/bin/feh", "--bg-scale", wallpaperFile]}  # Command to show wallpaper

    class theme:
        class border:
            activeColour = "#ffffff"    # Colour of borders when focused
            inactiveColour = "#000000"  # Colour of borders when not in focus
            borderWidth = 2             # Width of window borders



