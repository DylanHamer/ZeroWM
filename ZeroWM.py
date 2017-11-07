"""
 _____           __        ____  __
|__  /___ _ __ __\ \      / /  \/  |
  / // _ \ '__/ _ \ \ /\ / /| |\/| |
 / /|  __/ | | (_) \ V  V / | |  | |
/____\___|_|  \___/ \_/\_/  |_|  |_|

Version 1.0 | Spicy Salamander

ZeroWM 1.0
Super simple window manager written in Python
by Dylan Hamer
"""

from Xlib import X, XK                      # X server and X keyboard
from Xlib.display import Display            # X display
from Xlib.display import colormap           # X colourmap
import subprocess                           # Launch external processes
import click                                # Handle colours and styling for log output
from time import strftime as currentTime    # Get current time in human readable format
from Preferences import preferences         # User preference file
import Startup as startup                   # User startup file
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

class windowManagerInfo:  # Window manager constants
    name = "ZeroWM"
    version = "1.0"
    author = "Dylan Hamer"
    releaseDate = "November 2017"
    releaseName = "Spicy Salamander"
    informationString = name+" "+version+": "+click.style(releaseName, fg="green")+" by "+author+" ("+releaseDate+")"+"\n"


"""Main WM class"""
class wm(object):
    """Initialise WM variables and open display"""
    def __init__(self):
        self.windowList = []  # List of opened windows
        self.display = Display()  # Initialise display
        self.colormap = self.display.screen().default_colormap  # Initialise colourmap
        self.currentMode = None
        self.activeWindow = None
        self.rootWindow = self.display.screen().root  # Get root window
        self.displayWidth = self.rootWindow.get_geometry().width  # Get width of display
        self.displayHeight = self.rootWindow.get_geometry().height  # Get height of display
        self.rootWindow.change_attributes(event_mask = X.SubstructureRedirectMask)  # Redirect events from root window
        self.configureKeys()  # Configure key bindings

    def mainLoop(self):
        self.updateFocus()
        self.updateBorders()
        self.handleEvents()
        log(3, "Mode:"+str(self.currentMode))

    """Destroy an active window"""
    def destroyWindow(self, event):
        try:
            self.activeWindow.destroy()
            self.windowList.remove(self.activeWindow)
            self.activeWindow = None
        except:
            log(2, "No focused window!")
 
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
        self.r = set(code for code, index in self.display.keysym_to_keycodes(XK.XK_X))
        self.grabbedKeys = [self.left, self.right, self.up, self.down, self.close, self.t, self.e, self.x, self.r]
        for key in self.grabbedKeys:  # For each key to grab,
            superkey = preferences.applicationDefaults.modkey
            if (superkey == "Mod4"):
                self.grabKey(key, X.Mod4Mask)   # Preferences.py to change this key
            elif(superkey == "Mod1"):
                self.grabKey(key, X.Mod1Mask)

    #def resizeWindow(window, direction):
    #    windowW = window.get_geometry().width
    #    windowH = window.get_geometry().height
    #    if direction == 0: window.configure(width=windowW-1)
    #    elif direction == 1: window.configure(width=windowW+1)
    #    elif direction == 2: window.configure(height=windowH-1)
    #    elif direction == 3: window.configure(height=windowH+1)


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
      #  if self.currentMode == "resize":                                                             # If resize mode is enabled:
            #if event.detail in self.left: self.resizeWindow(event.window, 0)                        # Alt+Left Arrow: resize window (x-1)
           # elif event.detail in self.right: self.moveWindow(event.window, 1)                       # Alt+Right Arrow: resize window (x+1)
          #  elif event.detail in self.up: self.moveWindow(event.window, 2)                          # Alt+Up Arrow: resize window (y-1)
         #   elif event.detail in self.down: self.moveWindow(event.window, 3)                        # Alt+Down Arrow: resize window (y+1)
     #   else:                                                                                       # Otherwise,
        if event.detail in self.left: self.moveWindow("left")                                   # Alt+Left Arrow: move a window left
        elif event.detail in self.right: self.moveWindow("right")                               # Alt+Right Arrow: move a window right
        elif event.detail in self.up: self.moveWindow("up")                                     # Alt+Up Arrow: move a window up
        elif event.detail in self.down: self.moveWindow("down")                                 # Alt+Down Arrow: move a window down
        elif event.detail in self.t: self.runProcess(preferences.applicationDefaults.terminal)      # Alt+T: Launch a terminal
        elif event.detail in self.e: self.runProcess(preferences.applicationDefaults.launcher)      # Alt+E: Launch a program launcher
        elif event.detail in self.x: self.destroyWindow(event)                                      # ALT+X: Close a window
        elif event.detail in self.r: self.currentMode = "resize"                                    # ALT+R: Enable resize mode
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

def main():
    log(0, windowManagerInfo.informationString)  # Display version info, author, etc at startup
    try:
        startup.onStart()  # Run any commands in user startup file
    except:
        log(2, "There is an error in your startup file!")

    while True:
        try:
            windowManager.mainLoop()
        except KeyboardInterrupt:  # If CTRL-C pressed,
           startup.onStop()
           windowManager.closeDisplay()  # Close the connection to the display

windowManager = wm()

if __name__ == "__main__":
    main()
