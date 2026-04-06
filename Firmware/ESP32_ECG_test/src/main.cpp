#include <Arduino.h>

const int sensorPin = 34; // 刚才我们把信号线接在了 D34 引脚

void setup() {
  // 开启串口通信，波特率 115200 (必须与 Python 脚本一致)
  Serial.begin(115200); 
}

void loop() {
  // 读取 D34 引脚上的模拟电压值 (ESP32 的读取范围是 0 - 4095)
  int sensorValue = analogRead(sensorPin); 
  
  // 将读取到的数字发送给电脑
  Serial.println(sensorValue); 
  
  // 延时 10 毫秒，控制采样率，避免把电脑串口卡死
  delay(10); 
}