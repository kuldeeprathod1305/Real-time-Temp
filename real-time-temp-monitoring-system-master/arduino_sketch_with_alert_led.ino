#include <WiFi.h>
#include <DHT.h>
#include <ThingSpeak.h>

const char* ssid = "iPhone";
const char* password = "12345678";

unsigned long channelID = 3134042;
const char* writeAPIKey = "PLBN60EMMAH31KPA";

#define DHTPIN 4
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);
WiFiClient client;

unsigned long lastSendTime = 0;
const unsigned long interval = 60000;

void setup() {
  Serial.begin(115200);
  dht.begin();
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  ThingSpeak.begin(client);
}

void loop() {
  unsigned long currentTime = millis();
  if (currentTime - lastSendTime >= interval) {
    lastSendTime = currentTime;
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    if (!isnan(temperature) && !isnan(humidity)) {
      ThingSpeak.setField(1, temperature);
      ThingSpeak.setField(2, humidity);
      ThingSpeak.writeFields(channelID, writeAPIKey);
    }
  }
}
