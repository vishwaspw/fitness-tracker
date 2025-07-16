"""
Pose Estimator Module

This module provides the PoseEstimator class for detecting and tracking human poses
using MediaPipe Pose. It handles pose detection, landmark tracking, and angle calculations.
"""

import cv2
import mediapipe as mp
import numpy as np

class PoseEstimator:
    """A class for detecting and tracking human poses using MediaPipe."""
    
    def __init__(self, mode=False, model_complexity=1, smooth_landmarks=True,
                 enable_segmentation=False, smooth_segmentation=True,
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """Initialize the pose estimator with MediaPipe Pose.
        
        Args:
            mode (bool): Whether to treat the input images as a batch of static images.
            model_complexity (int): Complexity of the pose landmark model (0, 1, or 2).
            smooth_landmarks (bool): Whether to filter landmarks across different frames.
            enable_segmentation (bool): Whether to predict segmentation mask.
            smooth_segmentation (bool): Whether to filter segmentation across different frames.
            min_detection_confidence (float): Minimum confidence for pose detection.
            min_tracking_confidence (float): Minimum confidence for pose tracking.
        """
        self.mode = mode
        self.model_complexity = model_complexity
        self.smooth_landmarks = smooth_landmarks
        self.enable_segmentation = enable_segmentation
        self.smooth_segmentation = smooth_segmentation
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=self.mode,
            model_complexity=self.model_complexity,
            smooth_landmarks=self.smooth_landmarks,
            enable_segmentation=self.enable_segmentation,
            smooth_segmentation=self.smooth_segmentation,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
    
    def find_pose(self, img, draw=True):
        """Find pose landmarks in the given image.
        
        Args:
            img: Input image in BGR format.
            draw (bool): Whether to draw the pose landmarks on the image.
            
        Returns:
            tuple: (image with landmarks drawn, results from MediaPipe)
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(img_rgb)
        
        if draw and self.results.pose_landmarks:
            self.mp_draw.draw_landmarks(
                img, self.results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS)
                
        return img
    
    def find_position(self, img, draw=True):
        """Extract the positions of all pose landmarks.
        
        Args:
            img: Input image.
            draw (bool): Whether to draw the landmark positions on the image.
            
        Returns:
            list: List of landmark positions with their visibility scores.
        """
        self.lm_list = []
        
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lm_list.append([id, cx, cy, lm.visibility])
                
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
                    
        return self.lm_list
    
    def calculate_angle(self, a, b, c):
        """Calculate the angle between three points.
        
        Args:
            a, b, c: Points in the format [x, y]
            
        Returns:
            float: Angle in degrees.
        """
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
                 np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
