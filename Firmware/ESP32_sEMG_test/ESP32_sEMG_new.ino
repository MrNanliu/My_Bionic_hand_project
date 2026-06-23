const int PIN_SEMG1 = 35;
const int PIN_SEMG2 = 34;

const int WINDOW_SIZE = 50;
int history1[WINDOW_SIZE] = {0};
int history2[WINDOW_SIZE] = {0};
int buf_index = 0;

float auto_baseline1 = 0;
float auto_baseline2 = 0;

unsigned long lastSampleTime = 0;
const unsigned long sampleInterval = 1000;

unsigned long lastPrintTime = 0;
const unsigned long printInterval = 20000;

long sum1 = 0;
long sum2 = 0;

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
  unsigned long currentMicros = micros();

  if (currentMicros - lastSampleTime >= sampleInterval) {
    lastSampleTime = currentMicros;

    int raw1 = analogRead(PIN_SEMG1);
    int raw2 = analogRead(PIN_SEMG2);

    int abs_signal1 = abs(raw1 - auto_baseline1);
    int abs_signal2 = abs(raw2 - auto_baseline2);

    sum1 -= history1[buf_index];
    sum2 -= history2[buf_index];

    history1[buf_index] = abs_signal1;
    history2[buf_index] = abs_signal2;

    sum1 += history1[buf_index];
    sum2 += history2[buf_index];

    buf_index = (buf_index + 1) % WINDOW_SIZE;
  }

  if (currentMicros - lastPrintTime >= printInterval) {
    lastPrintTime = currentMicros;
    
    float env1 = sum1 / (float)WINDOW_SIZE;
    float env2 = sum2 / (float)WINDOW_SIZE;

    Serial.print("Inner_Envelope:");
    Serial.print(env1);
    Serial.print(",Outer_Envelope:");
    Serial.println(env2);
  }
}