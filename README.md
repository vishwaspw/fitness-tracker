# Fitness Tracker with Pose Detection

This project uses **MediaPipe** and **OpenCV** to build an intelligent exercise tracker that uses **pose estimation** to track body joints and count reps in real time. It's an excellent example of how computer vision can be used in fitness and health applications.

---

## 🏋️‍♂️ Features
- Real-time pose detection for multiple exercises (Push-ups, Squats)
- Form correction feedback
- Repetition counting
- Performance analytics
- Cross-platform compatibility

## 📦 Project Structure
```
fitness-tracker/
├── exercises/           # Exercise implementations
│   ├── base_exercise.py # Base exercise class
│   ├── squat_counter.py # Squat counter implementation
│   └── pushup_counter.py# Push-up counter implementation
├── models/              # ML models
│   └── pose_estimator.py# Pose estimation logic
├── utils/               # Utility functions
│   ├── ui_utils.py      # UI drawing utilities
│   └── file_utils.py    # File operation utilities
├── main.py              # Main application
└── requirements.txt     # Python dependencies
```

## 🧠 How the Project Works (Detailed Walkthrough)

### 1. Pose Detection
- Uses MediaPipe's pose estimation model to detect 33 key body points
- Tracks joints in real-time with high accuracy
- Processes each frame to analyze body position

### 2. Exercise Recognition
- Detects specific exercise patterns (push-ups, squats)
- Monitors joint angles and positions
- Provides real-time feedback on form

### 3. Rep Counting Logic
```python
# Simplified rep counting logic
if per >= 95:  # Down position
    if dir == 0:
        count += 0.5
        dir = 1
elif per <= 5:  # Up position
    if dir == 1:
        count += 0.5
        dir = 0
```
- Tracks full range of motion
- Prevents false counts
- Adjustable sensitivity

### 4. Real-time Feedback
- Visual progress bar
- Form correction hints
- Repetition counter
- FPS display

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Webcam
- Required packages (install via `requirements.txt`)

### Installation
```bash
# Clone the repository
git clone https://github.com/vishwaspw/fitness-tracker.git
cd fitness-tracker

# Install dependencies
pip install -r requirements.txt
```

### Usage
```bash
# Start with push-ups
python main.py --exercise pushup

# Or try squats
python main.py --exercise squat
```

## ✅ Project Summary
| Feature | Description |
|---------|-------------|
| Library | MediaPipe, OpenCV, NumPy |
| Input | Live webcam video feed |
| Output | Pose landmarks, progress bar, rep count |
| ML Model | MediaPipe Pose Estimation |
| Applications | Fitness, Rehab, Posture Correction |

## 🚀 Future Ideas
- Add sound feedback for each rep
- Save history of workout sessions
- Detect poor form (e.g., bent knees, arched back)
- Export stats (CSV, Graphs)
- Support for more exercises

## 👏 Credits
- Original concept and implementation: [Abdelkareem Hossam](https://github.com/abdelkareem-ahmed)
- Enhanced and modularized by: [Vishwas R](https://github.com/vishwaspw)
- Squat counter implementation: [Vishwas R](https://github.com/vishwaspw)

## 🙏 Acknowledgments
- Thanks to the MediaPipe team for their amazing pose estimation model
- Inspired by the fitness technology community

---

*Feel free to improve or extend it for other exercises like jumping jacks, pull-ups, or yoga!*
