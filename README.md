# 🦾 Capstone Project: Exploring Natural Muscle-Logic Interfaces for Bionic Hand Control

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/University-HKU-007D55" alt="HKU">
  <img src="https://img.shields.io/badge/Programme-MSc_IDT-E37222" alt="MSc IDT">
  <img src="https://img.shields.io/badge/Firmware-PlatformIO-orange" alt="PlatformIO">
</p>

---

### ℹ️ Project Affiliation
This project is an academic research initiative conducted at:
* **Author**: Lihao ZHOU
* **Institution**: **The University of Hong Kong (HKU)**, Faculty of Engineering (MSc in Innovative Design and Technology programme).

## 🌟 Project Overview
This repository contains the hardware designs, software implementation, and academic documentation for the HKU Capstone project. The initial aspiration of this research was to establish a complete engineering pipeline: capturing natural human operational intentions and translating them directly into the physical execution of a dexterous bionic hand.

The project commenced with extensive background research into robotic end-effectors, which led to the successful physical assembly of the TetherIA open-source tendon-driven hand. This foundational stage provided a deep understanding of robotic mechanics and successfully established the physical execution component of the system.

Subsequently, the research focus shifted to developing the human-machine controller. Due to strict budget constraints, the project adopted a 'boundary testing' strategy to find the maximum yield at the lowest possible cost. The sensor exploration progressed chronologically: beginning with highly affordable AD8232 ECG sensors to test feasibility limits, advancing to formal dry-electrode sEMG sensors, and finally experimenting with Hall-effect armbands to measure physical muscle deformation. 

While the TetherIA end-effector was successfully prepared, the real-time controller ultimately encountered reliability and signal drift bottlenecks during dynamic testing. Consequently, the final integration between the controller and the physical hand was cancelled to ensure safety. Nevertheless, this repository serves as a grounded, pragmatic exploration into low-cost human-machine interfaces and the practical challenges of raw-waveform control.

---

## 📂 Detailed Project Directory Structure

```text
MY_BIONIC_HAND_PROJECT/
├── Firmware/                                 # ESP32 & ESP32-S3 firmware engineering
├── Hardware/                                 # Mechanical & electrical design (TetherIA source)
├── Project_Docs/                             # 📄 Deliverables & research archives
│   ├── biweekly-ppt/                         # Biweekly presentation materials
│   ├── Gantt_Charts/                         # Project timeline management
│   ├── Literatures/                          # Reference papers & academic literature
│   ├── PowerPoints/                          # Defense materials & presentation slides
│   ├── Relative_pics_&_videos/               # Experiment recordings & prototype photos
│   ├── Reports/                              # Milestone reports & thesis drafts
│   ├── weekly/                               # Weekly markdown reports
│   └── Software/                             # Python control & machine learning framework
│       ├── EMG_raw_datasets/                 # Raw sEMG data & collection protocols
│       ├── GUI_application/                  # Real-time inference GUI & model training scripts
│       ├── legacy_benchmarks/                # Archived algorithm evaluation scripts
│       ├── old_data_collection/              # Historical data logging backups
│       └── TetherIA/                         # Open-source robotic hand SDK reference
├── .gitattributes                            
├── .gitignore                                
├── LICENSE                                   # Project code MIT license
├── MUJOCO_LOG.TXT                            # Physics simulation engine logs
└── README.md                                 # Project documentation
```

# 🛠️ Installation & Setup (Archived Reference)

### 1. Firmware (ESP32 / ESP32-S3)
1. Install **VS Code** and the **PlatformIO** extension.
2. Open the respective firmware folder (`Firmware/`) in VS Code.
3. Connect your microcontroller via USB and click the **Upload (→)** button on the PlatformIO bottom status bar.
   * *Note: The TetherIA hand requires a 6V/10A external power supply for servo movement.*

### 2. Software (Python)
1.  **Environment**: Ensure Python 3.8+ is installed (Anaconda is recommended).
2.  **Dependencies**: Install the required libraries via the GUI application directory.
3.  **Launch Control System**: Run the main GUI application for offline data visualisation:
    ```bash
    python Project_Docs/Software/GUI_application/main.py
    ```

---

# 🏁 Final Project Status

