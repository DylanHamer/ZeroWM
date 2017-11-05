"""
 _____           __        ____  __
|__  /___ _ __ __\ \      / /  \/  |
  / // _ \ '__/ _ \ \ /\ / /| |\/| |
 / /|  __/ | | (_) \ V  V / | |  | |
/____\___|_|  \___/ \_/\_/  |_|  |_|

Version 0.6 | Verbal Alligator

ZeroWM 0.6
Super simple window manager written in Python
by Dylan Hamer
"""

from Xlib import X, XK                      # X server and X keyboard
from Xlib.display import Display            # X display
from Xlib.display import colormap           # X colourmap
import subprocess                           # Launch external processes
import click                                # Handle colours and styling for log output
from time import strftime as currentTime    # Get current time in humman readable format

enableDebugging = False

"""Output log to command line"""
def log(logLevel, logInfo):
    colourCodes = ["green", "yellow", "red", "cyan"]  # Colour codes for different error levels
    logLevels = ["[Info]    ", "[Warning] ", "[Error]   ", "[Debug]   "]  # Labels for different log levels
    timeStamp = "["+currentTime("%H:%M:%S")+"] "  # Timestamp of current time
    if enableDebugging == False and logLevel == 3:
        return
    else:
        click.echo(click.style(logLevels[logLevel], fg=colourCodes[logLevel])+click.style(timeStamp, fg="blue")+logInfo)  # Display error level of log event, current time and log descriptiom

"""Preference class"""
class preferences:
    class windowManagerInfo:  # Window manager constants
        name = "ZeroWM"
        version = "0.6"
        author = "Dylan Hamer"
        releaseDate = "November 2017"
        releaseName = "Verbal Alligator"
        informationString = name+" "+version+": "+click.style(releaseName, fg="green")+" by "+author+" ("+releaseDate+")"+"\n"

    class applicationDefaults:  # Default applications, change these to your preferred applications
        terminal = {"name":"LXTerminal", "command":["/usr/bin/lxterminal"]}
        launcher = {"name":"Rofi", "command":["/usr/bin/rofi", "-show", "run"]}
        browser = {"name":"Midori", "command":["/usr/bin/midori"]}

    class wallpaper:
        wallpaperFile = "/home/dylan/Pictures/mrrobot.png"  # File of wallpaper
        wallpaperCommand = {"name":"Feh", "command":["/usr/bin/feh", "--bg-scale", wallpaperFile]}  # Command to show wallpaper

    class theme:
        class border:
            activeColour = "#7bfcb7"
            inactiveColour = "#252625"
            borderWidth = 2

