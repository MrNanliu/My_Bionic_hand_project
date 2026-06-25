# sEMG Gesture Recognition Model Evaluation Data

## 1. Training Performance (Offline)

| Model Architecture | Evaluation Method | Accuracy | Feature Input |
| :--- | :--- | :--- | :--- |
| **Random Forest (RF)** | 5-Fold Cross Validation | **99.94%** | 30-dimensional manual features (RMS, MAV, WL, ZCR, STD) |
| **1D-CNN** | Hold-out Test Dataset | **70.95%** | 240-dimensional raw waveform (Zero-mean normalisation) |

## 2. Independent File Evaluation: Random Forest (RF)

| Target Gesture | Test File Name | Primary Prediction | Avg Confidence |
| :--- | :--- | :--- | :--- |
| **Fist** | `fist_raw_20260713_135146.txt` | **Fist: 100.0%** (38/38) | 0.99 |
| **Open Hand** | `open_hand_raw_20260713_134305.txt` | **Open Hand: 100.0%** (39/39) | 1.00 |
| **Pinch** | `pinch_raw_20260713_135809.txt` | **Pinch: 100.0%** (37/37) | 0.99 |
| **Wrist Down** | `wrist_down_raw_20260713_141304.txt` | **Wrist Down: 100.0%** (39/39) | 0.99 |
| **Wrist Up** | `wrist_up_raw_20260713_140416.txt` | **Wrist Up: 100.0%** (39/39) | 0.98 |

Due to its excessively high accuracy and limitations imposed by the dataset size, this test result exhibits overfitting. Therefore, the actual test results should be used to determine and analyze the results.

## 3. Independent File Evaluation: 1D-CNN

| Target Gesture | Test File Name | Primary Prediction | Avg Confidence | Secondary Predictions (Confusion) |
| :--- | :--- | :--- | :--- | :--- |
| **Fist** | `fist_raw_20260713_135146.txt` | **Fist: 92.1%** (35/38) | 0.87 | Pinch: 7.9% |
| **Wrist Up** | `wrist_up_raw_20260713_140416.txt` | **Wrist Up: 87.2%** (34/39) | 0.85 | Open Hand: 10.3%, Pinch: 2.6% |
| **Open Hand** | `open_hand_raw_20260713_134305.txt` | **Open Hand: 79.5%** (31/39) | 0.77 | Fist: 12.8%, Wrist Down: 5.1%, Wrist Up: 2.6% |
| **Wrist Down** | `wrist_down_raw_20260713_141304.txt` | **Wrist Down: 66.7%** (26/39) | 0.74 | Pinch: 12.8%, Wrist Up: 10.3%, Open Hand: 10.3% |
| **Pinch** | `pinch_raw_20260713_135809.txt` | **Pinch: 64.9%** (24/37) | 0.66 | Open Hand: 16.2%, Fist: 10.8%, Wrist Up: 5.4%, Wrist Down: 2.7% |

## 4. Real-Time Live Testing Analysis

### 4.1 1D-CNN Performance
Live system testing reveals the critical environmental variables absent in static offline files, demonstrating the necessity of the CNN's dynamic preprocessing pipeline.

| Environmental Factor | Video Observation | Impact on Inference | Model Response |
| :--- | :--- | :--- | :--- |
| **Severe Baseline Drift** | DC offsets across channels drop or rise by ~500-1000+ units during arm movements. | Absolute-value features (RMS/MAV) would exceed trained thresholds, causing traditional models to collapse. | The CNN's sliding window zero-mean normalisation strips the drift, maintaining valid probability distributions. |
| **Transitional Artifacts** | Large, erratic spikes occur during the physical transition between gestures. | Causes temporary misclassification or sudden drops in confidence scores. | The model dynamically recovers within milliseconds once the gesture stabilises, outputting accurate scores. |
| **Electrode Shift / Noise** | Resting state baselines do not return to their original starting coordinates after forceful contractions. | Introduces chronic noise to the static data profile. | The CNN ignores persistent offsets and identifies relative waveform patterns, preserving multi-class recognition. |

### 4.2 Random Forest (RF) Real-Time Analysis
Unlike the offline performance, the RF model's real-time performance is highly unstable.
* **The Issue:** Even with added real-time calibration, manual calibration, and introducing stored average baseline channel values for correction, the RF model fails to process live signals.
* **Observed Behavior:** The system gets "stuck" between *Wrist Up* and *Fist*, frequently switching between these two states regardless of the actual hand gesture. It is completely unable to identify *Pinch* or other gestures, and it appears the model simply cannot handle the raw, dynamic signal input in real-time, resulting in a system that ignores user input.

## 5. System Behavioral Analysis (CNN)

| Behaviour | Root Cause | Technical Explanation |
| :--- | :--- | :--- |
| **Temporal Flickering** | Independent Window Inference | Each sliding window is processed as an isolated event. Minor signal noise can cause rapid fluctuations in class probability. |
| **Inference Latency** | Buffer Accumulation | The system requires a full 40-sample window to generate a prediction, creating a physical delay. |
| **Complex Gesture Success** | Hierarchical Feature Learning | CNN learns non-linear patterns directly from raw waveforms, distinguishing subtle synergies like 'Pinch'. |

## 6. Summary

* **Offline vs. Real-world:** While the RF model dominates offline testing with near-perfect accuracy, this is misleading for real-time control. Actual sEMG signals are volatile—affected by time-dependent drift, electrical noise, and sensor degradation due to device wear. RF models built on static datasets simply cannot handle this dynamic "drift."
* **CNN Viability:** Actual testing shows that the 1D-CNN is indeed capable of identifying gestures under real-world, limited dataset/hardware conditions. This aligns with findings in major research papers, suggesting it is the more robust architecture for this application.
* **Safety & Conclusion:** Despite the CNN's potential, the current real-time accuracy and reliability still do not meet the safety standards required for reliable human-machine interaction.
    * **Decision:** The plan to connect this control system to the virtual or physical robotic hand is **cancelled**. 