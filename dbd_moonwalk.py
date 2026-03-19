import time
import threading
from pynput.keyboard import Controller, Key
from pynput import mouse

keyboard = Controller()
running = False

sequence_delay = 0.2
alternate_delay = 0.2
#alternate_delay = 0.18

def macro_loop():
    global running

    # Hold Shift the entire time
    keyboard.press(Key.shift)

    # --- Run sequence once ---
    for key in ['w', 'a', 's']:
        if not running:
            break
        keyboard.press(key)
        time.sleep(sequence_delay)
        keyboard.release(key)

    # --- Hold W for alternating phase ---
    if running:
        keyboard.press('w')

    toggle = 0
    while running:
        key = 'd' if toggle == 0 else 'a'
        keyboard.press(key)
        time.sleep(alternate_delay)
        keyboard.release(key)
        toggle = 1 - toggle

    # Cleanup on stop
    keyboard.release('w')
    keyboard.release(Key.shift)

def start_macro():
    global running
    if not running:
        running = True
        threading.Thread(target=macro_loop, daemon=True).start()

def stop_macro():
    global running
    running = False

def on_click(x, y, button, pressed):
    if not pressed:
        return

    # --- Safe side button detection ---
    side_buttons = [mouse.Button.button8]

    # Add x1 only if it exists (prevents AttributeError)
    if hasattr(mouse.Button, "x1"):
        side_buttons.append(mouse.Button.x1)

    if button in side_buttons:
        if running:
            stop_macro()
        else:
            start_macro()

# Start mouse listener in a background thread
mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.daemon = True
mouse_listener.start()

# Keep main thread alive
print("Press the side mouse button (X1) to toggle macro. Ctrl+C to exit.")
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    stop_macro()
    print("Exiting...")
