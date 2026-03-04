# 🦾 sEMG-Based Bionic Hand Controller

### *A Modular Human-Machine Interface based on TetherIA Open Architecture*

<p align="center">
  <img src="https://img.shields.io/github/license/MrNanliu/My_Bionic_hand_project?color=blue" alt="License">
  <img src="https://img.shields.io/badge/University-HKU-007D55" alt="HKU">
  <img src="https://img.shields.io/badge/Collaborator-Sustech_Intelligent_Sensing-0056D2" alt="Sustech">
  <img src="https://img.shields.io/badge/Program-MSc_IDT-E37222" alt="MSc IDT">
  <img src="https://img.shields.io/badge/Firmware-PlatformIO-orange" alt="PlatformIO">
</p>

---

### ℹ️ Project Affiliation

This project is a collaborative initiative between:

* **Institution**: **The University of Hong Kong (HKU)**, Faculty of Engineering (MSc in Innovative Design and Technology).
* **Industry Partner**: **Sustech Intelligent Sensing Co., Ltd. (南科智能传感有限公司)**.

It focuses on developing a robust sEMG signal processing framework and integrating it with the **TetherIA Aero Hand** hardware.

---

## 🌟 Key Features (v0.2.0)

* **Advanced Firmware Architecture**: Migrated to **PlatformIO/VS Code** for modular C++ development on ESP32-S3.
* **Optimized Hand Control**:
    * **Smart Homing**: Custom auto-calibration logic for precise initial thumb posture (-10° abduction / +65° flexion).
    * **Dynamic Restoration**: Hand automatically restores optimal extend positions upon non-power resets (e.g., USB reconnection).
* **Signal Processing**: Supports real-time sEMG acquisition with anti-jitter algorithms (Moving Average Filter).
* **7-DOF Control**: Full dexterity control utilizing 7x Feetech servos with current/temperature protection.

## 📂 Project Structure

```text
My_Bionic_hand_project/
├── Firmware/                  # ESP32-S3 Firmware Projects
│   ├── Aero_Hand_Controller/  # [CORE] Main Bionic Hand Firmware
│   ├── ESP32_EMG_Sensor/      # EMG Signal Acquisition Firmware
│   └── _OLD_EMG_Firmware/     # Legacy/Backup Archives
│
├── Hardware/                  # Mechanical & Electrical Design (TetherIA Source)
│   ├── Assembly/              # Assembly guides
│   ├── CAD/                   # 3D Models
│   ├── PCB/                   # Circuit Schematics
│   └── LICENSE                # Hardware Open Source License
│
├── Software/                  # Python Control System
│   ├── sdk/                   # Core Drivers & GUI
│   ├── control_scripts/       # Experimental Signal Processing Scripts
│   └── requirements.txt       # Python Dependencies
│
├── Project_Docs/              # 📄 Deliverables & Research Archives
│   ├── doc-tetheria-cad/      # Reference Mechanical Models
│   ├── Gantt_Charts/          # Project Timeline Management
│   ├── Literatures/           # Reference Papers
│   ├── PowerPoints/           # Presentation Slides
│   └── Reports/               # Milestone Reports
│
├── .gitignore
├── LICENSE                    # Project Code License (e.g., MIT)
└── README.md                  # Project Documentation

```

---

# 🛠️ Installation & Setup

### 1.1 Firmware (ESP32)
1. Install **VS Code** and the **PlatformIO** extension.
2. Open the `Firmware/ESP32_EMG_Sensor` folder in VS Code.
3. Connect your ESP32 via USB and click the **Upload (→)** button on the PlatformIO bottom status bar.

### 1.2 Firmware (ESP32-S3)
1. Install **VS Code** and the **PlatformIO** extension.
2. Open the `Firmware/Aero_Hand_Controller` folder in VS Code.
3. Connect the Seeed Studio XIAO ESP32S3 via USB.
4. Click the **Upload (→)** button on the PlatformIO status bar.
   * Note: Ensure the 6V/10A external power supply is connected for servo movement.

### 2. Software (Python)
1.  **Environment**: Ensure Python 3.8+ is installed (Anaconda is highly recommended for environment management).
2.  **Dependencies**: Install the required libraries using the provided requirements file:
    ```bash
    pip install -r Software/requirements.txt
    ```
