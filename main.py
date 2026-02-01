"""
Lock-On System
Real-time screen capture with AI-based target detection and mouse lock-on
Hold 'E' to activate lock-on targeting
Supports: Red ball detection, Person/character detection (YOLO)
"""

import cv2
import numpy as np
import mss
import time
from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode
from collections import deque
import config

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("YOLO not available - install with: pip install ultralytics")

# Global YOLO model
yolo_model = None

# Global state
is_e_held = False
mouse_controller = mouse.Controller()
screen_saver = mss.mss()

# Smoothing buffer for mouse movement
position_buffer = deque(maxlen=5)
last_mouse_pos = (0, 0)


def on_press(key):
    """Handle key press events"""
    global is_e_held
    try:
        if key.char == 'e' or key.char == 'E':
            is_e_held = True
    except AttributeError:
        pass


def on_release(key):
    """Handle key release events"""
    global is_e_held
    try:
        if key.char == 'e' or key.char == 'E':
            is_e_held = False
    except AttributeError:
        pass


def start_keyboard_listener():
    """Start listening for keyboard input"""
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    return listener


def capture_screen(region=None):
    """Capture screen using MSS"""
    monitor = screen_saver.monitors[1]  # Primary monitor
    
    if region:
        left, top, width, height = region
        capture_area = {
            'left': left,
            'top': top,
            'width': width,
            'height': height
        }
    else:
        capture_area = monitor
    
    screenshot = screen_saver.grab(capture_area)
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    return frame

def detect_persons_yolo(frame):
    """
    Detect people/characters using YOLO
    Returns: list of (x, y, width, height) bounding boxes
    """
    global yolo_model
    
    if not YOLO_AVAILABLE or yolo_model is None:
        return [], None
    
    try:
        # Run YOLO inference
        results = yolo_model(frame, conf=config.YOLO_CONFIDENCE, iou=config.YOLO_IOU, verbose=False)
        
        persons = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get class name (should be 'person' for class 0)
                if int(box.cls[0]) == 0:  # Class 0 is 'person' in COCO dataset
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    width = x2 - x1
                    height = y2 - y1
                    
                    # Filter by minimum size
                    if width >= config.MIN_PERSON_WIDTH and height >= config.MIN_PERSON_HEIGHT:
                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2
                        persons.append((center_x, center_y, width, height))
        
        return persons, results[0] if results else None
    
    except Exception as e:
        print(f"YOLO detection error: {e}")
        return [], None


def find_closest_person(persons, frame_center):
    """Find the closest person to frame center"""
    if not persons:
        return None
    
    # Sort by distance to center
    persons_sorted = sorted(
        persons,
        key=lambda p: (p[0] - frame_center[0])**2 + (p[1] - frame_center[1])**2
    )
    
    return persons_sorted[0]  # Return closest person


def smooth_mouse_position(target_pos, smoothing=config.MOUSE_SMOOTHING):
    """Smooth mouse movement for better tracking"""
    global last_mouse_pos, position_buffer
    
    position_buffer.append(target_pos)
    
    # Calculate average of buffer
    if position_buffer:
        avg_x = int(np.mean([p[0] for p in position_buffer]))
        avg_y = int(np.mean([p[1] for p in position_buffer]))
        
        # Interpolate between last position and average
        smooth_x = int(last_mouse_pos[0] * (1 - smoothing) + avg_x * smoothing)
        smooth_y = int(last_mouse_pos[1] * (1 - smoothing) + avg_y * smoothing)
        
        last_mouse_pos = (smooth_x, smooth_y)
        return (smooth_x, smooth_y)
    
    return last_mouse_pos


def move_mouse_to_person(person, frame_width, frame_height, screen_offset=(0, 0)):
    """Move mouse to target person with smoothing"""
    if person is None:
        return
    
    x, y, width, height = person
    
    # Apply screen offset if capturing a region
    screen_x = x + screen_offset[0]
    screen_y = y + screen_offset[1]
    
    # Smooth the mouse movement
    smooth_pos = smooth_mouse_position((screen_x, screen_y))
    
    try:
        mouse_controller.position = smooth_pos
    except Exception as e:
        print(f"Error moving mouse: {e}")


