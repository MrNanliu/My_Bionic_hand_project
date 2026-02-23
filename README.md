![GitHub License](https://img.shields.io/github/license/MrNanliu/My_Bionic_hand_project?color=blue)

# 🦾 Bionic Hand Control System (EMG-Based)
### *A Modular Approach to Human-Machine Interface using ESP32 and Aero-Hand-Open SDK*

This repository contains the full stack for a 7-DOF (Degrees of Freedom) dexterous robotic hand controlled via surface electromyography (sEMG) signals. The project utilizes an **ESP32** as a signal acquisition unit and a **Python-based control hub** to translate muscle intensity into robotic motion.

---

## 🌟 Key Features
* **Auto-Calibration & Signal Filtering (New!)**: Implemented dynamic baseline auto-calibration and a moving average filter to eliminate hardware signal jitter and adapt to different users instantly.
* **Dual-Mode Signal Acquisition**: Supports real-world sEMG input (AD8232) and a built-in simulation mode for hardware-less debugging.
* **7-DOF Control**: Optimized for the `aero-hand-open` platform with fine-tuned pose libraries.
* **Real-time Processing**: Low-latency Serial communication (115200 Baud) between firmware and software.
* **Professional Toolchain**: Firmware developed and managed via **VS Code + PlatformIO** for strict C++ dependency control.

## 📂 Project Structure
```text
My_Bionic_Hand_Project/
├── Firmware/              # ESP32 C++ Code (PlatformIO Project)
│   └── ESP32_EMG_Sensor/  # sEMG signal processing & serial transmission (main.cpp)
├── Software/              # Python Control System
│   └── sdk/
│       ├── aero_open_sdk/ # Robotic hand drivers
│       └── src/
│           └── muscle_test.py # Main logic with filtering & dynamic thresholds
├── Hardware/              # Documentation & Schematics
│   └── BOM.csv            # Bill of Materials
└── README.md              # Project documentation

```

---

# 🛠️ Installation & Setup

1. Firmware (ESP32)
1. Install **VS Code** and the **PlatformIO** extension.
2. Open the `Firmware/ESP32_EMG_Sensor` folder in VS Code.
3. Connect your ESP32 via USB and click the **Upload (→)** button on the PlatformIO bottom status bar.


2. Software (Python)
1. Ensure you have Python 3.8+ installed (Anaconda recommended).
2. Install required dependencies:


```bash
pip install pyserial

```


3. Connect your ESP32 and the Robotic Hand to your PC.
4. Run the control script:


```bash
python Software/sdk/src/muscle_test.py

```

---

# 🚀 Roadmap

* [x] Simulation mode implementation.
* [x] Python-Serial bridge logic.
* [x] Integration of physical AD8232 sEMG sensors (with anti-jitter algorithms).
* [ ] Integration of the physical 7-DOF Robotic Hand.
* [ ] Multi-channel signal classification (Machine Learning for gesture recognition).



---

# 🦾 肌电控制仿生手系统

### 基于 ESP32 与 Aero-Hand-Open SDK 的模块化人机交互方案

本项目包含了一套完整的 7 自由度 (DOF) 灵巧手控制堆栈。系统通过表面肌电信号 (sEMG) 进行驱动，利用 ESP32 作为信号采集单元，并通过 Python 控制中心 将肌肉收缩强度转化为机械手的实时动作。

---

## 🌟 核心特性

* **智能校准与滤波防抖 (新增!)**: 引入动态基线自动校准与滑动平均滤波算法，彻底消除物理硬件带来的信号抖动，实现开机即用的高精准识别。
* **双模式采集**: 支持真实 sEMG 输入 (AD8232) 以及内置模拟模式，方便在无传感器时进行软件调试。
* **7 自由度控制**: 针对 `aero-hand-open` 平台优化，内置多种手势预设库。
* **实时处理**: 固件与软件间采用低延迟串口通信 (115200 波特率)。
* **专业级开发工具链**: 固件端全面迁移至 **VS Code + PlatformIO**，实现纯正 C++ 模块化管理。

## 📂 项目结构

```text
My_Bionic_Hand_Project/
├── Firmware/              # ESP32 C++ 代码 (PlatformIO 工程)
│   └── ESP32_EMG_Sensor/  # 肌电信号处理与串口发送 (main.cpp)
├── Software/              # Python 控制系统 (软件)
│   └── sdk/
│       ├── aero_open_sdk/ # 机械手底层驱动 SDK
│       └── src/
│           └── muscle_test.py # 主控制逻辑、滤波算法与阈值判定
├── Hardware/              # 硬件资料与图纸
│   └── BOM.csv            # 物料清单 (BOM)
└── README.md              # 项目说明文档

```

---

# 🛠️ 安装与配置

1. 固件端 (ESP32)
1. 安装 **VS Code** 及 **PlatformIO** 插件。
2. 在 VS Code 中直接打开 `Firmware/ESP32_EMG_Sensor` 文件夹。
3. 将 ESP32 通过 USB 连接电脑，点击底部蓝色状态栏的 **上传 (→)** 按钮完成编译烧录。


2. 软件端 (Python)
1. 确保电脑已安装 Python 3.8+ (推荐使用 Anaconda 创建虚拟环境)。
2. 安装必要依赖库:


```bash
pip install pyserial

```


3. 将 ESP32 和机械手通过 USB 连接至电脑。
4. 运行智能控制脚本:


```bash
python Software/sdk/src/muscle_test.py

```



---

# 🚀 后续开发计划

* [x] 模拟模式实现 (已完成验证)。
* [x] Python-串口通信链路搭建 (已完成验证)。
* [x] 集成物理 AD8232 肌电传感器 (含滤波防抖算法)。
* [ ] 接入并联调实体 7 自由度仿生机械手。
* [ ] 多通道信号分类 (引入机器学习进行复杂手势识别)。
