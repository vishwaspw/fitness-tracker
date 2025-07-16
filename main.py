#!/usr/bin/env python3
"""
Fitness Tracker - Main Application

This is the main entry point for the Fitness Tracker application.
It supports multiple exercises including push-ups and squats.
"""

import argparse
import cv2
import time
import sys
from exercises.pushup_counter import PushupCounter
from exercises.squat_counter import SquatCounter
from models.pose_estimator import PoseEstimator
from utils.ui_utils import draw_ui

def draw_ui(img, detector, per, bar, color, form_ok, form_feedback, p_time):
    """
    Draw the user interface elements on the frame.
    
    Args:
        img: The image frame to draw on
        detector: The exercise counter instance
        per: Exercise completion percentage
        bar: Progress bar height
        color: Color for the progress bar
        form_ok: Boolean indicating if form is correct
        form_feedback: Text feedback about form
        p_time: Previous time for FPS calculation
    """
    h, w, _ = img.shape
    
    # Draw semi-transparent overlay for better text visibility
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
    alpha = 0.4  # Transparency factor
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    
    # Draw progress bar with border
    cv2.rectangle(img, (w-100, 100), (w-25, h-100), (200, 200, 200), 3)
    cv2.rectangle(img, (w-100, int(bar)), (w-25, h-100), color, cv2.FILLED)
    cv2.rectangle(img, (w-100, 100), (w-25, h-100), (255, 255, 255), 1)
    
    # Draw percentage text
    cv2.putText(img, f'{int(per)}%', (w-150, 80),
               cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    
    # Draw rep counter with background
    cv2.rectangle(img, (20, 20), (300, 120), (0, 0, 0), -1)
    cv2.rectangle(img, (20, 20), (300, 120), (0, 255, 0), 2)
    cv2.putText(img, f'REPS: {int(detector.count)}', (40, 80), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    
    # Draw form feedback with background
    if form_feedback:
        text_size = cv2.getTextSize(form_feedback, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        text_x = (w - text_size[0]) // 2
        cv2.rectangle(img, 
                     (text_x - 10, 20), 
                     (text_x + text_size[0] + 10, 60), 
                     (0, 0, 0), -1)
        cv2.rectangle(img, 
                     (text_x - 10, 20), 
                     (text_x + text_size[0] + 10, 60), 
                     (0, 255, 0) if form_ok else (0, 0, 255), 2)
        cv2.putText(img, form_feedback, (text_x, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
                   (255, 255, 255), 2)
    
    # Draw FPS
    c_time = time.time()
    fps = 1 / (c_time - p_time)
    p_time = c_time
    cv2.putText(img, f'FPS: {int(fps)}', (w-150, 30),
               cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
    
    # Draw instructions
    instructions = [
        "INSTRUCTIONS:",
        "1. Stand 6-8 feet from camera",
        "2. Keep feet shoulder-width apart",
        "3. Keep back straight",
        "4. Perform exercise until completion",
        "5. Press 'q' to quit"
    ]
    
    for i, line in enumerate(instructions):
        y_pos = h - 150 + (i * 25)
        cv2.putText(img, line, (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return img, p_time

def main():
    """Main function to run the Fitness Tracker application."""
    print("\n=== Fitness Tracker ===")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fitness Tracker')
    parser.add_argument('--exercise', type=str, choices=['pushup', 'squat'], 
                      default='squat', help='Exercise to track')
    parser.add_argument('--camera', type=int, default=0, 
                      help='Camera device index (default: 0)')
    args = parser.parse_args()
    
    print(f"\nStarting {args.exercise} counter...")
    print("Press 'q' to quit\n")
    
    # Initialize webcam
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return 1
    
    # Set camera resolution and properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    
    # Initialize the selected exercise
    if args.exercise == 'pushup':
        detector = PushupCounter()
    else:  # default to squat
        detector = SquatCounter()
    
    # FPS variables
    p_time = 0
    c_time = 0
    
    # Main loop
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to capture image from webcam.")
            break
        
        # Mirror the image
        img = cv2.flip(img, 1)
        display_img = img.copy()
        
        # Process the frame
        try:
            # Process the exercise
            img, per, bar, color, form_ok, feedback = detector.process_frame(img)
            
            # Draw UI elements
            display_img, p_time = draw_ui(
                display_img, detector, per, bar, color, 
                form_ok, feedback, p_time
            )
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            continue
        
        # Display the image
        cv2.imshow("Fitness Tracker", display_img)
        
        # Check for quit key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    print("\nSession ended.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