def draw_debug_info(frame, persons, target_person, is_locked):
    """Draw debug visualization on frame"""
    # Draw all detected persons
    if persons:
        for x, y, width, height in persons:
            half_w = width // 2
            half_h = height // 2
            cv2.rectangle(frame, (x - half_w, y - half_h), (x + half_w, y + half_h), (255, 0, 255), 2)  # Magenta
            cv2.circle(frame, (x, y), 5, (255, 0, 255), -1)
    
    # Draw target person (if locked)
    if target_person and is_locked:
        x, y, width, height = target_person
        half_w = width // 2
        half_h = height // 2
        cv2.rectangle(frame, (x - half_w, y - half_h), (x + half_w, y + half_h), (0, 255, 0), 3)  # Green locked
        cv2.circle(frame, (x, y), 8, (0, 255, 0), -1)
    
    # Draw crosshair at center
    h, w = frame.shape[:2]
    cv2.line(frame, (w // 2 - 20, h // 2), (w // 2 + 20, h // 2), (255, 0, 0), 1)
    cv2.line(frame, (w // 2, h // 2 - 20), (w // 2, h // 2 + 20), (255, 0, 0), 1)
    
    # Draw status text
    status = "LOCKED ON" if is_locked else "Ready"
    color = (0, 255, 0) if is_locked else (0, 165, 255)
    cv2.putText(frame, f"Status: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, f"Persons detected: {len(persons) if persons else 0}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, "Hold E to lock-on", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    
    return frame


def main():
    """Main application loop"""
    global is_e_held, yolo_model
    
    print("Starting Lock-On System...")
    print("Loading YOLO model for person/character detection...")
    
    # Load YOLO
    if not YOLO_AVAILABLE:
        print("ERROR: ultralytics not installed. Install with: pip install ultralytics")
        return
    
    print(f"Loading YOLO model: {config.YOLO_MODEL}...")
    try:
        yolo_model = YOLO(config.YOLO_MODEL)
        print("YOLO model loaded successfully!")
    except Exception as e:
        print(f"Error loading YOLO: {e}")
        return
    
    print("Hold 'E' to activate lock-on")
    print("Press 'Q' to exit")
    
    # Start keyboard listener
    listener = start_keyboard_listener()
    
    try:
        frame_count = 0
        start_time = time.time()
        
        while True:
            # Capture screen
            frame = capture_screen(region=config.SCREEN_REGION)
            frame_height, frame_width = frame.shape[:2]
            frame_center = (frame_width // 2, frame_height // 2)
            
            # Detect persons
            persons, _ = detect_persons_yolo(frame)
            target = find_closest_person(persons, frame_center)
            
            # Move mouse if locked on
            if is_e_held and target:
                move_mouse_to_person(target, frame_width, frame_height)
            
            # Draw debug info
            if config.SHOW_DEBUG_WINDOW:
                debug_frame = draw_debug_info(frame.copy(), persons, target, is_e_held)
                
                # Scale for display
                scaled_h = int(debug_frame.shape[0] * config.DEBUG_WINDOW_SCALE)
                scaled_w = int(debug_frame.shape[1] * config.DEBUG_WINDOW_SCALE)
                debug_frame = cv2.resize(debug_frame, (scaled_w, scaled_h))
                
                cv2.imshow("Lock-On System", debug_frame)
            
            # FPS counter
            frame_count += 1
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"FPS: {fps:.1f} | Persons detected: {len(persons)} | Locked: {is_e_held}")
            
            # Check for exit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Exiting...")
                break
    
    except KeyboardInterrupt:
        print("Interrupted by user")
    
    finally:
        listener.stop()
        cv2.destroyAllWindows()
        print("System shutdown complete")


if __name__ == "__main__":
    main()
