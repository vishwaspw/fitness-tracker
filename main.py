#!/usr/bin/env python3
"""
Squat Counter - Main Application

This is the main entry point for the Squat Counter application.
It initializes the camera, sets up the pose detector, and runs the main loop.
"""

import os
import sys
import cv2
import time
from datetime import datetime
from src.squat_counter import SquatCounter
from src.pose_estimator import PoseEstimator
from src.utils import draw_ui, save_session_data

def draw_ui(img, detector, per, bar, color, form_ok, form_feedback, p_time):
    """
    Draw the user interface elements on the frame.
    
    Args:
        img: The image frame to draw on
        detector: The SquatCounter instance
        per: Squat completion percentage
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
        "4. Squat until thighs are parallel to ground",
        "5. Press 'q' to quit"
    ]
    
    for i, line in enumerate(instructions):
        y_pos = h - 150 + (i * 25)
        cv2.putText(img, line, (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return img, p_time

def main():
    """Main function to run the Squat Counter application."""
    print("\n=== Squat Counter ===")
    print("Initializing camera...")
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return 1
    
    # Set camera resolution and properties for better full-body tracking
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    
    # Create SquatCounter instance
    detector = SquatCounter(detection_con=0.7, tracking_con=0.7)
    
    # FPS variables
    p_time = 0
    frame_count = 0
    start_time = time.time()
    zoom_level = 0.7  # Start with zoomed out view
    
    # Create window with resizable property
    cv2.namedWindow("Squat Counter", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Squat Counter", 1280, 720)
    
    print("\n=== Instructions ===")
    print("1. Stand 6-8 feet away from the camera")
    print("2. Ensure good lighting in the room")
    print("3. Face the camera with your full body visible")
    print("4. Press 'q' to quit\n")
    
    print("Starting squat counter...")
    
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to capture image from webcam.")
            break
        
        # Apply zoom
        if zoom_level != 1.0:
            h, w = img.shape[:2]
            center_x, center_y = w // 2, h // 2
            new_w, new_h = int(w / zoom_level), int(h / zoom_level)
            x1 = max(0, center_x - new_w // 2)
            y1 = max(0, center_y - new_h // 2)
            x2 = min(w, center_x + new_w // 2)
            y2 = min(h, center_y + new_h // 2)
            img = img[y1:y2, x1:x2]
            img = cv2.resize(img, (w, h))
            
        # Process image
        img = cv2.flip(img, 1)  # Mirror the image
        display_img = img.copy()
        
        # Process pose detection
        img = detector.find_pose(img, draw=True)
        lm_list = detector.find_position(img, draw=True)
        
        # Count squats and get feedback
        img, per, bar, color, form_ok, form_feedback = detector.count_squats(img)
        
        # Draw UI elements
        display_img, p_time = draw_ui(display_img, detector, per, bar, color, 
                                    form_ok, form_feedback, p_time)
        
        # Display zoom level and instructions
        cv2.putText(display_img, f'Zoom: {zoom_level:.1f}x', (20, 40), 
                   cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        
        # Display the image
        cv2.imshow("Squat Counter", display_img)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Quit
            break
        elif key == ord('+'):  # Zoom in
            zoom_level = min(1.5, zoom_level + 0.1)
        elif key == ord('-'):  # Zoom out
            zoom_level = max(0.5, zoom_level - 0.1)
    
    # Save session data
    save_session_data(detector.analytics)
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    print("\nSession ended. Workout data saved.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
