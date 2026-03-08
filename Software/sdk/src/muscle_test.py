import serial
import time
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from aero_open_sdk.aero_hand import AeroHand
except ImportError:
    print("⚠️ 警告: 找不到 SDK，将运行在纯模拟模式")
    class AeroHand:
        def set_joint_positions(self, positions):
            pass 

# ================= 配置区域 =================
ESP32_PORT = 'COM4'   # <--- 确认端口
BAUD_RATE = 115200    
# ===========================================

def main():
    print(f"--- 启动义肢逻辑测试 (智能校准版) ---")
    
    print(f"1. 正在连接 ESP32 采集卡 ({ESP32_PORT})...")
    try:
        ser = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)
        print("   ✅ 采集卡连接成功！")
    except Exception as e:
        print(f"\n❌ [致命错误] 无法连接 ESP32！")
        return

    print("2. 正在搜索机械手...")
    hand = None
    try:
        hand = AeroHand() 
        print("   ✅ 机械手硬件已连接！")
    except:
        print("   🚀 切换到 [纯软件仿真模式] - 只在屏幕显示结果")

    # ================= 智能校准阶段 =================
    print("\n" + "="*40)
    print("🤖 进入智能基线校准，请按提示操作！")
    print("="*40)
    
    print("\n【步骤 1/2】请把手臂平放在桌面上，完全放松...")
    time.sleep(2)
    print("⏳ 正在采集你的【放松基线】(持续3秒，请勿乱动)...")
    relax_vals = []
    ser.reset_input_buffer() # 清空旧数据
    start_time = time.time()
    while time.time() - start_time < 3:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.isdigit():
                relax_vals.append(int(line))
    
    relax_avg = sum(relax_vals) // len(relax_vals) if relax_vals else 3800
    print(f"✅ 放松基线计算完毕: {relax_avg}")

    print("\n【步骤 2/2】⚠️ 准备好了吗？请在看到提示后【用力握紧拳头】并保持！")
    time.sleep(3)
    print("⏳ ✊ 现在！用力握紧！(持续3秒，保持住)...")
    clench_vals = []
    ser.reset_input_buffer()
    start_time = time.time()
    while time.time() - start_time < 3:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.isdigit():
                clench_vals.append(int(line))

    clench_avg = sum(clench_vals) // len(clench_vals) if clench_vals else 3000
    print(f"✅ 发力基线计算完毕: {clench_avg}")

    # 计算黄金阈值 (取放松和发力的中间值)
    THRESHOLD = (relax_avg + clench_avg) // 2
    print(f"\n✨ 校准完成！为你量身定制的阈值为: 【 {THRESHOLD} 】 ✨\n")
    print("=== 正式测试开始 (按 Ctrl+C 退出) ===")

    # ================= 正式工作阶段 =================
    history = [] # 用于滑动平均滤波的队列
    
    try:
        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line.isdigit():
                        val = int(line)
                        
                        # --- 核心算法：滑动平均滤波 (防抖) ---
                        history.append(val)
                        if len(history) > 8:  # 收集最近8个数据
                            history.pop(0)    # 踢掉最老的数据
                        smooth_val = sum(history) / len(history) # 计算平均值
                        deadzone = THRESHOLD * 0.05
                        # -----------------------------------
                        
                        if smooth_val > (THRESHOLD + deadzone):
                            status = "【✊ 握拳指令】"
                            target_pose = [80.0] * 16 
                        elif smooth_val < (THRESHOLD - deadzone):
                            status = "  🖐  张开指令  "
                            target_pose = [0.0] * 16
                        else:
                            pass
                        
                        max_bar_width = 30
                        bar_len = int((smooth_val / 4095) * max_bar_width)
                        bar = '█' * bar_len
                        spaces = ' ' * (max_bar_width - bar_len)
                        output = f"\r滤波信号: {int(smooth_val):4d} |{bar}{spaces}| {status}      "
                        # 打印平滑后的数值，肉眼终于能看清了！
                        print(output, end='', flush=True)

                        if hand:
                            try:
                                hand.set_joint_positions(target_pose)
                            except:
                                pass
                        
                        if smooth_val < 50:
                            status = "⚠️ 传感器失联"

                except ValueError:
                    pass
    except KeyboardInterrupt:
        print("\n\n测试结束。")
        ser.close()

if __name__ == "__main__":
    main()