3.  **Hardware Connection**: Connect your ESP32-S3 and the Robotic Hand to your PC via USB.
4.  **Launch Control System**: Run the main GUI application:
    ```bash
    python Software/sdk/aero_open_gui.py
    ```

---

# 🚀 Roadmap

* [x] Simulation mode implementation.
* [x] Python-Serial bridge logic.
* [x] **Physical 7-DOF Robotic Hand Assembly & Calibration (v0.2.0).**
* [ ] Integration of sEMG signal processing algorithms.
* [ ] Multi-channel signal classification (Machine Learning for gesture recognition).

---

# ⚖️ Disclaimer & Safety

**1. Academic Use Only**: This project is developed by **周礼昊 (Lihao ZHOU)** for the MSc IDT program at HKU. It is intended for research purposes.
**2. No Warranty**: The software/hardware designs are provided "AS IS". The author, HKU, and Sustech Intelligent Sensing accept no liability for damages.
**3. Safety Warning**: This project uses **high-current (10A)** power supplies and high-torque actuators. Use with extreme caution.
**4. Not a Medical Device**: This is a robotic prototype and is **NOT** a certified medical prosthetic.

### 🙏 Acknowledgments
Special thanks to **TetherIA** for the open-source Aero Hand mechanical design, which serves as the foundation for this control system research.

---

### 📅 Release History
* **v0.2.0 (Current)**: Completed hardware assembly, migrated to PlatformIO, and implemented smart homing/auto-restoration logic.
* **v0.1.0**: Initial hardware selection and basic servo testing.

---

# 🦾 基于肌电信号的仿生手控制系统
### *基于 TetherIA 开源架构的模块化人机交互方案*

### ℹ️ 项目背景
本项目为校企联合研发项目：
* **所属院校**: **香港大学 (HKU)** 工程学院 (MSc in Innovative Design and Technology 课程)。
* **企业伙伴**: **南科智能传感有限公司 (Sustech Intelligent Sensing)**。

本项目致力于开发一套鲁棒的 sEMG 信号处理框架，并将其与 **TetherIA Aero Hand** 开源硬件深度集成。

---

## 🌟 核心特性 (v0.2.0)
* **固件架构升级**: 全面迁移至 **PlatformIO/VS Code**，基于 ESP32-S3 进行模块化 C++ 开发。
* **运动控制优化**:
    * **智能归位 (Smart Homing)**: 自定义自动校准算法，确保大拇指初始化至完美姿态（外展 -10° / 屈曲 +65°）。
    * **热启动记忆**: 引入掉电保护逻辑，在非断电重启（如 USB 意外断开重连）时，机械手可自动恢复舒展状态，无需重新校准。
* **信号处理**: 集成实时 sEMG 信号采集链路，内置防抖算法（滑动平均滤波器）以消除硬件噪声。
* **7 自由度控制**: 精准驱动 7 个飞特 (Feetech) 串行总线舵机，具备实时电流过载保护与温度监控功能。

## 📂 项目结构

```text
My_Bionic_hand_project/
├── Firmware/                  # ESP32-S3 固件工程
│   ├── Aero_Hand_Controller/  # [核心] 仿生手主控固件
│   ├── ESP32_EMG_Sensor/      # 肌电信号采集固件
│   └── _OLD_EMG_Firmware/     # 旧版/备份归档
│
├── Hardware/                  # 机械与电子设计 (TetherIA 源码)
│   ├── Assembly/              # 装配指南
│   ├── CAD/                   # 3D 模型文件
│   ├── PCB/                   # 电路原理图
│   └── LICENSE                # 硬件开源协议
│
├── Software/                  # Python 控制系统
│   ├── sdk/                   # 核心驱动与 GUI
│   ├── control_scripts/       # 实验性信号处理脚本
│   └── requirements.txt       # Python 依赖库列表
│
├── Project_Docs/              # 📄 交付物与研究归档
│   ├── doc-tetheria-cad/      # 参考机械模型
│   ├── Gantt_Charts/          # 项目进度管理
│   ├── Literatures/           # 参考文献
│   ├── PowerPoints/           # 演示 PPT
│   └── Reports/               # 阶段性报告
│
├── .gitignore
├── LICENSE                    # 项目代码协议 (如 MIT)
└── README.md                  # 项目说明文档

```

---

# 🛠️ 安装与配置