* [x] Physical 7-DOF Robotic Hand Assembly & Calibration.
* [x] Python-Serial bridge logic implementation.
* [x] Offline Machine Learning classification (Random Forest & 1D-CNN) achieving high static accuracy.
* [x] Real-time physical integration testing (Concluded).
* **Conclusion**: Real-time deployment highlighted critical limitations in raw-waveform signal stability (baseline drift and transition noise). Active development and physical integration have been formally ceased.

---

# ⚖️ Disclaimer & Safety

**1. Academic Use Only**: This project is developed by **Lihao ZHOU** for the MSc IDT programme at HKU. It is strictly intended for academic research purposes.
**2. No Warranty**: The software and hardware designs are provided "AS IS". The author and HKU accept no liability for any damages arising from the use of this repository.
**3. Safety Warning**: The hardware component utilises **high-current (10A)** power supplies and high-torque actuators. Ensure strict adherence to electrical safety protocols.
**4. Not a Medical Device**: This is a robotic engineering prototype and is **NOT** a certified medical prosthetic.

### 🙏 Acknowledgments
Special thanks to the **TetherIA** team for the Aero Hand Open mechanical design, which served as the hardware foundation for this research.

---

# 📜 License

This project involves multiple components with different open-source licenses:

### 1. Software & Firmware (Original Work)
* **Scope**: Original code in `Firmware/` and `Project_Docs/Software/`.
* **License**: **MIT License** (See root `LICENSE`).
* **Copyright**: © 2026 ZHOU Lihao & The University of Hong Kong.

### 2. Hardware Design (Derivative Work)
* **Scope**: Mechanical models (CAD), PCB designs, and Assembly guides in `Hardware/`.
* **Source**: Derived from **TetherIA (Aero Hand Open)**.
* **License**: Subject to the original **TetherIA Hardware License** (See `Hardware/LICENSE`).
    * *Note: Any modification to the hardware files must comply with the share-alike provisions of the original license.*
### 3. Commercial Hardware & Reference SDKs
**Hardware Scope**: The Pegasus Muscle Deformation Armband (飞马座形变手环) utilized in the final boundary testing phase is a commercial off-the-shelf (COTS) product manufactured by Sichiray (大脑实验室). Its proprietary hardware design is strictly excluded from this repository's open-source licenses.
**Code Scope**: Any baseline data acquisition scripts (e.g., UDP packet parsing templates) adapted from Sichiray's official reference documentation retain their original vendor licensing terms.

---

# 🦾 Capstone Project: 基于人体自然肌肉逻辑的仿生手控制接口探索

### ℹ️ 项目归属
本项目为学术研究项目：
* **作者**: 周礼昊 (Lihao ZHOU)
* **所属院校**: **香港大学 (HKU)** 工程学院 (MSc in Innovative Design and Technology 课程)。

## 🌟 项目概述
本仓库包含香港大学 Capstone 项目的硬件设计、软件实现及学术文档。本研究最初的期望是建立一个完整的工程链路：捕捉人类自然而然的操作意图，并将其直接转化为灵巧仿生手的物理控制信号。

项目初期对机器人末端执行器进行了详尽的背景调查，并成功完成了 TetherIA 开源绳驱动机械手的物理组装。这一基础阶段为理解机器人力学提供了深度参考，并成功打通了系统的物理执行端。

随后，研究重心转移至人机控制器的开发。由于严格的预算限制（商业科研级 sEMG 臂环动辄数千元），本项目采用了“边界测试”策略，以期在最低成本下实现最大收益。传感器探索按时间顺序推进：从极低成本的 AD8232 心电传感器（用于测试可行性边界）开始，推进到正式的干电极 sEMG 传感器，最后尝试使用基于霍尔传感器的飞马座臂环来测量物理肌肉形变。

尽管 TetherIA 末端执行器已准备就绪，但实时控制器在动态测试中最终遇到了信号漂移和稳定性的工程瓶颈。因此，控制器与物理机械手的最终实时集成未能实现。尽管如此，本仓库仍可作为对低成本人机接口及原始波形控制实际挑战的一次务实、落地的工程探索。

---

## 📂 详细项目目录结构

