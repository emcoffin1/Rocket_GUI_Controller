#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "ESP32";
const char* password = "12345";

WiFiServer tcpServer(8080);  // TCP Server on port 8080
WiFiUDP udpServer;           // UDP for telemetry
const int udpPort = 12345;

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nWiFi connected.");
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());

    tcpServer.begin();  // Start TCP server
    udpServer.begin(udpPort);  // Start UDP server
}

void loop() {
    WiFiClient client = tcpServer.available();  // Check for incoming TCP connection

    if (client) {
        Serial.println("TCP Client Connected");
        while (client.connected()) {
            if (client.available()) {
                String command = client.readStringUntil('\n');
                Serial.println("Received Command: " + command);

                if (command == "START_ENGINE") {
                    client.println("Engine Started");
                } else if (command == "STOP_ENGINE") {
                    client.println("Engine Stopped");
                } else {
                    client.println("Unknown Command");
                }
            }
        }
        client.stop();
        Serial.println("TCP Client Disconnected");
    }

    // Send sensor data via UDP
    String sensorData = "Temperature: 25.3, Pressure: 1002";
    udpServer.beginPacket("192.168.1.50", 12345);  // Send to Python client IP
    udpServer.print(sensorData);
    udpServer.endPacket();

    delay(1000);  // Send every 1 second
}
