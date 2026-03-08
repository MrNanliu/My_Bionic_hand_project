import cv2
import mediapipe as mp
import math

# 1. 初始化
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

print("🚀 视觉仪表盘启动！专注于全维度右手特征提取...")

while cap.isOpened():
    success, image = cap.read()
    if not success: break

    # 画面预处理
    image = cv2.flip(image, 1) # 水平翻转，符合镜子习惯
    h, w, _ = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            
            # 🌟 仅处理右手 (根据你的代码逻辑)
            if handedness.classification[0].label == "Right":
                # 画出原始骨骼线
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                lm = hand_landmarks.landmark
                # 拇指尖 (点 4)
                t_x, t_y = int(lm[4].x * w), int(lm[4].y * h)
                
                # 定义要追踪的指尖编号
                finger_tips = [8, 12, 16, 20]
                labels = ["Index", "Mid", "Ring", "Pinky"]
                
                for i, tip_idx in enumerate(finger_tips):
                    # 获取指尖像素坐标
                    f_x, f_y = int(lm[tip_idx].x * w), int(lm[tip_idx].y * h)
                    
                    # 计算归一化距离 (用于 IL 训练)
                    dist = math.hypot(lm[tip_idx].x - lm[4].x, lm[tip_idx].y - lm[4].y)
                    
                    # 🌟 绘制红色辅助线
                    cv2.line(image, (t_x, t_y), (f_x, f_y), (0, 0, 255), 2)
                    
                    # 🌟 在屏幕上显示数据仪表盘
                    cv2.putText(image, f"{labels[i]}: {dist:.2f}", (f_x, f_y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow('TetherIA - Real-time IL Dashboard', image)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()