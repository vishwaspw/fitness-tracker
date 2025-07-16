"""
UI Utilities

This module contains utility functions for drawing UI elements on frames.
"""

import cv2
import time

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
        
    Returns:
        tuple: (frame with UI elements, current_time)
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
    cv2.putText(img, f'FPS: {int(fps)}', (w-150, 30),
               cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
    
    # Draw instructions
    instructions = [
        "INSTRUCTIONS:",
        "1. Stand 6-8 feet from camera",
        "2. Keep feet shoulder-width apart",
        "3. Keep back straight",
        f"4. Perform {detector.name} with proper form",
        "5. Press 'q' to quit"
    ]
    
    for i, line in enumerate(instructions):
        y_pos = h - 150 + (i * 25)
        cv2.putText(img, line, (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return img, c_time
