import serial
import time
import sys
import os

# 尝试导入机械手 SDK，如果找不到则进入仿真模式
try:
    from aero_open_sdk.aero_hand import AeroHand
except ImportError:
    class AeroHand:
        def set_joint_positions(self, positions): pass

# ================= 配置区域 =================
ESP32_PORT = 'COM4'   # 请确认你的端口
BAUD_RATE = 115200    
WINDOW_SIZE = 10      # 增加滤波窗口，让进度条更丝滑
# ===========================================

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("="*50)
    print("🚀 灵巧手肌肉信号控制 - 演示专用版 🚀")
    print("="*50)

    # 1. 初始化连接
    try:
        ser = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)
        print(f"✅ 采集卡已就绪 ({ESP32_PORT})")
    except:
        print(f"❌ 错误: 请检查 ESP32 是否连接在 {ESP32_PORT}")
        return

    hand = None
    try:
        hand = AeroHand() 
        print("✅ 机械手硬件已连接")
    except:
        print("💡 提示: 未检测到机械手，当前为屏幕演示模式")

    # 2. 智能校准阶段
    print("\n[第一步] 采集放松状态 - 请完全放松手臂...")
    time.sleep(2)
    relax_vals = []
    ser.reset_input_buffer()
    for _ in range(100):
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.isdigit(): relax_vals.append(int(line))
    relax_avg = sum(relax_vals) // len(relax_vals) if relax_vals else 2400
    print(f"✔️ 放松基线: {relax_avg}")

    print("\n[第二步] 采集握拳状态 - 现在！用力握紧并保持...")
    time.sleep(2)
    clench_vals = []
    for _ in range(100):
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.isdigit(): clench_vals.append(int(line))
    clench_avg = sum(clench_vals) // len(clench_vals) if clench_vals else 3200
    print(f"✔️ 发力基线: {clench_avg}")

    # 计算阈值和动态死区
    THRESHOLD = (relax_avg + clench_avg) // 2
    DEADZONE = (clench_avg - relax_avg) * 0.1 # 自动设置10%的缓冲区
    
    print(f"\n✨ 校准成功！目标阈值: {THRESHOLD}")
    input("👉 按 [回车键] 开始正式演示...")

    # 3. 实时演示循环
    history = []
    status = "  🖐  准备就绪  " # 初始化变量防止报错
    last_action = None

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not line.isdigit(): continue
                
                val = int(line)
                
                # --- 抗干扰逻辑 ---
                # 如果信号突然掉到 50 以下（通常是断线），保持上一次的数值，防止视频中机械手乱跳
                if val < 50 and len(history) > 0:
                    val = history[-1]

                history.append(val)
                if len(history) > WINDOW_SIZE: history.pop(0)
                smooth_val = sum(history) / len(history)

                # --- 核心判断逻辑 (带死区) ---
                if smooth_val > (THRESHOLD + DEADZONE):
                    status = "【✊ 握拳指令】"
                    current_action = "GRIP"
                    target_pose = [80.0] * 16 
                elif smooth_val < (THRESHOLD - DEADZONE):
                    status = "  🖐  张开指令  "
                    current_action = "OPEN"
                    target_pose = [0.0] * 16
                else:
                    current_action = last_action # 维持现状

                # --- 视觉渲染 ---
                bar_len = int((smooth_val / 4095) * 30)
                bar_len = max(0, min(30, bar_len))
                bar = '█' * bar_len + '-' * (30 - bar_len)
                
                # 使用固定长度输出，确保不换行、不残余旧字符
                sys.stdout.write(f"\r信号: {int(smooth_val):4d} |{bar}| {status}    ")
                sys.stdout.flush()

                # 执行动作 (仅在状态切换时发送指令，避免堵塞串口)
                if hand and current_action != last_action:
                    hand.set_joint_positions(target_pose)
                    last_action = current_action

    except KeyboardInterrupt:
        print("\n\n演示结束。")
        ser.close()

if __name__ == "__main__":
    main()