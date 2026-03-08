import cv2
import mediapipe as mp
import math
import serial
import csv
import time
import os

# --- 1. 配置区域 ---
# 请根据你的实际情况修改串口号 (可以在终端输入 ls /dev/cu.* 查看)
SERIAL_PORT = '/dev/cu.usbserial-0001' # 👈 替换为你的 ESP32 串口号
BAUD_RATE = 115200
# 自动创建保存路径
SAVE_PATH = "collected_data"
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)
FILENAME = f"{SAVE_PATH}/il_data_{int(time.time())}.csv"

# --- 2. 初始化硬件与 AI ---
# 初始化串口
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    print(f"✅ 串口 {SERIAL_PORT} 已连接")
except:
    print(f"❌ 无法连接串口，请检查端口号！")
    exit()

# 初始化 MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

# --- 3. 准备 CSV 文件 ---
# 自动创建并写入表头
with open(FILENAME, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Timestamp', 'sEMG_Value', 'Index_Dist', 'Mid_Dist', 'Ring_Dist', 'Pinky_Dist'])

print(f"📊 数据将保存至: {FILENAME}")
print("🚀 开始录制！按下 'q' 键停止并保存...")

while cap.isOpened():
    success, image = cap.read()
    if not success: break

    # 画面预处理
    image = cv2.flip(image, 1)
    h, w, _ = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    # A. 读取肌电信号 (来自 ESP32)
    emg_value = 0
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        if line.isdigit(): # 确保读到的是数字
            emg_value = int(line)

    # B. 读取视觉信号 (来自 MediaPipe)
    distances = [0.0, 0.0, 0.0, 0.0] # 默认值
    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            if handedness.classification[0].label == "Right":
                lm = hand_landmarks.landmark
                t_tip = lm[4] # 拇指
                # 计算 4 根手指的捏合距离
                distances = [
                    math.hypot(lm[8].x - t_tip.x, lm[8].y - t_tip.y),  # 食指
                    math.hypot(lm[12].x - t_tip.x, lm[12].y - t_tip.y), # 中指
                    math.hypot(lm[16].x - t_tip.x, lm[16].y - t_tip.y), # 无名指
                    math.hypot(lm[20].x - t_tip.x, lm[20].y - t_tip.y)  # 小指
                ]
                # 在画面上画出骨骼（可选，方便观察）
                mp.solutions.drawing_utils.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # C. 数据对齐并写入 CSV
    current_time = time.time()
    with open(FILENAME, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([current_time, emg_value] + distances)

    # 显示监控画面
    cv2.putText(image, f"sEMG: {emg_value}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('TetherIA - Synchronized Data Collector', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
ser.close()
cv2.destroyAllWindows()
print(f"✅ 录制结束，数据已安全存入 {FILENAME}")