import serial
import time
import sys
import os

# --- 自动寻找 SDK 路径 ---
# 这一步是为了确保 Python 能找到 aero_open_sdk 文件夹
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # 假设 sdk 在上一级目录
sys.path.append(parent_dir)

try:
    from aero_open_sdk.aero_hand import AeroHand
except ImportError:
    # 如果找不到 SDK，我们做一个假的“替身”类，防止报错
    print("⚠️ 警告: 找不到 SDK，将运行在纯模拟模式")
    class AeroHand:
        def set_joint_positions(self, positions):
            pass # 假装在动，实际什么都不做

# ================= 配置区域 =================
ESP32_PORT = 'COM3'   # <--- 请确认你的 ESP32 端口
BAUD_RATE = 115200    
THRESHOLD = 600       
# ===========================================

def main():
    print(f"--- 启动义肢逻辑测试 (无手模式支持) ---")
    
    # 1. 连接 ESP32 (这个必须有，因为你要测信号)
    print(f"1. 正在连接 ESP32 采集卡 ({ESP32_PORT})...")
    try:
        ser = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)
        print("   ✅ 采集卡连接成功！")
    except Exception as e:
        print(f"\n❌ [致命错误] 无法连接 ESP32！\n请检查: 1.USB线插了吗? 2.Arduino绘图器关了吗?")
        return

    # 2. 尝试连接机械手 (如果没有，我们就用替身)
    print("2. 正在搜索机械手...")
    hand = None
    try:
        real_hand = AeroHand() # 尝试连接真手
        # 这里通常需要检查连接状态，如果 SDK 抛出异常说明没连上
        # 假设 AeroHand() 初始化失败会报错
        hand = real_hand
        print("   ✅ 机械手硬件已连接！")
    except Exception as e:
        print(f"   ⚠️ 未检测到机械手 ({e})")
        print("   🚀 切换到 [纯软件仿真模式] - 只在屏幕显示结果")
        hand = None 

    print("\n=== 测试开始 ===")
    print("观察屏幕上的进度条，这就是未来机械手的动作指令\n")

    # 3. 循环逻辑
    try:
        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line.isdigit():
                        val = int(line)
                        
                        # === 你的算法逻辑 ===
                        if val > THRESHOLD:
                            status = "【✊ 握拳指令】"
                            # 如果你想模拟握拳数据
                            target_pose = [80.0] * 16 
                        else:
                            status = "  🖐  张开指令  "
                            target_pose = [0.0] * 16
                        
                        # === 可视化反馈 (这就是你在没手时的参考) ===
                        # 动态进度条
                        bar_len = int(val / 40)
                        bar = '█' * bar_len
                        print(f"\r信号: {val:4d} |{bar:<25}| {status}", end='')

                        # === 发送指令 (如果有手就发，没手就跳过) ===
                        if hand:
                            # 加上 try-catch 防止中途断开报错
                            try:
                                hand.set_joint_positions(target_pose)
                            except:
                                pass

                except ValueError:
                    pass
    except KeyboardInterrupt:
        print("\n\n测试结束。")
        ser.close()

if __name__ == "__main__":
    main()