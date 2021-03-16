//==================================================================
// minimal web server controlling a single digital output intended
// to control a relay
//==================================================================

#define VERSION "2.103.161"
#define PROGRAM "wifi-relay"
#define CONTACT "bright.tiger@gmail.com"

//------------------------------------------------------------------
// you need to know the ip address assigned to the wifi relay when
// it connects to the network, but that will potentially change
// every time it connects to the wifi network.  you can find it
// from the dhcp server table on your wifi router, or by using the
// arp-scan utility, but either way you will want to know the mac
// address of the wifi relay board.  to find that, plug it in and
// turn on the serial monitor (at 115200) in the arduino ide, and
// hit the reset button on the board.  It will display the mac
// address on the console.  write it down, and perhaps write the
// last two digits on the board itself for future reference.
//
// if you can access the wifi router web interface you may be able
// to see the assigned ip address in the dhcp server status table.
// you may also have to option of making that address static, or
// locking it to the mac address.  if you have that option, take
// it and then things won't change unexpectidly in the future.
//
// if you prefer to do things from a command line, you can install
// the arp-scan and curl utilities like this:
//
//   sudo apt install app-scan
//   sudo apt install curl
//
// knowing the mac address of the wifi relay board, do something
// like this:
//
//   sudo arp-scan -q -l | grep 3c:61:05:d0:1e:cb
//
// then use the resulting ip address via your web browser, or use
// a curl command to directly control the relay:
//
//   curl -s http://192.168.29.111/off > /dev/null
//   curl -s http://192.168.29.111/on  > /dev/null
//   curl -s http://192.168.29.111/
//
// note: the built-in led will be on for relay off, and vice-versa
//------------------------------------------------------------------

//------------------------------------------------------------------
// uncomment this line if you want extra debug info on the serial
// console.  it is not helpful if things are working normally.
//------------------------------------------------------------------

// #define DEBUG

//------------------------------------------------------------------
// plug in your wifi credentials here
//------------------------------------------------------------------

const char* ssid     = "werecow29";
const char* password = "micro123" ;

//------------------------------------------------------------------
// the actual wifi interface library and objects
//------------------------------------------------------------------

#include <ESP8266WiFi.h>
WiFiServer server(80);
String header;

//------------------------------------------------------------------
// the relay interface - you can change the output pin if you like,
// but D0 is also the built-in led which can be handy.
//------------------------------------------------------------------

const int RelayOutput = D0;

const bool On  = true ;
const bool Off = false;

bool RelayState() {
  return digitalRead(RelayOutput) ? On : Off;
}

void RelaySet(bool OnOff) {
  Serial.println(           OnOff ? "relay on" : "relay off");
  digitalWrite(RelayOutput, OnOff ?        On  :        Off );
}

void RelayInit() {
  pinMode(RelayOutput, OUTPUT);
  RelaySet(Off);
}

//------------------------------------------------------------------
// some crude timing variables
//------------------------------------------------------------------

unsigned long currentTime = millis();
unsigned long previousTime = 0;
const long timeoutTime = 2000;

//------------------------------------------------------------------
// start up the serial console, turn the relay output off, and
// connect to the wifi network
//------------------------------------------------------------------

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println(PROGRAM " " VERSION);
  Serial.println();
  RelayInit();
  Serial.print("mac address: ");
  Serial.println(WiFi.macAddress());
  Serial.print("connecting to ssid: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("connected");
  Serial.print("ip address: ");
  Serial.println(WiFi.localIP());
  server.begin();
}

//------------------------------------------------------------------
// run the simple web server which allows for on/off relay control
//------------------------------------------------------------------

void loop(){
  WiFiClient client = server.available();
  if (client) {
    #ifdef DEBUG
      Serial.println("new client");
    #endif
    String currentLine = "";
    currentTime = millis();
    previousTime = currentTime;
    while (client.connected() && currentTime - previousTime <= timeoutTime) {
      currentTime = millis();
      if (client.available()) {
        char c = client.read();
        #ifdef DEBUG
          Serial.write(c);
        #endif
        header += c;
        if (c == '\n') {
          if (currentLine.length() == 0) {
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();
            if (header.indexOf("GET /on") >= 0) {
              RelaySet(On);
            } else if (header.indexOf("GET /off") >= 0) {
              RelaySet(Off);
            } else {
              if (int Offset = header.indexOf("GET /") > 0) {
                String Command = header.substr(Offset+5);
                Serial.print("Command [");
                Serial.print(Command);
                Serial.println("]");
            } }
            client.println("<!DOCTYPE html><html>");
            client.println("<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
            client.println("<link rel=\"icon\" href=\"data:,\">");
            client.println("<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}");
            client.println(".button { background-color: #195B6A; border: none; color: white; padding: 16px 40px;");
            client.println("text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}");
            client.println(".button2 {background-color: #77878A;}</style></head>");
            client.println("<body><h1>WiFi Relay Web Server</h1>");
            if (RelayState()) {
              client.println("<p>Relay is ON</p>");
              client.println("<p><a href=\"/off\"><button class=\"button button2\">Turn OFF</button></a></p>");
            } else {
              client.println("<p>Relay is OFF</p>");
              client.println("<p><a href=\"/on\"><button class=\"button\">Turn ON</button></a></p>");
            }
            client.println("</body></html>");
            client.println();
            break;
          } else {
            currentLine = "";
          }
        } else if (c != '\r') {
          currentLine += c;
    } } }
    header = "";
    client.stop();
    #ifdef DEBUG
      Serial.println("client disconnected");
      Serial.println("");
    #endif
} }

//==================================================================
// end
//==================================================================
