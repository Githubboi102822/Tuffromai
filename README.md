# Tuff Bot - AI Lock-On System

A real-time AI-powered screen capture system that detects people/characters and locks your mouse cursor onto them when you hold the 'E' key. Features a clean tabbed GUI for easy configuration.

## Features

- **AI-based Person Detection** - Uses YOLO v8 to detect people/characters in games (CS:GO, Valorant, etc.)
- **Keyboard Lock-On** - Hold 'E' to activate targeting
- **Smooth Mouse Control** - Configurable smoothing for natural tracking
- **Clean GUI Interface** - Tabbed settings with real-time stats
- **Model Selection** - Choose between nano (fast), small (balanced), or medium (accurate) YOLO models
- **Debug Visualization** - Live preview of detections and lock-on status

## Installation

1. Install Python 3.8+
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

**Launch with GUI:**
```bash
python launcher.py
```

Or directly:
```bash
python gui.py
```

**Controls:**
- **Hold E** - Activate lock-on targeting
- **Q** - Exit the bot
- Adjust all settings in the GUI tabs before clicking "Run Tuff Bot"

## GUI Tabs

### 🎯 Lock-On Tab
- **Mouse Smoothing** - Adjust how smooth the cursor follows targets (0-1, higher = smoother)
- **Show Debug Window** - Toggle real-time detection visualization

### 🔍 Detection Tab
- **YOLO Model** - Select model size (nano = fastest, medium = most accurate)
- **Confidence Threshold** - How confident the AI needs to be to detect a person (0.1-1.0)
- **Person Size Filter** - Minimum width/height to count as a valid target

### ⚙️ Advanced Tab
- **Debug Window Scale** - Resize the preview window
- **IOU Threshold** - Intersection over Union for object detection

### 📊 Stats Tab
- **Live FPS** - Current frames per second
- **Persons Detected** - Number of people found in current frame
- **Lock-On Status** - Whether targeting is active
- **Status Messages** - Bot state and information

## Configuration

All settings can be adjusted through the GUI. Default values are in `config.py`:

- `YOLO_MODEL` - Model to use (nano/small/medium)
- `YOLO_CONFIDENCE` - Detection confidence threshold
- `MOUSE_SMOOTHING` - Mouse movement smoothing (0-1)
- `MIN_PERSON_WIDTH` / `MIN_PERSON_HEIGHT` - Size filtering

## How It Works

1. **Screen Capture** - Continuously captures screen at high speed (MSS)
2. **AI Detection** - YOLO v8 detects people/characters in real-time
3. **Target Selection** - Picks the closest person to screen center
4. **Mouse Tracking** - Moves cursor smoothly to follow the target
5. **Keyboard Input** - Monitors 'E' key to enable/disable lock-on

## Supported Games

Works with any game that has visible characters:
- Counter-Strike: Global Offensive (CS:GO)
- Valorant
- Call of Duty
- Apex Legends
- Overwatch
- And many more!

## Troubleshooting

**No detections:**
- Lower the confidence threshold in the Detection tab
- Ensure characters are clearly visible
- Try a larger YOLO model (medium instead of nano)

**Jittery mouse:**
- Increase Mouse Smoothing value (try 0.8-0.9)
- Increase Debug Window Scale

**Slow performance:**
- Use nano model instead of medium
- Increase Debug Window Scale
- Close other applications

## Technical Stack

- **PyQt5** - GUI interface
- **mss** - Ultra-fast screen capture
- **OpenCV (cv2)** - Image processing
- **ultralytics (YOLO v8)** - AI object detection
- **pynput** - Keyboard and mouse control
- **NumPy** - Numerical operations

