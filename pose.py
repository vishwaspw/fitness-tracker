import cv2
import mediapipe as mp
import time
import math


class poseDetector():
    
    def __init__(self, mode=False, smooth=True, detectionCon = 0.5, trackingCon=0.5):
        
        self.mode = mode
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackingCon = trackingCon
        

        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(
            static_image_mode = self.mode,
            smooth_landmarks = self.smooth,
            min_detection_confidence = self.detectionCon,
            min_tracking_confidence = self.trackingCon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findPose(self, img, draw=True):
    
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
    
        if draw and self.results.pose_landmarks:
            self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
            
        return img
    
    def findPosition(self, img, draw=True):
        self.lmList = []
        if  self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                self.lmList.append([id, cx, cy])
                
                if draw: cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
                    
        return self.lmList
    
    def findAngle(self, img, p1, p2, p3, draw=True):
        # Get the points
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        x3, y3 = self.lmList[p3][1], self.lmList[p3][2]
        
        # Calculate the angle
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
        
        if angle > 180: 
            angle = 360 - angle
        elif angle < 0:
            angle = -angle
        
        
        # Draw
        if draw:
            cv2.circle(img, (x1, y1), 10, (64, 127, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (64, 127, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 10, (64, 127, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (64, 127, 255))
            cv2.circle(img, (x2, y2), 15, (64, 127, 255))
            cv2.circle(img, (x3, y3), 15, (64, 127, 255))
            cv2.line(img, (x1, y1), (x2, y2), (255, 127, 64), 3)
            cv2.line(img, (x2, y2), (x3, y3), (255, 127, 64), 3)
            # cv2.putText(img, str(int(angle)), (x2 - 20, y2 + 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 127, 0), 2)
            
        return angle
        
def main():
    cTime, pTime = 0, 0
    cam = cv2.VideoCapture(0)
    
    detector = poseDetector()

    while True:
        success, img = cam.read()
        img = detector.findPose(img, draw=False)
        lmList = detector.findPosition(img, draw=False)
        if (len(lmList)): cv2.circle(img, (lmList[14][1], lmList[14][2]), 8, (255, 0, 255), cv2.FILLED)
        
        cTime = time.time()
        fps = 1/(cTime - pTime)
        pTime = cTime
        cv2.putText(img, ("fps: " + str(int(fps))), (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 127, 255), 2)
        
        cv2.imshow("Image", img)
        cv2.waitKey(1)
    
    
if __name__ == "__main__":
    main()