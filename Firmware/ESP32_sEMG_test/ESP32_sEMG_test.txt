const int PIN_SEMG1 = 35; 
const int PIN_SEMG2 = 34; 

const int WINDOW_SIZE = 50; 
int history1[WINDOW_SIZE] = {0};
int history2[WINDOW_SIZE] = {0};
int buf_index = 0;

float auto_baseline1 = 0;
float auto_baseline2 = 0;

void setup() {
  Serial.begin(115200);
  
  long sum_cal1 = 0;
  long sum_cal2 = 0;
  for(int i = 0; i < 300; i++) {
    sum_cal1 += analogRead(PIN_SEMG1);
    sum_cal2 += analogRead(PIN_SEMG2);
    delay(10);
  }
  auto_baseline1 = sum_cal1 / 300.0;
  auto_baseline2 = sum_cal2 / 300.0;
}

void loop() {
  int raw1 = analogRead(PIN_SEMG1);
  int raw2 = analogRead(PIN_SEMG2);

  int abs_signal1 = abs(raw1 - auto_baseline1);
  int abs_signal2 = abs(raw2 - auto_baseline2);

  history1[buf_index] = abs_signal1;
  history2[buf_index] = abs_signal2;
  buf_index = (buf_index + 1) % WINDOW_SIZE;

  long sum1 = 0, sum2 = 0;
  for(int i = 0; i < WINDOW_SIZE; i++) {
    sum1 += history1[i];
    sum2 += history2[i];
  }
  
  float env1 = sum1 / (float)WINDOW_SIZE;
  float env2 = sum2 / (float)WINDOW_SIZE;

  Serial.print(env1);
  Serial.print(",");
  Serial.println(env2);

  delay(10); 
}