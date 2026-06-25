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
    print("Warning: SDK not found, running in simulation mode.")
    class AeroHand:
        def set_joint_positions(self, positions):
            pass 

ESP32_PORT = 'COM4'
BAUD_RATE = 115200

def main():
    print("Starting prosthetic logic test (calibration mode)")
    print(f"Connecting to data acquisition board on {ESP32_PORT}...")
    
    try:
        ser = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)
        print("Board connected.")
    except Exception:
        print("\nFatal error: Cannot connect to board.")
        return

    print("Searching for robotic hand...")
    hand = None
    try:
        hand = AeroHand() 
        print("Hardware connected.")
    except:
        print("Switched to software simulation mode.")

    print("\nCommencing baseline calibration.")
    print("Step 1/2: Rest arm on table and relax completely.")
    time.sleep(2)
    print("Recording relaxation baseline (3 seconds)...")
    
    relax_vals = []
    ser.reset_input_buffer()
    start_time = time.time()
    while time.time() - start_time < 3:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.isdigit():
                relax_vals.append(int(line))
    
    relax_avg = sum(relax_vals) // len(relax_vals) if relax_vals else 3800
    print(f"Relaxation baseline calculated: {relax_avg}")

    print("\nStep 2/2: Clench fist tightly and hold.")
    time.sleep(3)
    print("Recording clenching baseline (3 seconds)...")
    
    clench_vals = []
    ser.reset_input_buffer()
    start_time = time.time()
    while time.time() - start_time < 3:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.isdigit():
                clench_vals.append(int(line))

    clench_avg = sum(clench_vals) // len(clench_vals) if clench_vals else 3000
    print(f"Clenching baseline calculated: {clench_avg}")

    THRESHOLD = (relax_avg + clench_avg) // 2
    print(f"\nCalibration complete. Threshold set to: {THRESHOLD}\n")
    print("Test started (Press Ctrl+C to exit).")

    history = []
    status = "Unknown"
    target_pose = [0.0] * 16

    try:
        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line.isdigit():
                        val = int(line)
                        
                        history.append(val)
                        if len(history) > 8:
                            history.pop(0)
                        
                        smooth_val = sum(history) / len(history)
                        deadzone = THRESHOLD * 0.05
                        
                        if smooth_val < 50:
                            status = "Disconnected"
                        elif smooth_val > (THRESHOLD + deadzone):
                            status = "Clench"
                            target_pose = [80.0] * 16 
                        elif smooth_val < (THRESHOLD - deadzone):
                            status = "Open"
                            target_pose = [0.0] * 16
                        
                        max_bar_width = 30
                        bar_len = int((smooth_val / 4095) * max_bar_width)
                        bar = '█' * bar_len
                        spaces = ' ' * (max_bar_width - bar_len)
                        
                        output = f"\rFiltered Signal: {int(smooth_val):4d} |{bar}{spaces}| Status: {status:<12}"
                        print(output, end='', flush=True)

                        if hand:
                            try:
                                hand.set_joint_positions(target_pose)
                            except:
                                pass

                except ValueError:
                    pass
    except KeyboardInterrupt:
        print("\n\nTest concluded.")
        ser.close()

if __name__ == "__main__":
    main()