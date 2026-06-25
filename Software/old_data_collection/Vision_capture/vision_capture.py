import cv2
import mediapipe as mp
import math
import time

# Initialise MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

print("Starting vision dashboard for right-hand feature extraction...")

while cap.isOpened():
    success, image = cap.read()
    if not success: 
        break

    current_timestamp = time.time()
    h, w, _ = image.shape
    
    # Process RGB frame before flipping for accurate handedness detection
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    image = cv2.flip(image, 1)

    cv2.putText(image, f"Timestamp: {current_timestamp:.3f}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            
            if handedness.classification[0].label == "Right":
                lm = hand_landmarks.landmark
                
                # Map normalised coordinates to flipped pixel coordinates (thumb tip)
                t_x = int((1 - lm[4].x) * w) 
                t_y = int(lm[4].y * h)
                
                finger_tips = [8, 12, 16, 20]
                labels = ["Index", "Mid", "Ring", "Pinky"]
                
                for i, tip_idx in enumerate(finger_tips):
                    f_x = int((1 - lm[tip_idx].x) * w)
                    f_y = int(lm[tip_idx].y * h)
                    
                    # Calculate Euclidean distance
                    dist = math.hypot(f_x - t_x, f_y - t_y)
                    
                    cv2.line(image, (t_x, t_y), (f_x, f_y), (0, 0, 255), 2)
                    cv2.putText(image, f"{labels[i]}: {dist:.1f}px", (f_x, f_y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow('TetherIA - Feature Extraction & Labelling', image)
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break

cap.release()
cv2.destroyAllWindows()