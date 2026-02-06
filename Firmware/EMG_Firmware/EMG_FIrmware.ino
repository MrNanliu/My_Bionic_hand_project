// --- ESP32 模拟肌电信号发生器 ---
// 只要接上USB，这段代码就会不断向电脑发送模拟数据

void setup() {
  // 初始化串口，波特率必须是 115200
  Serial.begin(115200);
}

void loop() {
  // 1. 制造一个正弦波信号 (范围 0 - 800)
  // 这个信号模拟了：肌肉用力 -> 放松 -> 用力 的循环过程
  // sin() 函数产生 -1 到 1 的波形，我们把它放大并抬升
  float wave = (sin(millis() / 500.0) + 1.0) * 400.0; 
  
  // 2. 加一点随机噪音 (模拟真实传感器会有的小抖动)
  int fake_emg_value = (int)wave + random(0, 50);
  
  // 3. 发送给电脑 (这一步最关键，Python就是读这个数)
  Serial.println(fake_emg_value);
  
  // 4. 控制发送速度 (每秒约20次，太快了Python处理不过来)
  delay(50);
}