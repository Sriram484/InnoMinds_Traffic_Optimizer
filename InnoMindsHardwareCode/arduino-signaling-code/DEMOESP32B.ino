#include <WiFi.h>
#include <PubSubClient.h>

// Replace with your network credentials
// const char* ssid = "Airtel_PREMIER ILLAM";
// const char* password = "28130429";
const char* ssid = "Iot";
const char* password = "12345678";

// MQTT Broker settings
const char* mqtt_server = "192.168.105.30";  // IP address of your MQTT broker
const int mqtt_port = 1883;  // Default MQTT port
const char* mqtt_topic = "traffic_lights_B";  // Topic for ESP32 Point B

WiFiClient espClient;
PubSubClient client(espClient);

// Traffic Light Pins
const int NS_Red = 13, NS_Yellow = 12, NS_Green = 14;
const int EW_Red = 26, EW_Yellow = 25, EW_Green = 33;
const int SN_Red = 15, SN_Yellow = 2, SN_Green = 4;
const int WE_Red = 5, WE_Yellow = 18, WE_Green = 19;

void setup() {
  Serial.begin(9600);
  setupWiFi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  pinMode(NS_Red, OUTPUT);
  pinMode(NS_Yellow, OUTPUT);
  pinMode(NS_Green, OUTPUT);

  pinMode(EW_Red, OUTPUT);
  pinMode(EW_Yellow, OUTPUT);
  pinMode(EW_Green, OUTPUT);

  pinMode(SN_Red, OUTPUT);
  pinMode(SN_Yellow, OUTPUT);
  pinMode(SN_Green, OUTPUT);

  pinMode(WE_Red, OUTPUT);
  pinMode(WE_Yellow, OUTPUT);
  pinMode(WE_Green, OUTPUT);

  resetAllLights();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client_B")) {
      Serial.println("connected");
      client.subscribe(mqtt_topic);  // Subscribe to the topic
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String command;
  for (int i = 0; i < length; i++) {
    command += (char)payload[i];
  }
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  Serial.println(command);
  processCommand(command);
}

void processCommand(String command) {
  Serial.print("Processing command: ");
  Serial.println(command);
  resetAllLights();

  if (command == "NS_GREEN") {
    digitalWrite(NS_Green, HIGH);
    digitalWrite(EW_Red, HIGH);
    digitalWrite(SN_Red, HIGH);
    digitalWrite(WE_Red, HIGH);
  } else if (command == "NS_YELLOW") {
    digitalWrite(NS_Yellow, HIGH);
    digitalWrite(EW_Red, HIGH);
    digitalWrite(SN_Red, HIGH);
    digitalWrite(WE_Red, HIGH);
  } else if (command == "EW_GREEN") {
    digitalWrite(EW_Green, HIGH);
    digitalWrite(NS_Red, HIGH);
    digitalWrite(SN_Red, HIGH);
    digitalWrite(WE_Red, HIGH);
  } else if (command == "EW_YELLOW") {
    digitalWrite(EW_Yellow, HIGH);
    digitalWrite(NS_Red, HIGH);
    digitalWrite(SN_Red, HIGH);
    digitalWrite(WE_Red, HIGH);
  } else if (command == "SN_GREEN") {
    digitalWrite(SN_Green, HIGH);
    digitalWrite(NS_Red, HIGH);
    digitalWrite(EW_Red, HIGH);
    digitalWrite(WE_Red, HIGH);
  } else if (command == "SN_YELLOW") {
    digitalWrite(SN_Yellow, HIGH);
    digitalWrite(NS_Red, HIGH);
    digitalWrite(EW_Red, HIGH);
    digitalWrite(WE_Red, HIGH);
  } else if (command == "WE_GREEN") {
    digitalWrite(WE_Green, HIGH);
    digitalWrite(NS_Red, HIGH);
    digitalWrite(EW_Red, HIGH);
    digitalWrite(SN_Red, HIGH);
  } else if (command == "WE_YELLOW") {
    digitalWrite(WE_Yellow, HIGH);
    digitalWrite(NS_Red, HIGH);
    digitalWrite(EW_Red, HIGH);
    digitalWrite(SN_Red, HIGH);
  }
   else if (command == "ALL_RED") {
    digitalWrite(NS_Red, HIGH);
    digitalWrite(EW_Red, HIGH);
    digitalWrite(SN_Red, HIGH);
    digitalWrite(WE_Red, HIGH);
  }
}

void resetAllLights() {
  digitalWrite(NS_Red, LOW);
  digitalWrite(NS_Yellow, LOW);
  digitalWrite(NS_Green, LOW);

  digitalWrite(EW_Red, LOW);
  digitalWrite(EW_Yellow, LOW);
  digitalWrite(EW_Green, LOW);

  digitalWrite(SN_Red, LOW);
  digitalWrite(SN_Yellow, LOW);
  digitalWrite(SN_Green, LOW);

  digitalWrite(WE_Red, LOW);
  digitalWrite(WE_Yellow, LOW);
  digitalWrite(WE_Green, LOW);
}

void setupWiFi() {
  delay(10);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi");
}
