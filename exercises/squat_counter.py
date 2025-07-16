"""
Squat Counter Module

This module contains the SquatCounter class which extends PoseEstimator
to provide squat counting and form analysis functionality.
"""

import cv2
import numpy as np
import time
from datetime import datetime
from models.pose_estimator import PoseEstimator
from .base_exercise import BaseExercise

class SquatAnalytics:
    """Class to track and analyze workout statistics."""
    
    def __init__(self):
        self.session_start = None
        self.rep_times = []
        self.depths = []
        self.form_errors = []
        self.feedback_messages = []
        self.last_beep_time = 0
        self.beep_cooldown = 1.0  # seconds between beeps
        
    def play_beep(self, frequency=1000, duration=200):
        """Play a beep sound if not in cooldown."""
        current_time = time.time()
        if current_time - self.last_beep_time > self.beep_cooldown:
            try:
                winsound.Beep(frequency, duration)
                self.last_beep_time = current_time
            except Exception as e:
                print(f"Could not play beep sound: {e}")
    
    def add_feedback(self, message):
        """Add a feedback message and play a beep."""
        if message and message not in self.feedback_messages:
            self.feedback_messages.append(message)
            self.play_beep()
            
    def clear_feedback(self):
        """Clear all feedback messages."""
        self.feedback_messages.clear()
        
    def start_session(self):
        """Start a new workout session."""
        self.session_start = datetime.now()
        
    def add_rep(self, depth, form_ok=True):
        """
        Add a rep to the workout session.
        
        Args:
            depth (float): Depth of the squat as a percentage
            form_ok (bool): Whether the form was correct
        """
        self.rep_times.append(time.time())
        self.depths.append(depth)
        self.form_errors.append(not form_ok)
        
    def get_stats(self):
        """Calculate and return workout statistics."""
        if not self.rep_times:
            return {}
            
        total_reps = len(self.rep_times)
        avg_depth = np.mean(self.depths) if self.depths else 0
        good_form_percentage = (1 - sum(self.form_errors) / total_reps) * 100 if total_reps > 0 else 100
        
        # Calculate reps per minute
        if len(self.rep_times) > 1:
            time_elapsed = self.rep_times[-1] - self.rep_times[0]
            reps_per_min = (len(self.rep_times) - 1) / (time_elapsed / 60)
        else:
            reps_per_min = 0
            
        return {
            'total_reps': total_reps,
            'avg_depth': avg_depth,
            'good_form_percentage': good_form_percentage,
            'reps_per_min': reps_per_min,
            'session_duration': (datetime.now() - self.session_start).total_seconds() / 60 if self.session_start else 0
        }

class SquatCounter(BaseExercise, PoseEstimator):
    """
    A class that extends PoseEstimator to count squats and analyze form.
    """
    
    def __init__(self):
        """Initialize the squat counter."""
        BaseExercise.__init__(self, "Squat")
        PoseEstimator.__init__(self)
        
        # Squat-specific parameters
        self.direction = 0
        self.prev_per = 0
        self.count = 0
        self.form_ok = True
        self.feedback = "Start with standing position"
        
        # Thresholds
        self.SQUAT_ANGLE = 140
        self.BACK_ANGLE_THRESHOLD = 15
        self.KNEE_ANGLE_THRESHOLD = 160
        
        # Analytics
        self.analytics = SquatAnalytics()
        self.analytics.start_session()
        
    def process_frame(self, frame):
        """
        Process a single frame for squat counting.
        
        Args:
            frame: Input image frame
            
        Returns:
            tuple: (processed_frame, percentage, bar, color, form_ok, feedback)
        """
        try:
            # Get pose landmarks
            frame = self.find_pose(frame)
            lm_list = self.find_position(frame)
            
            if len(lm_list) == 0:
                return frame, 0, 0, (0, 0, 255), False, "No person detected"
                
            # Calculate angles for squat detection
            left_leg_angle = self.calculate_angle(
                lm_list[23][1:3],  # Left hip
                lm_list[25][1:3],  # Left knee
                lm_list[27][1:3]   # Left ankle
            )
            
            right_leg_angle = self.calculate_angle(
                lm_list[24][1:3],  # Right hip
                lm_list[26][1:3],  # Right knee
                lm_list[28][1:3]   # Right ankle
            )
            
            # Calculate back angle
            back_angle = self.calculate_angle(
                lm_list[11][1:3],  # Left shoulder
                lm_list[23][1:3],  # Left hip
                lm_list[25][1:3]   # Left knee
            )
            
            # Calculate percentage of squat completion
            avg_leg_angle = (left_leg_angle + right_leg_angle) / 2
            per = np.interp(avg_leg_angle, 
                          (self.SQUAT_ANGLE, 180), 
                          (100, 0))
            
            # Check form
            self.form_ok = True
            self.feedback = "Good form!"
            
            # Check back angle
            if back_angle < 160:
                self.form_ok = False
                self.feedback = "Keep your back straight"
            
            # Check knee alignment
            knee_angle = self.calculate_angle(
                lm_list[23][1:3],  # Left hip
                lm_list[25][1:3],  # Left knee
                lm_list[27][1:3]   # Left ankle
            )
            
            if knee_angle < self.KNEE_ANGLE_THRESHOLD:
                self.form_ok = False
                self.feedback = "Keep your knees behind your toes"
            
            # Check for squat completion
            if per == 100:
                if self.direction == 0:
                    self.count += 0.5
                    self.direction = 1
            elif per == 0:
                if self.direction == 1:
                    self.count += 0.5
                    self.direction = 0
            
            # Calculate progress bar
            bar = np.interp(per, (0, 100), (650, 100))
            
            # Set color based on form
            color = (0, 255, 0) if self.form_ok else (0, 0, 255)
            
            # Add feedback to analytics
            self.analytics.add_feedback(self.feedback)
            
            # Log the rep with form check
            self.analytics.add_rep(per, self.form_ok)
            
            return frame, per, bar, color, self.form_ok, self.feedback
            
        except Exception as e:
            print(f"Error in process_frame: {e}")
            return frame, 0, 0, (0, 0, 255), False, "Error processing frame"