"""Main WM class"""
class wm(object):
    """Initialise WM variables and open display"""
    def __init__(self):
        log(0, "Starting... ")
        self.windowList = []  # List of opened windows
        self.display = Display()  # Initialise display
        self.colormap = self.display.screen().default_colormap  # Initialise colourmap
        self.rootWindow = self.display.screen().root  # Get root window
        self.displayWidth = self.rootWindow.get_geometry().width  # Get width of display
        self.displayHeight = self.rootWindow.get_geometry().height  # Get height of display
        self.rootWindow.change_attributes(event_mask = X.SubstructureRedirectMask)  # Redirect events from root window
        self.configureKeys()  # Configure key bindings

    def mainLoop(self):
        self.updateFocus()
        self.updateBorders()
        self.handleEvents()

    """Destroy an active window"""
    def destroyWindow(self, event):
        self.activeWindow.destroy()

    def updateFocus(self):
        window = self.display.screen().root.query_pointer().child
        if window != 0:
            self.activeWindow = window

    def updateBorders(self):
        for window in self.windowList:
            if window != self.activeWindow:
                borderColour = preferences.theme.border.inactiveColour
            else:
                borderColour = preferences.theme.border.activeColour
            borderColour = self.colormap.alloc_named_color(borderColour).pixel #borderColour).pixel
            window.configure(border_width = preferences.theme.border.borderWidth)
            window.change_attributes(None,border_pixel=borderColour)
            self.display.sync()

    """Handle WM events"""
    def handleEvents(self):
        ignoredEvents = [3, 33, 34, 23]  # Blacklisted events
        if self.display.pending_events() > 0:
            event = self.display.next_event()  # Get next event from display 
        else:
            return
        if event.type == X.MapRequest: self.handleMap(event)  # Send mapping events to the mapping handler
        elif event.type == X.KeyPress: self.handleKeyPress(event)  # Send keypress event to the keypress handler
        elif event.type in ignoredEvents: log(3, "Ignoring event: "+str(event.type))  # Ignore event if it is a blacklisted event
        else:  # Otherwise, if the event is not a currently handled event
            log(1, "Unhandled event: "+str(event.type))  # Warn of an unhandled event

    """Handle a mapping request"""
    def handleMap(self, event):
        self.windowList.append(event.window)  # Add the window identifier to a list of open windows
        log(3, str(self.windowList))  # Show list of windows (DEBUG)
        self.activeWindow = event.window  # Set the active window to the mapped window
        self.activeWindowName = event.window.get_wm_name()  # Set the active window name to the window title
        event.window.map()  # Map the window

    """Receive a KeyPressed event when a certain key is pressed"""
    def grabKey(self, codes, modifier):
        for code in codes:  # For each code
            self.rootWindow.grab_key(code, modifier, 1, X.GrabModeAsync, X.GrabModeAsync)  # Receive events when the key is pressed

    """Bind keys"""
    def configureKeys(self):
        self.left = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_Left))  # Assign a list of possible keycodes to the variable
        self.right = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_Right))
        self.up = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_Up))
        self.down = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_Down))
        self.close = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_X))
        self.t = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_T))
        self.e = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_E))
        self.x = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_X))
        self.grabbedKeys = [self.left, self.right, self.up, self.down, self.close, self.t, self.e, self.x]
        for key in self.grabbedKeys:  # For each key to grab,
            self.grabKey(key, X.Mod1Mask)  # Grab the key with the modifer of Alt

    """Change the position of an active window"""
    def moveWindow(self, direction):
        try:
            if direction == "left":
                windowX = self.activeWindow.get_geometry().x  # Get the current position of the active window
                self.activeWindow.configure(x=windowX-5)  # Decrease the X position to move it left
            elif direction == "right":
                windowX = self.activeWindow.get_geometry().x
                self.activeWindow.configure(x=windowX+5)
            elif direction == "up":
                windowY = self.activeWindow.get_geometry().y
                self.activeWindow.configure(y=windowY-5)    
            elif direction == "down":
                windowY = self.activeWindow.get_geometry().y
                self.activeWindow.configure(y=windowY+5)
            else:
                log(1, "Invalid movement direction!")  
        except AttributeError:
                log(1, "No focused window!")

    """Handle key presses"""
    def handleKeyPress(self, event):
        if event.detail in self.left: self.moveWindow("left")                                   # Alt+Left Arrow: move a window left
        elif event.detail in self.right: self.moveWindow("right")                               # Alt+Right Arrow: move a window right
        elif event.detail in self.up: self.moveWindow("up")                                     # Alt+Up Arrow: move a window up
        elif event.detail in self.down: self.moveWindow("down")                                 # Alt+Down Arrow: move a window down
        elif event.detail in self.t: self.runProcess(preferences.applicationDefaults.terminal)  # Alt+T: Launch a terminal
        elif event.detail in self.e: self.runProcess(preferences.applicationDefaults.launcher)  # Alt+E: Launch a program launcher
        elif event.detail in self.x: self.destroyWindow(event)                                  # ALT+X: Close a window
        else:
            log(1, "Unhandled key event!")

    """Close connection to display server"""
    def closeDisplay(self):
        log(0, "Exiting...")
        self.display.close()

    """Run an application/process"""
    def runProcess(self, applicationInfo):
        try:
            name = applicationInfo["name"]  # Get application name
            command = applicationInfo["command"]  # Get aplication command 
        except:
            raise ValueError
        try:
            log(0, "Running: "+name)
            subprocess.Popen(command)  # Run the command and disown the child process
        except BaseException as error:
            log(2, "Failed to launch process: "+processCommand+"!")
            log(3, str(error))

@click.option("--debug", default = False)
def main(debug=False):
    print debug
    enableDebugging = debug
    print preferences.windowManagerInfo.informationString  # Display version info, author, etc at startup
    windowManager = wm()  # Initialise the WM
    windowManager.runProcess(preferences.wallpaper.wallpaperCommand)    # Set wallpaper

    while True:
        try:
            windowManager.mainLoop()
        except KeyboardInterrupt:  # If CTRL-C pressed,
           windowManager.closeDisplay()  # Close the connection to the display

if __name__ == "__main__":
    main()
