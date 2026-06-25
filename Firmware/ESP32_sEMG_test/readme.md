### Hardware Wiring & Pin Mapping

**1. EMG Sensor Pinout**
* Pin 1: GND
* Pin 2: 5V
* Pin 3: A0
* Port 4: Audio Jack

**2. ESP32 Connection**

**Channel A: Inner Flexor**
* Sensor Pin 1 (GND) -> ESP32 GND
* Sensor Pin 2 (5V)  -> ESP32 5V
* Sensor Pin 3 (A0)  -> ESP32 GPIO 35

**Channel B: Outer Extensor**
* Sensor Pin 1 (GND) -> ESP32 GND
* Sensor Pin 2 (5V)  -> ESP32 5V
* Sensor Pin 3 (A0)  -> ESP32 GPIO 34