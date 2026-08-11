# 专业项目交接 / 归档评审标准

---

## 一、交接包最低交付物（所有技术方向通用）


| ID  | 交付物              | 必须内容 【“请填写”】                          | 缺则后果        |
| --- | ---------------- | ------------------------------------- | ----------- |
| H1  | `README.md`（课题版） | 一句话目标、完成/未完成边界、硬件与软件依赖、完整目录地图、联系人邮箱 | 新人无法进入      |
| H2  | `HANDOVER.md`    | 核心必读路径（main.py等）、TetherIA 散热与臂环人体工程学注意事项、硬件在线采购指南、后续优化建议  | 隐性知识丢失      |
| H3  | 版本冻结指针           | Git Tag：archive/2026-lihaozhou   | 无法对齐「当时交付态」 |
| H4  | 进度轨迹             | weekly/（ISO 周报）、biweekly-ppt/（汇报 PDF）    | 无法理解演进      |
| H5  | 外部资产登记           | 已在 HANDOVER.md 中登记：仿生手存放于公司，臂环需采购       | 仓库外知识黑洞     |


---



## 二、按项目类型的资产门禁（Asset Gates）

### Type M — 机械设计 / 腱驱手·臂 / 3D 打印
直接采用 TetherIA 开源物理结构进行组装与调试，无自研机械 CAD 设计

| Gate | 要求 | 合格证据 / 填写说明 |
| :--- | :--- | :--- |
| **M1 方案总述** | 设计目标、约束、与基线差异 | **N/A**（严格采用 TetherIA 开源腱驱动手标准结构，无自研机械方案与结构改动） |
| **M2 原生 CAD** | SolidWorks/Inventor 等源文件 | **N/A**（使用 TetherIA 官方开源 3D 打印与 CAD 模型，存放于 `Hardware/CAD/`） |
| **M3 中性格式** | STEP 装配 + 关键 STL | **N/A**（开源中性打印与装配文件，存放于 `Hardware/CAD/`） |
| **M4 BOM** | 零件/标准件/工具，含规格与数量 | **N/A**（组装采购与零部件清单见 `Hardware/Assembly/BoM.xlsx`） |
| **M5 装配说明** | 装配顺序、爆炸图/照片、扭矩/张紧说明 | **N/A**（组装风险与失效模式分析见 `Hardware/Assembly/FMECA_TetherIA.xlsx`|
| **M6 渲染/外观** | 至少 3 张可展示图（装配/细节/场景） | **N/A**（实物组装、打磨与过程照片存放于 `Project_Docs/Relative_pics_&_videos/`） |
| **M7 变更史** | v1/v2/v3 差异 | **N/A**（无自研 CAD 结构版本迭代） |



### Type E — 电子 / PCB / 传感
多代传感硬件迭代 / 面包板搭建与离散模块集成（无自研 PCB 工程）
*注：前期 AD8232 与干电极 sEMG 采样的面包板硬件为早期探索归档版本；最终控制 pipeline 采用 6 通道蓝牙肌肉形变臂环。*

| Gate | 要求 | 合格证据 / 填写说明 |
| :--- | :--- | :--- |
| **E1 原理与工程** | 原理图 + PCB 工程 | **无自研 PCB 工程**。早期 sEMG/ECG 采样前端采用面包板搭接离散模块（ESP32、AD8232、干电极模块）；最终方案采用成品 6 通道霍尔肌肉形变臂环；TetherIA 机械手官方参考 PCB 文件存放在 `Hardware/PCB/`。 |
| **E2 元器件 BOM** | BOM + 贴片坐标 | 各迭代阶段传感元器件与硬件清单见 `Hardware/Assembly/BoM.xlsx`；由于电路均采用面包板手工搭接或离散模块集成，无自动化 SMT 贴片坐标文件。 |
| **E3 接线图** | MCU–传感器–电机–供电接线 | **硬件接口与通信映射（含历史迭代）：**<br>• **AD8232 单通道（早期）：** `3.3V`->`3.3V`, `GND`->`GND`, `OUTPUT`->`D34`<br>• **双通道干电极 sEMG（中期）：** `VIN`->`3.3V`, `GND`->`GND`, `CH1 OUT`->`D35`, `CH2 OUT`->`D34`<br>• **肌肉形变臂环（最终）：** 6 通道霍尔阵列，采用 Bluetooth Serial 无线传输（采样率 31 Hz，波特率 `115200`）。 |
| **E4 电气限制** | 电气安全与极限 | ESP32 ADC 引脚（D34, D35）输入电压需严格限制在 3.3V 逻辑电平范围内，切勿接入 5V 或更高外部电压，防止损坏单片机芯片。 |




