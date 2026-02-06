# 🦾 Bionic Hand Control System (EMG-Based)
### *A Modular Approach to Human-Machine Interface using ESP32 and Aero-Hand-Open SDK*

This repository contains the full stack for a 7-DOF (Degrees of Freedom) dexterous robotic hand controlled via surface electromyography (sEMG) signals. The project utilizes an **ESP32** as a signal acquisition unit and a **Python-based control hub** to translate muscle intensity into robotic motion.

---

## 🌟 Key Features
* **Dual-Mode Signal Acquisition**: Supports real-world sEMG input (AD8232) and a built-in Sine-wave simulation mode for "hardware-less" debugging.
* **7-DOF Control**: Optimized for the `aero-hand-open` platform with fine-tuned pose libraries.
* **Real-time Processing**: Low-latency Serial communication (115200 Baud) between firmware and software.
* **Modular Architecture**: Clean separation between hardware manifests, ESP32 firmware, and Python control logic.

## 📂 Project Structure
```text
My_Bionic_Hand_Project/
├── firmware/              # ESP32 C++ Code
│   └── EMG_Acquisition/   # sEMG signal processing & serial transmission
├── software/              # Python Control System
│   ├── aero_open_sdk/     # Robotic hand drivers
│   └── muscle_control.py  # Main control logic & signal thresholding
├── hardware/              # Documentation & Schematics
│   └── BOM.csv            # Bill of Materials
└── README.md              # Project documentation
```

---

# 🛠️ Installation & Setup

1. Firmware(ESP32)
    1. Open ```  firmware/EMG_Acquisition/EMG_Acquisition.ino``` in Arduino IDE.
    2. Install the ESP32 board support package (by Espressif Systems).
    3. Upload the code to your ESP32. Use the Serial Plotter (115200 Baud) to verify the signal wave.

2. Sofeware (Python)
    1. Ensure you have Python 3.8+ installed (Anaconda recommended).
    2. Install required dependencies:
    ```bash
    pip install pyserial
    ```
    3. Connect your ESP32 and the Robotic Hand to your PC.
    4. Run the control script:
    ```bash
    python software/muscle_control.py
    ```

---

# 🚀 Roadmap
- [x] Simulation mode implementation.
- [x] Python-Serial bridge logic.
- [ ] Integration of physical AD8232 sEMG sensors.
- [ ] Multi-channel signal classification (Machine Learning for gesture recognition).

---

# 🦾 肌电控制仿生手系统
### 基于 ESP32 与 Aero-Hand-Open SDK 的模块化人机交互方案

本项目包含了一套完整的 7 自由度 (DOF) 灵巧手控制堆栈。系统通过表面肌电信号 (sEMG) 进行驱动，利用 ESP32 作为信号采集单元，并通过 Python 控制中心 将肌肉收缩强度转化为机械手的实时动作。

---

## 🌟 核心特性
* **双模式采集**: 支持真实 sEMG 输入 (AD8232) 以及内置的正弦波模拟模式，方便在没有传感器时进行软件调试。
* **7 自由度控制**: 针对 `aero-hand-open` 平台优化，内置多种手势预设库。
* **实时处理**: 固件与软件间采用低延迟串口通信 (115200 波特率)。
* **模块化架构**: 硬件清单、ESP32 固件与 Python 控制逻辑严格分离，易于扩展。

## 📂 项目结构
```text
My_Bionic_Hand_Project/
├── firmware/              # ESP32 C++ 代码 (固件)
│   └── EMG_Acquisition/   # s肌电信号处理与串口发送
├── software/              # Python 控制系统 (软件)
│   ├── aero_open_sdk/     # 机械手底层驱动
│   └── muscle_control.py  # 主控制逻辑与信号阈值判定
├── hardware/              # 硬件资料与图纸
│   └── BOM.csv            # 物料清单 (BOM)
└── README.md              # 项目说明文档
```

---

# 🛠️ 安装与配置

1. 固件端 (ESP32)
    1. 使用 Arduino IDE 打开 ```  firmware/EMG_Acquisition/EMG_Acquisition.ino``` 
    2. I安装 ESP32 开发板支持包 (Espressif Systems 官方版)。
    3. 将代码烧录至 ESP32。打开 串口绘图器 (115200 波特率) 验证波形输出。

2. 软件端 (Python)
    1. 确保电脑已安装 Python 3.8+ (推荐使用 Anaconda)。
    2. I安装必要依赖库:
    ```bash
    pip install pyserial
    ```
    3. 将 ESP32 和机械手通过 USB 连接至电脑。
    4. 运行控制脚本:
    ```bash
    python software/muscle_control.py
    ```

---

# 🚀 后续开发计划
- [x] 模拟模式实现 (已完成验证)。
- [x] Python-串口通信链路搭建 (已完成验证)。
- [ ] 集成物理 AD8232 肌电传感器。
- [ ] 多通道信号分类 (引入机器学习进行复杂手势识别)。