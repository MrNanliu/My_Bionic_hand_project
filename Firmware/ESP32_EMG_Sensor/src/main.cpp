#include <Arduino.h>

const int sensorPin = 34;
const int windowSize = 20;     // 滤波窗口大小（20个样本求一次平均值）
int readings[windowSize];      // 存储最近的样本
int readIndex = 0;
long total = 0;
int baseline = 2048;           // ESP32 ADC 中点（12位下约为 1.65V）

void setup() {
  Serial.begin(115200);
  // 初始化数组
  for (int i = 0; i < windowSize; i++) readings[i] = 0;
  
  // 建议：在这里可以加一个自动校准逻辑，记录前 2 秒的均值作为 baseline
}

void loop() {
  // 1. 读取原始值
  int rawValue = analogRead(sensorPin);
  
  // 2. 整流：减去基准线并取绝对值（这步最关键！）
  int rectifiedValue = abs(rawValue - baseline);
  
  // 3. 简单平滑处理（滑动平均滤波）
  total = total - readings[readIndex];
  readings[readIndex] = rectifiedValue;
  total = total + readings[readIndex];
  readIndex = (readIndex + 1) % windowSize;
  
  int smoothedValue = total / windowSize;

  // 4. 发送给电脑
  // 建议同时发送原始值和滤波值，方便你在 Serial Plotter 里对比
  Serial.print(rectifiedValue); // 蓝线：整流后的波动
  Serial.print(" ");
  Serial.println(smoothedValue); // 红线：平滑后的发力趋势（AI 想要的 Y）

  delay(2); // 提高采样率到 500Hz
}