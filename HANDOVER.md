# Project Handover Documentation

**Project Title:** Development and Integration of a Bionic Hand System Controlled by Muscle Deformation  
**Author:** Lihao ZHOU 
**Handover Date:** August 2026  

---

## 1. Must-Read Paths

1. `Software/GUI_application/main.py` — Core real-time interactive GUI for signal monitoring and model inference.
2. `Software/MD_raw_datasets/Data_Collection_Protocol.md` — Protocol governing muscle deformation data acquisition.
3. `Software/GUI_application/training_scripts/preprocess_datasets.py` — Pipeline for raw dataset preprocessing and feature extraction.
4. `Software/GUI_application/training_scripts/train_deformation_rf.py` & `train_deformation_cnn.py` — Machine learning training workflows.
5. `Project_Docs/Reports/` — Final and Interim Capstone Reports containing detailed theoretical analysis and test results.
6. `Hardware/Assembly/BoM.xlsx` & `FMECA_TetherIA.xlsx` — Bill of materials and failure mode analysis for the TetherIA hand.

---

## 2. Known Pitfalls & Hardware Warnings

* **TetherIA Hand Thermal Management:** Potential heat dissipation bottlenecks may occur during prolonged, continuous control of the TetherIA bionic hand. Thermal accumulation requires careful attention if long-duration operational testing is conducted in future work.
* **Armband Ergonomics & Thermal Artifacts:** The muscle deformation armband requires ergonomic optimization and an improved wearing/fastening mechanism. Structural loosening during movement directly introduces positional instability and data drift. Additionally, sensor heat generation during operation can introduce artificial signal peaks/spikes, requiring further hardware thermal isolation or filtering.
* **Handedness Protocol:** Computer vision data collection and gesture processing scripts are strictly configured for **Right-Hand** execution.
* **Firmware Scope:** Files under `Firmware/` belong to early exploratory sEMG/ECG prototyping and are **not required** to execute the final muscle deformation GUI application.

---

## 3. Large File Locations & Storage 

To avoid bloat within the Git repository structure, large binaries and weights are tracked as follows:
* **Trained Models & Scalers:** Stored directly under `Software/GUI_application/` (`emg_cnn_model.pth`, `rf_model.pkl`, `rf_scaler.pkl`, `scaler.pkl`).
* **Preprocessed Feature Arrays:** Stored under `Software/GUI_application/training_scripts/` (`X_cnn_raw.npy`, `X_ml_features.npy`, `Y_labels.npy`).
* **Demonstration Videos & High-Res Images:** Located in `Project_Docs/Relative_pics_&_videos/`.

---

## 4. Physical Asset Location

* **TetherIA Bionic Hand Assembly:** Stored in company.
* **Hall-Effect Muscle Deformation Armband:** The physical prototype is unavailable. Successors wishing to replicate are required to procure the relevant components online. 

---

## 5. Next Steps & Recommendations for Successors

1. **Expand Dataset Scale:** Collect multi-session, multi-subject muscle deformation data to improve generalisation across users.
2. **Feature Engineering & Model Optimisation:** Perform hyperparameter searches, feature engineering, and explore temporal architectures (e.g., LSTM or temporal CNNs). The primary objective is to elevate classification accuracy and mitigate baseline signal drift, whilst ensuring processing latency remains strictly within an acceptable threshold for real-time control responsiveness.
3. **Closed-Loop Hardware Integration:** Re-implement low-latency ROS2 or direct serial feedback to establish physical coupling between the deformation controller and the TetherIA hand once model stability is achieved.