### Type F — 固件 / 电机控制
归档嵌入式固件（用于早期硬件探索与执行端参考，最终 pipeline 未依赖）

| Gate | 要求 | 合格证据 / 填写说明 |
| :--- | :--- | :--- |
| **F1 工具链与烧录** | 目标 MCU、IDE/工具链、flash 步骤 | **目标 MCU：** ESP32-D；**工具链：** VS Code + PlatformIO / Arduino IDE。<br>• **传感器采集固件：** 位于 `Firmware/ESP32_sEMG_test/`<br>• **仿生手电机控制固件：** 位于 `Firmware/Aero_Hand_Controller/` |
| **F2 配置与手型** | 左右手/配置宏说明 | 仿生手控制与数据采集逻辑统一配置为**右手（Right-Hand）**。 |
| **F3 通信协议** | 串口协议或命令表 | 采用 UART 串口通信（默认波特率 `115200`）：<br>• **采集端：** 输出 6 Channel 原始 ADC 模拟采样数据流（采样率约 31 Hz）<br>• **控制端：** 接收 7 个 FeeTech 舵机的目标角度控制指令 |
| **F4 安全与限位** | 安全：回零、限流、急停 | **电气安全：** ESP32 ADC 引脚严格限制在 3.3V 逻辑电平。<br>**机械/舵机安全：** 在 `Aero_Hand_Controller` 固件中硬编码设定了 7 个舵机的软限位角度范围，防止超行程导致腱绳拉断或物理卡死。 |


### Type S — 应用软件 / GUI / 机器学习
基于 Python 3.10 的实时上位机 GUI、特征工程与机器学习训练管线

| Gate | 要求 | 合格证据 / 填写说明 |
| :--- | :--- | :--- |
| **S1 环境与依赖** | 运行环境、核心依赖库与 requirements.txt | **环境：** Python 3.10。<br>**依赖清单：** 包含 `PyQt5`, `pyqtgraph`, `torch`, `scikit-learn`, `imbalanced-learn`, `pyserial`, `mediapipe`, `opencv-python` 等。<br>**依赖锁定文件：** 存放在 `Software/GUI_application/requirements.txt`，同时在根目录备份了 `environment.yml`。 |
| **S2 唯一入口** | 一条命令跑通 Demo / 上位机入口 | **唯一上位机 GUI 入口：** `python Software/GUI_application/main.py`。<br>支持串口/蓝牙实时数据接收、6 通道动态波形绘制、离线数据集评估以及实时模型推理输出（Live Feedback）。 |
| **S3 离线与密钥** | 无外部 API Key / 本地独立运行 | **完全本地化独立运行：** 无需任何云端 API Key 或网络服务，所有信号处理、特征提取及模型推理均在本地 CPU/GPU 完成。 |
| **S4 软件架构** | 代码结构、分层与辅助工具链 | **模块化架构分层：**<br>• **核心 GUI：** `Software/GUI_application/main.py`<br>• **训练与特征处理：** `Software/GUI_application/training_scripts/`（包含 `preprocess_datasets.py`、`train_deformation_rf.py` 与 `train_deformation_cnn.py`）<br>• **数据集协议：** `Software/MD_raw_datasets/Data_Collection_Protocol.md`<br>• **历史诊断与 Benchmark：** 归档于 `Software/legacy_benchmarks/` |




### Type R — 仿真 / RL / 物理引擎
N/A（无自研仿真环境搭建或强化学习训练）

| Gate | 要求 | 合格证据 / 填写说明 |
| :--- | :--- | :--- |
| **R1 仿真环境** | Gazebo / Isaac Gym / MuJoCo 等环境与 URDF | **N/A**（未搭建物理仿真环境） |
| **R2 算法与策略** | RL 强化学习 / 控制策略工程 | **N/A**（本项目采用监督学习/传统 ML 与 1D-CNN 进行手势分类，无 RL 策略训练） |
| **R3 仿真与实物对齐** | Sim-to-Real 迁移与误差分析 | **N/A** |
| **R4 依赖与一键运行** | 仿真依赖脚本与运行入口 | **N/A** |




### Type D — 数据 / 模型 / 机器学习数据集
包含 5 类手势的肌肉形变数据集、标准化采集协议、预处理脚本及已训练模型权重

