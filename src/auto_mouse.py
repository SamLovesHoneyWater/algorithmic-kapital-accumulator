import pyautogui
import time,random

def move_mouse_randomly(interval, duration=None):
    """
    Move the mouse cursor to random positions on the screen for a specified duration.
    
    :param duration: Total time in seconds to move the mouse randomly.
    :param interval: Time in seconds between each random move.
    """
    start_time = time.time()
    x, y = pyautogui.size()
    screen_width, screen_height = x - 200, y - 200
    
    while duration is None or time.time() - start_time < duration:
        x = random.randint(0, screen_width - 1)
        y = random.randint(0, screen_height - 1)
        pyautogui.moveTo(x, y, duration=1)
        time.sleep(interval)

# Example usage: move the mouse randomly for 10 seconds with 1-second intervals
move_mouse_randomly(10)

'''
# Define the coordinates where you want to click
coordinates = [
    (498, 1052),
    (709, 331),  # Example coordinate 1
    (1375, 269),  # Example coordinate 2
    (1419, 631),  # Example coordinate 3
    # Add more coordinates as needed
]

# Define the time interval between clicks
min_interval = 1  # 1 second
time.sleep(4)
# Start the iterative clicking process
while True:
    time.sleep(35)
    for x, y in coordinates:
        pyautogui.click(x, y)
        print(f"clicked {x}, {y}")
        time.sleep(min(min_interval, random.random()*15))  # Wait for the specified interval before the next click

    pyautogui.hotkey('ctrl', 'a')

    # Press the Delete key to remove the selected text
    pyautogui.press('delete')

    time.sleep(min(min_interval, random.random()*15))

    # Type out a string
    pyautogui.hotkey('ctrl', 'v')
    #pyautogui.write('RE: 孙也好领导大家', interval=min(0.01, random.random()*0.1))

    # Press the Enter key
    pyautogui.press('enter')
'''
    