"""
Utility functions for the Squat Counter application.

This module provides helper functions for drawing UI elements and saving workout data.
"""

import os
import csv
import cv2
import numpy as np
from datetime import datetime

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
    
    # Draw progress bar
    cv2.rectangle(img, (w-100, 100), (w-25, h-100), (0, 255, 0), 3)
    cv2.rectangle(img, (w-100, int(bar)), (w-25, h-100), color, cv2.FILLED)
    cv2.putText(
        img, 
        f'{int(per)}%', 
        (w-150, 80),
        cv2.FONT_HERSHEY_PLAIN, 
        2, 
        color, 
        2
    )
    
    # Display count
    cv2.rectangle(img, (20, 20), (300, 120), (0, 255, 0), cv2.FILLED)
    cv2.putText(
        img, 
        f'Count: {int(detector.count)}', 
        (30, 80), 
        cv2.FONT_HERSHEY_PLAIN, 
        3, 
        (255, 0, 0), 
        3
    )
    
    # Display form feedback
    feedback_color = (0, 255, 0) if form_ok else (0, 0, 255)
    cv2.putText(
        img, 
        form_feedback, 
        (w//2 - 150, 50), 
        cv2.FONT_HERSHEY_SIMPLEX, 
        1, 
        feedback_color, 
        2
    )
    
    # Display stats
    stats = detector.analytics.get_stats()
    if stats:
        cv2.putText(
            img, 
            f"Avg Depth: {stats['avg_depth']:.1f}%", 
            (20, h-100), 
            cv2.FONT_HERSHEY_PLAIN, 
            2, 
            (255, 255, 255), 
            2
        )
        cv2.putText(
            img, 
            f"Good Form: {stats['good_form_percentage']:.1f}%", 
            (20, h-70), 
            cv2.FONT_HERSHEY_PLAIN, 
            2, 
            (255, 255, 255), 
            2
        )
        cv2.putText(
            img, 
            f"Rate: {stats['reps_per_min']:.1f}/min", 
            (20, h-40), 
            cv2.FONT_HERSHEY_PLAIN, 
            2, 
            (255, 255, 255), 
            2
        )

def save_session_data(analytics):
    """
    Save workout session data to a CSV file.
    
    Args:
        analytics: The SquatAnalytics instance
    """
    if not os.path.exists('workout_data'):
        os.makedirs('workout_data')
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'workout_data/session_{timestamp}.csv'
    
    stats = analytics.get_stats()
    data = {
        'timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        'total_reps': [stats.get('total_reps', 0)],
        'avg_depth': [stats.get('avg_depth', 0)],
        'good_form_percentage': [stats.get('good_form_percentage', 0)],
        'reps_per_min': [stats.get('reps_per_min', 0)],
        'session_duration_min': [stats.get('session_duration', 0)]
    }
    
    # Save to CSV
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data.keys())
        writer.writerow([data[key][0] for key in data])
    
    print(f"Workout data saved to {filename}")

def get_workout_history():
    """
    Get a list of all workout sessions.
    
    Returns:
        list: List of dictionaries containing session data
    """
    if not os.path.exists('workout_data'):
        return []
        
    sessions = []
    for filename in os.listdir('workout_data'):
        if filename.endswith('.csv'):
            with open(os.path.join('workout_data', filename), 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sessions.append(dict(row))
    
    return sorted(sessions, key=lambda x: x['timestamp'], reverse=True)