| Gate | 要求 | 合格证据 / 填写说明 |
| :--- | :--- | :--- |
| **D1 数据集与协议** | 采集协议、数据说明与标注方式 | **标准化采集协议：** 存放在 `Software/MD_raw_datasets/Data_Collection_Protocol.md`。<br>采用按键触发离散单次采集与时间戳严格对齐，彻底消除摄像头同步延时与肌疲劳漂移。 |
| **D2 目标手势与存储** | 标注数据格式与存储路径 | **数据集包含 5 类目标手势：** `fist`（握拳）、`open_hand`（张手）、`pinch`（捏合）、`wrist_down`（屈腕）、`wrist_up`（抬腕）。<br>原始传感器数据以分类 `.txt` 格式存放于 `Software/MD_raw_datasets/`。 |
| **D3 预处理与模型** | 处理管线、训练脚本与模型权重 | • **预处理与训练脚本：** 位于 `Software/GUI_application/training_scripts/`（包含滑动窗口切片 `N=40, S=10`、动态零均值归一化、RF 与 1D-CNN 训练脚本）<br>• **已训练模型权重与标定文件：** 存放在 `Software/GUI_application/`（包含 `emg_cnn_model.pth`、`rf_model.pkl`、`rf_scaler.pkl` 与 `scaler.pkl`） |
| **D4 历史与对比数据** | 历史归档与多模态/基准数据 | 早期 sEMG/AD8232 探索数据及对比基准归档于：<br>• `Software/GUI_application/sEMG_raw_datasets/`<br>• `Software/old_data_collection/`<br>• `Software/legacy_benchmarks/` |




### Type A — 学术交付 / 报告与文档
包含终期论文报告、中期汇报、双周 PPT、周报轨迹、参考文献库及实物演示音视频）

| Gate | 要求 | 合格证据 / 填写说明 |
| :--- | :--- | :--- |
| **A1 过程与中期汇报** | 中期报告、双周汇报 PPT、进度轨迹 | • **中期报告：** `Project_Docs/Reports/Lihao_ZHOU_3036507016_interim_report.pdf`<br>• **双周汇报演示 PPT：** 存放于 `biweekly-ppt/`<br>• **周报轨迹：** 存放于 `weekly/` |
| **A2 终期报告与论文** | 毕业论文/终期报告（含摘要与贡献声明） | **终期论文报告：** `Project_Docs/Reports/Lihao_ZHOU_3036507016_Final_report.pdf`。<br>完整涵盖 Abstract, Statement of Contributions, FMECA 风险分析表、硬件接口映射及算法对比论证。 |
| **A3 参考文献库** | 课题关联文献与参考资料归档 | 部分文献 PDF 存档于 `Project_Docs/Literatures/`；完整文献引用列表（共 48 篇）已通过 Zotero 统一管理并完整收录于终期论文报告 `Project_Docs/Reports/Lihao_ZHOU_3036507016_Final_report.pdf` 的 References 章节。 |
| **A4 演示视频与媒体资产** | 实物照片、测试视频与演示媒体 | 存放于 `Project_Docs/Relative_pics_&_videos/`（包含 TetherIA 仿生手打磨组装实物图、离散传感器搭接照片、肌肉形变臂环佩戴图及 GUI 实时测试视频记录）。 |


---



## 三、评分量表（每维 0–2，总分 20）


| 分   | 含义                      |
| --- | ----------------------- |
| 0   | 缺失或误导（如 README 仍是管理模板）  |
| 1   | 有素材但难导航 / 重复混乱 / 无法独立复现 |
| 2   | 新人可自助：路径明确、版本清晰、边界诚实    |


**维度：**

1. **Narrative** — 课题叙事与完成边界
2. **Mech** — 机械门禁覆盖率（不适用写 N/A，针对无机械设计的项目）
3. **Elec** — 电子
4. **Firmware** — 固件
5. **Software** — 软件
6. **Sim/RL** — 仿真 RL
7. **Data/Model** — 数据模型
8. **Academic** — 报告/PPT/论文
9. **Progress trail** — 周报/里程碑可读
10. **Repro + Handover pack** — H1–H5

**就绪等级：**


| 总分（适用维归一后） | 等级              | 含义             |
| ---------- | --------------- | -------------- |
| ≥ 85%      | **Ready**       | 可交接，小修即可       |
| 60–84%     | **Conditional** | 核心资产在，但导航/复现不足 |
| 40–59%     | **At risk**     | 有材料，接手成本高      |
| < 40%      | **Blocked**     | 不可对新人直接交接      |


N/A 维度从分母剔除。

