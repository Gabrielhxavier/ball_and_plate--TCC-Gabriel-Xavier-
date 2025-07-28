#include <Arduino.h>
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

// PINOS PWM PARA SERVOS E CONFIGURAÇÃO
const int servoPinX = 33;
const int servoPinY = 15;
const int canalPWM_X = 0;
const int canalPWM_Y = 1;
const int freqPWM = 50;
const int resolucaoPWM = 16;
const int pwmMin = 1638;
const int pwmMax = 8192;
const int pwmNeutro = 4915;

// PARAMETROS PID 
float Kp = 7.0, Ki = 1.0, Kd = 4.0, N = 15.0, Ts = 0.02;

// COEFICIENTES CALCULADOS DO CONTROLADOR
float a0_i, a1_i, c0_d, c1_d, d1_d;

// VARIÁVEIS PID X - EIXO X
float erroX = 0, erroX_1 = 0, somaIX = 0, derivX_1 = 0, uX = 0;

// VARIÁVEIS PID Y - EIXO Y
float erroY = 0, erroY_1 = 0, somaIY = 0, derivY_1 = 0, uY = 0;

// TEMPO DE CONTROLE
unsigned long tempoAnterior = 0;
const int Ts_ms = 20;

// POSIÇÃO DA ESFERA (da câmera)
float posX = 0, posY = 0;

// SETPOINT (CENTRO DA MESA) - CALIBRADO
const float setX = 225.0 / 2.0;
const float setY = 173.0 / 2.0;

// FUNÇÃO DE LIMITAÇÃO DA AÇÃO PWM
int limitarPWM(float valor) {
  if (valor < pwmMin) return pwmMin;
  if (valor > pwmMax) return pwmMax;
  return (int)valor;
}

// FUNÇAO PARA CÁLCULO DOS COEFICIENTES - CONTROLADOR PID
void calcularCoeficientes() {
  a0_i = (Ki * Ts) / 2.0;
  a1_i = a0_i;

  float den = N * Ts + 2.0;
  c0_d = (2.0 * Kd * N) / den;
  c1_d = -c0_d;
  d1_d = (2.0 - N * Ts) / den;
}

// SETUP (INICIALIZAÇÃO)
void setup() {
  Serial.begin(115200);      // USB para receber posição da bola
  SerialBT.begin("BallPlate_BT"); // Bluetooth para visualização

  ledcSetup(canalPWM_X, freqPWM, resolucaoPWM);
  ledcAttachPin(servoPinX, canalPWM_X);
  ledcSetup(canalPWM_Y, freqPWM, resolucaoPWM);
  ledcAttachPin(servoPinY, canalPWM_Y);

  ledcWrite(canalPWM_X, pwmNeutro);
  ledcWrite(canalPWM_Y, pwmNeutro);

  calcularCoeficientes();

  SerialBT.println("tempo_ms,posX,setX,posY,setY");
}

// LOOP PRINCIPAL
void loop() {
  // CALCULO DO TEMPO DE AMOSTRAGEM
  if (millis() - tempoAnterior >= Ts_ms) {
    tempoAnterior = millis();

    // Recebe coordenadas (formato "x,y\n") da câmera via USB
    if (Serial.available()) {
      String dados = Serial.readStringUntil('\n');
      int sep = dados.indexOf(',');
      if (sep != -1) {
        posX = dados.substring(0, sep).toFloat();
        posY = dados.substring(sep + 1).toFloat();
      }
    }

    // PID X
    erroX = setX - posX;
    float P_X = Kp * erroX;
    somaIX += a0_i * erroX + a1_i * erroX_1;
    float D_X = c0_d * erroX + c1_d * erroX_1 + d1_d * derivX_1;

    uX = P_X + somaIX + D_X;
    erroX_1 = erroX;
    derivX_1 = D_X;

    ledcWrite(canalPWM_X, limitarPWM(pwmNeutro + uX)); // AÇÃO DE CONTROLE

    // === PID Y ===
    erroY = setY - posY;
    float P_Y = Kp * erroY;
    somaIY += a0_i * erroY + a1_i * erroY_1;
    float D_Y = c0_d * erroY + c1_d * erroY_1 + d1_d * derivY_1;

    uY = P_Y + somaIY + D_Y;
    erroY_1 = erroY;
    derivY_1 = D_Y;

    ledcWrite(canalPWM_Y, limitarPWM(pwmNeutro + uY)); // AÇÃO DE CONTROLE

    // EXPORTAÇÃO DOS DADOS VIA BLUETOOTH
    SerialBT.print(millis()); SerialBT.print(",");
    SerialBT.print(posX, 3); SerialBT.print(",");
    SerialBT.print(setX, 3); SerialBT.print(",");
    SerialBT.print(posY, 3); SerialBT.print(",");
    SerialBT.println(setY, 3);
  }
}
