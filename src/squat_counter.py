"""
Squat Counter Module

This module contains the SquatCounter class which extends PoseEstimator
to provide squat counting and form analysis functionality.
"""

import time
import math
import numpy as np
import cv2
import winsound
from datetime import datetime
from .pose_estimator import PoseEstimator

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

class SquatCounter(PoseEstimator):
    """
    A class that extends PoseEstimator to count squats and analyze form.
    """
    
    def __init__(self, mode=False, smooth=True, detection_con=0.5, tracking_con=0.5):
        """
        Initialize the SquatCounter.
        
        Args:
            mode (bool): Whether to treat input as a batch of static images.
            smooth (bool): Whether to smooth landmarks across frames.
            detection_con (float): Minimum confidence for detection.
            tracking_con (float): Minimum confidence for tracking.
        """
        super().__init__(
            mode=mode,
            model_complexity=1,
            smooth_landmarks=smooth,
            enable_segmentation=False,
            min_detection_confidence=detection_con,
            min_tracking_confidence=tracking_con
        )
        
        # Squat tracking variables
        self.count = 0
        self.direction = 0  # 0: standing, 1: squatting
        self.prev_per = 0
        self.bar = 0
        self.color = (0, 0, 255)  # Default red
        self.form_ok = True
        
        # Analytics
        self.analytics = SquatAnalytics()
        self.analytics.start_session()
        
        # Required landmarks for form analysis
        self.required_landmarks = [
            11, 12,  # Shoulders
            23, 24,  # Hips
            25, 26,  # Knees
            27, 28,  # Ankles
            15, 16   # Wrists (for better upper body tracking)
        ]
        
    def check_visibility(self):
        """Check if all required body parts are visible."""
        if not hasattr(self, 'lm_list') or len(self.lm_list) < 29:
            self.analytics.add_feedback("Please ensure full body is visible")
            return False
            
        missing_parts = []
        for landmark_id in self.required_landmarks:
            if landmark_id >= len(self.lm_list) or self.lm_list[landmark_id][3] < 0.3:  # visibility threshold
                part_name = self._get_landmark_name(landmark_id)
                missing_parts.append(part_name)
        
        if missing_parts:
            feedback = f"Adjust position to show: {', '.join(missing_parts)}"
            self.analytics.add_feedback(feedback)
            return False
            
        self.analytics.clear_feedback()
        return True
        
    def _get_landmark_name(self, landmark_id):
        """Convert landmark ID to human-readable name."""
        names = {
            11: "left shoulder",
            12: "right shoulder",
            15: "left wrist",
            16: "right wrist",
            23: "left hip",
            24: "right hip",
            25: "left knee",
            26: "right knee",
            27: "left ankle",
            28: "right ankle"
        }
        return names.get(landmark_id, f"body part {landmark_id}")
    
    def check_knee_alignment(self, img):
        """Check if knees are aligned with toes to prevent injury."""
        if not hasattr(self, 'lm_list') or len(self.lm_list) < 29:
            return True
            
        try:
            # MediaPipe Pose landmark indices
            LEFT_KNEE = 25
            RIGHT_KNEE = 26
            LEFT_ANKLE = 27
            RIGHT_ANKLE = 28
            LEFT_HIP = 23
            RIGHT_HIP = 24
            
            # Get knee and ankle positions [id, x, y, visibility]
            l_knee = self.lm_list[LEFT_KNEE][1:3]  # [x, y]
            r_knee = self.lm_list[RIGHT_KNEE][1:3]
            l_ankle = self.lm_list[LEFT_ANKLE][1:3]
            r_ankle = self.lm_list[RIGHT_ANKLE][1:3]
            l_hip = self.lm_list[LEFT_HIP][1:3]
            r_hip = self.lm_list[RIGHT_HIP][1:3]
            
            # Calculate if knee goes over toes (more accurate check)
            # Check if knee is in front of ankle (x coordinate comparison)
            l_over_toes = l_knee[0] > l_ankle[0] + 20  # Left knee should not go too far over toes
            r_over_toes = r_knee[0] < r_ankle[0] - 20  # Right knee (accounting for mirroring)
            
            # Draw alignment lines for visualization
            cv2.line(img, 
                    (int(l_knee[0]), int(l_knee[1])), 
                    (int(l_ankle[0]), int(l_ankle[1])), 
                    (0, 0, 255) if l_over_toes else (0, 255, 0), 3)
            
            cv2.line(img, 
                    (int(r_knee[0]), int(r_knee[1])), 
                    (int(r_ankle[0]), int(r_ankle[1])), 
                    (0, 0, 255) if r_over_toes else (0, 255, 0), 3)
            
            # Also check if knees are collapsing inward (valgus)
            l_knee_valgus = self._check_knee_valgus(l_hip, l_knee, l_ankle)
            r_knee_valgus = self._check_knee_valgus(r_hip, r_knee, r_ankle)
            
            return not (l_over_toes or r_over_toes or l_knee_valgus or r_knee_valgus)
            
        except Exception as e:
            print(f"Error in check_knee_alignment: {e}")
            return True
            
    def _check_knee_valgus(self, hip, knee, ankle):
        """Check if knee is collapsing inward (valgus)."""
        # Convert points to numpy arrays for vector operations
        hip = np.array(hip)
        knee = np.array(knee)
        ankle = np.array(ankle)
        
        # Calculate vectors
        thigh = knee - hip
        shin = ankle - knee
        
        # Calculate angle between thigh and shin
        angle = self.calculate_angle(hip, knee, ankle)
        
        # If angle is too small (knee collapsing inward)
        return angle < 160  # Degrees
    
    def check_back_angle(self, img):
        """Check if back is straight."""
        if not hasattr(self, 'lm_list') or len(self.lm_list) < 25:
            return True
            
        # Get relevant points (x,y coordinates)
        try:
            # MediaPipe Pose landmark indices
            LEFT_SHOULDER = 11
            RIGHT_SHOULDER = 12
            LEFT_HIP = 23
            RIGHT_HIP = 24
            
            shoulder_l = self.lm_list[LEFT_SHOULDER][1:3]  # [x, y]
            shoulder_r = self.lm_list[RIGHT_SHOULDER][1:3]
            hip_l = self.lm_list[LEFT_HIP][1:3]
            hip_r = self.lm_list[RIGHT_HIP][1:3]
            
            # Calculate midpoints
            shoulder_center = ((shoulder_l[0] + shoulder_r[0])//2, 
                             (shoulder_l[1] + shoulder_r[1])//2)
            hip_center = ((hip_l[0] + hip_r[0])//2, 
                         (hip_l[1] + hip_r[1])//2)
            
            # Calculate angle from vertical (in degrees)
            dx = shoulder_center[0] - hip_center[0]
            dy = shoulder_center[1] - hip_center[1]
            angle = abs(np.degrees(np.arctan2(dy, dx)) - 90)
            
            # Draw back line for visualization
            cv2.line(img, 
                    (int(shoulder_center[0]), int(shoulder_center[1])),
                    (int(hip_center[0]), int(hip_center[1])),
                    (0, 255, 0) if angle < 15 else (0, 0, 255), 3)
            
            return angle < 15  # Allow 15 degrees from vertical
            
        except Exception as e:
            print(f"Error in check_back_angle: {e}")
            return True
    
    def count_squats(self, img):
        """
        Count squats and provide feedback.
        
        Args:
            img: Input image frame
            
        Returns:
            tuple: (image, percentage, bar, color, form_ok, form_feedback)
        """
        # First check visibility of required body parts
        if not self.check_visibility():
            return img, 0, 0, (0, 0, 255), False, "Adjust position to show all body parts"
            
        # Get the required landmarks for angle calculation
        left_hip = self.lm_list[23][1:3]  # x,y coordinates
        left_knee = self.lm_list[25][1:3]
        left_ankle = self.lm_list[27][1:3]
        right_hip = self.lm_list[24][1:3]
        right_knee = self.lm_list[26][1:3]
        right_ankle = self.lm_list[28][1:3]
        
        # Calculate angles for both legs
        left_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
        right_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
        
        # Use the average angle of both legs
        angle = (left_angle + right_angle) / 2
        
        # Convert angle to percentage (0-100%)
        per = np.interp(angle, [90, 180], [100, 0])
        per = max(0, min(100, per))
        
        # Check form
        back_ok = self.check_back_angle(img)
        knees_ok = self.check_knee_alignment(img)
        self.form_ok = back_ok and knees_ok
        feedback_messages = []
        
        if not back_ok:
            feedback_messages.append("Keep back straight")
        if not knees_ok:
            feedback_messages.append("Align knees with feet")
            
        # Map percentage to bar height
        bar = np.interp(per, [0, 100], [650, 100])
        
        # Check for squat completion
        if per >= 80:  # Squat down position
            if self.direction == 0:
                self.direction = 1
                self.color = (0, 255, 0) if self.form_ok else (0, 165, 255)  # Orange for bad form
        
        if per <= 20:  # Standing position
            if self.direction == 1:
                self.direction = 0
                self.count += 1
                self.color = (0, 0, 255)
                # Log the rep with form check
                self.analytics.add_rep(per, self.form_ok)
        
        # Update previous percentage
        self.prev_per = per
        
        # Add feedback to analytics
        for msg in feedback_messages:
            self.analytics.add_feedback(msg)
            
        # Get the most recent feedback to display
        current_feedback = self.analytics.feedback_messages[-1] if self.analytics.feedback_messages else "Good form!"
        
        return img, per, bar, self.color, self.form_ok, current_feedback