### 1.1 固件端 (ESP32)
1. 安装 **VS Code** 及 **PlatformIO** 插件。
2. 在 VS Code 中直接打开 `Firmware/ESP32_EMG_Sensor` 文件夹。
3. 将 ESP32 通过 USB 连接电脑，点击底部蓝色状态栏的 **上传 (→)** 按钮完成编译烧录。

### 1.2 固件端 (ESP32-S3)
1.  安装 **VS Code** 及 **PlatformIO** 插件.
2.  在 VS Code 中打开 `Firmware/Aero_Hand_Controller` 文件夹.
3.  通过 USB 连接 Seeed Studio XIAO ESP32S3 开发板。
4.  点击 PlatformIO 底部状态栏的 **上传 (→)** 按钮。
    * *注意: 必须连接 6V/10A 外部电源才能驱动舵机动作*.

### 2. 软件端 (Python)
1.  **环境准备**: 确保已安装 Python 3.8+ (强烈推荐使用 Anaconda 管理虚拟环境)。
2.  **安装依赖**: 使用提供的配置文件一键安装所需库:
    ```bash
    pip install -r Software/requirements.txt
    ```
3.  **硬件连接**: 将 ESP32-S3 及机械手通过 USB 连接至电脑。
4.  **启动系统**: 运行主控制 GUI 程序:
    ```bash
    python Software/sdk/aero_open_gui.py
    ```

---

# 🚀 后续开发计划

* [x] 模拟模式实现 (已完成验证)。
* [x] Python-串口通信链路搭建 (已完成验证)。
* [x] **实体 7 自由度仿生手组装与运动校准 (v0.2.0)。**
* [ ] sEMG 信号处理算法集成。
* [ ] 多通道信号分类 (引入机器学习进行复杂手势识别)。

---

# ⚖️ 免责声明与安全警告

**1. 仅限学术用途**: 本项目由 **周礼昊 (Lihao ZHOU)** 开发，属于香港大学 MSc IDT 课程研究成果.
**2. 不提供担保**: 软件及硬件设计按“原样”提供，作者、校方及合作企业不对使用过程中的损坏负责.
**3. 安全警告**: 系统涉及 **10A 大电流** 及高扭矩舵机，请严格遵守用电安全规范。
**4. 非医疗设备**: 本项目为仿生机器人原型，**严禁**用于临床医疗或作为义肢替代品.

### 🙏 致谢
特别感谢 **TetherIA** 团队提供的 Aero Hand Open 开源机械设计，为本项目的控制算法研究提供了坚实的硬件基础.

---

# 📜 License / 许可

This project involves multiple components with different open-source licenses. Please refer to the specific license files in each directory:

### 1. Software & Firmware (Original Work)
* **Scope**: All original code in `Firmware/Aero_Hand_Controller` and `Software/sdk`.
* **License**: **MIT License** (See root `LICENSE`).
* **Copyright**: © 2026 Zhou Lihao (Jason) & The University of Hong Kong.

### 2. Hardware Design (Derivative Work)
* **Scope**: Mechanical models (CAD), PCB designs, and Assembly guides in `Hardware/`.
* **Source**: Derived from **TetherIA (Aero Hand Open)**.
* **License**: Subject to the original **TetherIA Hardware License** (See `Hardware/LICENSE`).
    * *Note: Any modification to the hardware files must comply with the share-alike provisions of the original license.*

### 3. Third-Party Libraries
* **PlatformIO Libraries**: Libraries used in firmware (e.g., servo drivers, sensor libs) retain their original licenses (MIT/GPL/BSD) as specified in their respective folders.

---
### 1. 软件与固件 (原创部分)
* **范围**: `Firmware/` 和 `Software/` 下的所有原创代码。
* **协议**: **MIT 协议** (详见根目录 `LICENSE`)。
* **版权**: © 2026 Zhou Lihao (Jason) & 香港大学。

### 2. 硬件设计 (衍生部分)
* **范围**: `Hardware/` 目录下的机械模型、PCB 设计及装配文档。
* **来源**: 源自 **TetherIA (Aero Hand Open)** 开源项目。
* **协议**: 遵循原作者的硬件开源协议 (详见 `Hardware/LICENSE`)。
    * *注意: 对硬件图纸的任何修改均需遵守原协议的“相同方式共享 (Share-Alike)”条款。*

### 3. 第三方库
* 本项目固件中调用的第三方库 (如 PlatformIO 依赖库) 均保留其原始协议声明。