# Data Collection Protocol

This document outlines the standardisation protocol for the kinematic and sensor data collection phase. The dataset is designed to evaluate the classification performance boundaries of the algorithm under strict hardware constraints. The camera-based vision system is utilised strictly for automated data labelling during this collection phase and does not serve as a real-time multimodal input for final deployment.

## Global Execution Constraints

To ensure data integrity and prevent baseline contamination, the following hardware and physical constraints must be strictly observed throughout the recording process:

* **Maintain Hardware Pre-load:** Do not touch, adjust, or rotate the armband once the session begins. All gestures must share an identical mechanical baseline.
* **Eliminate Mechanical Hysteresis:** After completing a 2.5-second recording window, completely relax the forearm muscles and pause for 1 to 2 seconds before triggering the next recording.
* **Volume Standardisation:** Execute exactly 50 repetitions per gesture to maintain a balanced dataset matrix.

---

## Execution Sequence

Data must be collected in the following order to establish macro-level bounds before capturing micro-level deformations.

### 1. Fist (Rest)
* **Objective:** Establish the static baseline and electrical noise floor.
* **Protocol:** Forearm resting flat on a surface, completely relaxed. Record 50 pure samples with zero intentional muscle activation.

### 2. Open Hand
* **Objective:** Extract the outward expansion range of the extensor muscles.
* **Repetitions 1–15 (Standard Baseline):** Forearm flat on the desk, extending all five fingers outwards and backwards to the physical limit.
* **Repetitions 16–30 (Pose Crosstalk):** Forearm suspended. Alter the rotational angle of the arm while maintaining the open hand extension.
* **Repetitions 31–45 (Force Gradient):** 5 minimal extensions (overcoming gravity only), 5 standard extensions, and 5 rigid extensions (fingers slightly hyperextended).
* **Repetitions 46–50 (Transient Response):** Instantaneous, explosive extension from a relaxed or fist state.

### 3. Pinch
* **Objective:** Establish boundaries for minor local muscle deformations with a low signal-to-noise ratio.
* **Constraint:** You must use the **thumb and middle finger** or **thumb and ring finger** to ensure the vision labelling oracle registers the state correctly.
* **Repetitions 1–15 (Standard Baseline):** Forearm flat on the desk, executing a precise pinch.
* **Repetitions 16–30 (Isolated Control):** Maintain the pinch while altering the posture of the non-participating fingers (e.g., index finger fully straight versus naturally curled).
* **Repetitions 31–45 (Force Gradient):** 5 light touches (finger pads only), 5 standard pinches, and 5 maximum-force pinches.
* **Repetitions 46–50 (Anti-Gravity Crosstalk):** Forearm fully suspended, introducing crosstalk from stabilising muscle groups.

### 4. Wrist Up
* **Objective:** Capture the primary displacement of the forearm muscle group during upward wrist flexion.
* **Repetitions 1–15 (Standard Baseline):** Forearm flat on the desk, wrist suspended over the edge, extending the back of the hand towards the forearm.
* **Repetitions 16–30 (Deflection Crosstalk):** Execute the extension while simultaneously inducing slight left or right radial/ulnar deviations.
* **Repetitions 31–45 (Force Gradient):** 5 minimal lifts, 5 standard extensions, and 5 maximum-angle extensions.
* **Repetitions 46–50 (Suspended Dynamic):** Execute the extension with the entire arm suspended.

### 5. Wrist Down
* **Objective:** Capture the primary displacement of the forearm muscle group during downward wrist flexion.
* **Repetitions 1–15 (Standard Baseline):** Forearm flat on the desk, wrist suspended over the edge, flexing the palm downwards and inwards.
* **Repetitions 16–30 (Digit Crosstalk):** 5 flexions with fingers fully extended, and 10 flexions while maintaining a loose fist (to test the superposition of finger and wrist flexors).
* **Repetitions 31–45 (Force Gradient):** 5 minimal flexions, 5 standard flexions, and 5 maximum-angle flexions.
* **Repetitions 46–50 (Suspended Dynamic):** Execute the flexion with the entire arm suspended.