```text
MY_BIONIC_HAND_PROJECT/
├── Firmware/                                 # ESP32 & ESP32-S3 固件工程
├── Hardware/                                 # 机械与电子设计 (源自 TetherIA)
├── Project_Docs/                             # 📄 交付物与研究归档
│   ├── biweekly-ppt/                         # 双周汇报演示文稿
│   ├── Gantt_Charts/                         # 项目进度管理
│   ├── Literatures/                          # 参考文献与学术资料
│   ├── PowerPoints/                          # 答辩与最终演示文稿
│   ├── Relative_pics_&_videos/               # 实验录像与原型机照片
│   ├── Reports/                              # 里程碑报告与论文草稿
│   ├── weekly/                               # 每周 Markdown 进度报告
│   └── Software/                             # Python 控制与机器学习框架
│       ├── EMG_raw_datasets/                 # 原始肌电数据与采集协议
│       ├── GUI_application/                  # 实时推理 GUI 与模型训练脚本
│       ├── legacy_benchmarks/                # 已归档的算法评估脚本
│       ├── old_data_collection/              # 历史数据记录备份
│       └── TetherIA/                         # 开源机械手 SDK 参考
├── .gitattributes                            
├── .gitignore                                
├── LICENSE                                   # 项目代码 MIT 协议
├── MUJOCO_LOG.TXT                            # 物理仿真引擎日志
└── README.md                                 # 项目说明文档
```

---

# 🛠️ 安装与配置 (归档参考)

### 1. 固件端 (ESP32 / ESP32-S3)
1. 安装 **VS Code** 及 **PlatformIO** 插件。
2. 在 VS Code 中打开相应的固件文件夹 (`Firmware/`)。
3. 通过 USB 连接微控制器，点击 PlatformIO 底部状态栏的 **上传 (→)** 按钮。
   * *注意: 必须连接 6V/10A 外部电源才能驱动 TetherIA 机械手动作。*

### 2. 软件端 (Python)
1. **环境准备**: 确保已安装 Python 3.8+ (推荐使用 Anaconda)。
2. **安装依赖**: 通过 GUI 应用程序目录配置所需依赖库。
3. **启动系统**: 运行主控制 GUI 程序以进行离线数据可视化:
    ```bash
    python Project_Docs/Software/GUI_application/main.py
    ```

---

# 🏁 项目最终状态

* [x] 实体 7 自由度仿生手组装与物理校准。
* [x] Python-串口通信链路逻辑实现。
* [x] 离线机器学习分类 (随机森林与 1D-CNN) 实现高静态准确率。
* [x] 实时物理集成测试 (已终止)。
* **结论**: 实时部署凸显了原始波形信号稳定性 (基线漂移与过渡噪声) 的严重局限性。主动开发与物理集成环节已正式结束。

---

# ⚖️ 免责声明与安全警告

**1. 仅限学术用途**: 本项目由 **周礼昊 (Lihao ZHOU)** 开发，属于香港大学 MSc IDT 课程研究成果，仅供学术研究使用。
**2. 不提供担保**: 软件及硬件设计按“原样”提供，作者及香港大学不对使用过程中的任何物理或数据损坏负责。
**3. 安全警告**: 系统涉及 **10A 大电流** 电源及高扭矩执行器，请严格遵守实验室用电安全规范。
**4. 非医疗设备**: 本项目为机器人工程原型，**严禁**用作经过认证的医疗义肢。

### 🙏 致谢
特别感谢 **TetherIA** 团队提供的 Aero Hand Open 机械设计，为本研究提供了坚实的硬件基础。

---

# 📜 License / 许可
****
本项目包含多个适用不同开源协议的组件：

### 1. 软件与固件 (原创部分)
* **范围**: `Firmware/` 和 `Project_Docs/Software/` 下的原创代码。
* **协议**: **MIT 协议** (详见根目录 `LICENSE`)。
* **版权**: © 2026 ZHOU Lihao & 香港大学。

### 2. 硬件设计 (衍生部分)
* **范围**: `Hardware/` 目录下的机械模型 (CAD)、PCB 设计及装配文档。
* **来源**: 源自 **TetherIA (Aero Hand Open)** 开源项目。
* **协议**: 遵循原作者的硬件开源协议 (详见 `Hardware/LICENSE`)。
    * *注意: 对硬件图纸的任何修改均需严格遵守原协议的“相同方式共享 (Share-Alike)”条款。*

### 3. 商业硬件与参考 SDK
* **硬件范围**: 项目后期边界测试中使用的飞马座形变手环为 Sichiray (大脑实验室) 生产的商业现成产品 (COTS)。该硬件的专有设计不属于本仓库的开源范围。
* **代码范围**: 本项目中基于 Sichiray 官方参考文档修改的基础数据采集脚本 (如 UDP 数据包解析模板) 保留其原始供应商的许可条款。