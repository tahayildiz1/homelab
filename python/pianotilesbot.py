import win32api
import win32con
import win32gui
import time
from PIL import ImageGrab
import keyboard

# Function to perform a mouse click at a given coordinate
def click(x, y):
    win32api.SetCursorPos((x, y))  # Move the cursor to the specified coordinates
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)  # Press the left mouse button down
    time.sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)    # Release the left mouse button

# Coordinates to check for the black color
coordinates = [(759, 500), (847, 500), (932, 500), (1024, 500)]

try:
    while True:  # Infinite loop to keep the program running
        if keyboard.is_pressed('q'):  # If 'q' is pressed, break the loop
            print("Exiting...")
            break

        screen = ImageGrab.grab()  # Take a screenshot of the screen

        for coord in coordinates:
            if screen.getpixel(coord) == (0, 0, 0):  # Check if the pixel is black
                click(*coord)  # Click the coordinate
                print(f"Clicked at {coord}")

except KeyboardInterrupt:
    print("Program exited with CTRL+C")
