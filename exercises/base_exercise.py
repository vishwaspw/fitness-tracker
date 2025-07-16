"""
Base Exercise Class

This module contains the BaseExercise class which provides common functionality
for all exercise trackers.
"""

import time
import cv2
import numpy as np

class BaseExercise:
    """Base class for all exercise trackers."""
    
    def __init__(self, name):
        """
        Initialize the base exercise.
        
        Args:
            name (str): Name of the exercise
        """
        self.name = name
        self.count = 0
        self.direction = 0
        self.prev_per = 0
        self.form_ok = True
        self.feedback = ""
        
    def process_frame(self, frame):
        """
        Process a single frame of the exercise.
        
        Args:
            frame: Input image frame
            
        Returns:
            tuple: (processed_frame, count, percentage, bar, color, form_ok, feedback)
        """
        return frame, 0, 0, 0, (0, 0, 0), True, ""
        
    def calculate_angle(self, a, b, c):
        """
        Calculate the angle between three points.
        
        Args:
            a: First point (x, y)
            b: Middle point (x, y)
            c: End point (x, y)
            
        Returns:
            float: Angle in degrees
        """
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def draw_progress_bar(self, img, per, bar, color):
        """
        Draw a progress bar on the image.
        
        Args:
            img: Input image
            per: Percentage complete
            bar: Bar height
            color: Bar color (BGR)
            
        Returns:
            Image with progress bar
        """
        h, w, _ = img.shape
        
        # Draw the outline of the bar
        cv2.rectangle(img, (w-100, 100), (w-25, 550), (200, 200, 200), 3)
        # Draw the filled portion
        cv2.rectangle(img, (w-100, int(bar)), (w-25, 550), color, cv2.FILLED)
        # Draw the percentage text
        cv2.putText(img, f'{int(per)}%', (w-150, 80),
                   cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        
        return img
