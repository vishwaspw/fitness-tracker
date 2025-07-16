# Squat Counter with Pose Detection

A real-time squat counter application that uses computer vision to track and analyze your squats. Built with Python, OpenCV, and MediaPipe.

![Demo](assets/demo.gif)

## Features

- 🏋️ Real-time squat counting with pose estimation
- 📊 Performance metrics (reps, depth, form analysis)
- 🎯 Form feedback and correction
- 📈 Session history and progress tracking
- 🎮 Simple keyboard controls
- 📱 Responsive UI with zoom functionality

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/squat-counter.git
   cd squat-counter
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Position yourself:
   - Stand 6-8 feet away from your webcam
   - Ensure good lighting
   - Make sure your full body is visible

3. Controls:
   - `+` : Zoom in
   - `-` : Zoom out
   - `q` : Quit application

## Project Structure

```
squat-counter/
├── main.py              # Main application entry point
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── src/                 # Source code
│   ├── __init__.py
│   ├── pose_estimator.py  # Pose detection logic
│   ├── squat_counter.py   # Squat counter logic
│   └── utils.py          # Utility functions
├── assets/              # Images and demo files
└── workout_data/        # Saved workout sessions
```

## Requirements

- Python 3.7+
- OpenCV
- MediaPipe
- NumPy
- Pandas

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for the amazing pose estimation model
- [OpenCV](https://opencv.org/) for computer vision capabilities
- All contributors who helped improve this project
