//==================================================================
// minimal web WebServer controlling a single digital output intended
// to control a relay
//==================================================================

#define VERSION "2.103.282"
#define PROGRAM "wifi-relay"
#define CONTACT "bright.tiger@gmail.com"

//------------------------------------------------------------------
// diagnostic and status information is sent to the serial console
//------------------------------------------------------------------

#define CONSOLE_BAUDRATE 115200

//------------------------------------------------------------------
// feature flags - set AUTO_OFF to 0 to disable that feature
//------------------------------------------------------------------

#define RELAY_INIT  false  // false for off, true for on
#define RELAY_ON        1  // 0 for active low, 1 for active high
#define AUTO_OFF      360  // turn off automatically after so many seconds

//------------------------------------------------------------------
// you need to know the ip address assigned to the wifi relay when
// it connects to the network, but that will potentially change
// every time it connects to the wifi network.  you can find it
// from the dhcp WebServer table on your wifi router, or by using the
// arp-scan utility, but either way you will want to know the mac
// address of the wifi relay board.  to find that, plug it in and
// turn on the serial monitor (at 115200) in the arduino ide, and
// hit the reset button on the board.  It will display the mac
// address on the console.  write it down, and perhaps write the
// last two digits on the board itself for future reference.
//
// if you can access the wifi router web interface you may be able
// to see the assigned ip address in the dhcp WebServer status table.
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
WiFiServer WebServer(80);
String Header;

//------------------------------------------------------------------
// some typedefs to keep us honest
//------------------------------------------------------------------

typedef const               char * ccptr ;
typedef const   signed      int    cint16;
typedef       unsigned long int     bit32;

//------------------------------------------------------------------
// we need a wifi network connection to report data to corlysis,
// and will pick the one with the strongest signal from the
// following list
//------------------------------------------------------------------

typedef struct {
  ccptr Location, Ssid, Password;
} t_WiFiNetwork;

#define WIFI_NETWORKS 2

const t_WiFiNetwork WiFiNetwork[WIFI_NETWORKS] = {
  { "lab"  , "werecow25", "micro123" },
  { "house", "werecow29", "micro123" }
};

//------------------------------------------------------------------
// some crude timing variables
//------------------------------------------------------------------

      bit32 CurrentTime  = millis();
      bit32 PreviousTime =        0;
      bit32 RelayTime    =        0;
const bit32 TimeoutTime  =     2000;

//------------------------------------------------------------------
// the relay interface - you can change the output pin if you like,
// but D0 is also the built-in led which can be handy.
//------------------------------------------------------------------

const int RelayOutput = D0;

const bool On  = RELAY_ON ? true  : false; // was true
const bool Off = RELAY_ON ? false : true ; // was false

bool RelayState() {
  return digitalRead(RelayOutput) ? On : Off;
}

void RelaySet(bool OnOff) {
  Serial.println(           OnOff ? "  relay on" : "  relay off");
  digitalWrite(RelayOutput, OnOff ?          On  :          Off );
  RelayTime = millis();
}

void RelayInit() {
  pinMode(RelayOutput, OUTPUT);
  RelaySet(RELAY_INIT);
}

//------------------------------------------------------------------
// start up the serial console, turn the relay output off, and
// connect to the wifi network
//------------------------------------------------------------------

void setup() {
  ccptr BestSsid     = NULL;
  ccptr BestPassword = NULL;
  ccptr BestLocation = NULL;
  int32 BestRssi = -200;
  Serial.begin(CONSOLE_BAUDRATE);
  delay(1000);
  Serial.println();
  Serial.println(PROGRAM " " VERSION);
  Serial.println();
  RelayInit();
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  Serial.print("mac address: ");
  Serial.println(WiFi.macAddress());
  Serial.println("starting wifi scan...");
  while (BestRssi < -180) {
    if (int ScanResults = WiFi.scanNetworks(false, true)) { // async, hidden
      if (ScanResults > 0) {
        String Ssid;
        int32 Rssi;
        byte EncryptionType;
        uint8_t * Bssid;
        bool Hidden;
        int32 Channel;
        Serial.printf("  found %d networks\n", ScanResults);
        for (int i = 0; i < ScanResults; i++) {
          WiFi.getNetworkInfo(i, Ssid, EncryptionType, Rssi, Bssid, Channel, Hidden);
          Serial.printf(PSTR("    %02d: [CH %02d] [%02X:%02X:%02X:%02X:%02X:%02X] %ddBm %c %c %s\n"),
                        i,
                        Channel,
                        Bssid[0], Bssid[1], Bssid[2],
                        Bssid[3], Bssid[4], Bssid[5],
                        Rssi,
                        (EncryptionType == ENC_TYPE_NONE) ? ' ' : '*',
                        Hidden ? 'H' : 'V',
                        Ssid.c_str());
          for (int Network = 0; Network < WIFI_NETWORKS; Network++) {
            if (Ssid == WiFiNetwork[Network].Ssid) {
              if (Rssi > BestRssi) {
                BestRssi = Rssi;
                BestLocation = WiFiNetwork[Network].Location;
                BestSsid     = WiFiNetwork[Network].Ssid    ;
                BestPassword = WiFiNetwork[Network].Password;
          } } }
          delay(0);
        }
      } else {
        Serial.printf(PSTR("  wifi scan error %d"), ScanResults);
      }
    } else {
      Serial.println("  no networks found");
    }
    if (BestRssi < -180) {
      delay(5000);
  } }
  Serial.println("autoselected network");
  Serial.printf("      rssi: %ddBm\n", BestRssi    );
  Serial.printf("  location: %s\n", BestLocation);
  Serial.printf("      ssid: %s\n", BestSsid    );
  Serial.printf("  password: %s\n", BestPassword);
  Serial.print("starting wifi...");
  delay(1000);
  WiFi.mode(WIFI_STA);
  WiFi.begin(BestSsid, BestPassword);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("  wifi connected - ip address: ");
  Serial.println(WiFi.localIP());
  WebServer.begin();
  Serial.print("on  = "); Serial.println(On );
  Serial.print("off = "); Serial.println(Off);
  Serial.print("relay = "); Serial.println(RelayState());
}

//------------------------------------------------------------------
// run the simple web WebServer which allows for on/off relay control
//------------------------------------------------------------------

void loop(){
  String Command = "";
  WiFiClient client = WebServer.available();
  if (RelayState() == On) {
    if (AUTO_OFF) {
      bit32 AutoTime = millis();
      if (((AutoTime - RelayTime) / 1000) > AUTO_OFF) {
        RelaySet(false);
  } } }
  if (client) {
    #ifdef DEBUG
      Serial.println("new client");
    #endif
    String CurrentLine = "";
    CurrentTime = millis();
    PreviousTime = CurrentTime;
    while (client.connected() && CurrentTime - PreviousTime <= TimeoutTime) {
      CurrentTime = millis();
      if (client.available()) {
        char c = client.read();
        #ifdef DEBUG
          Serial.write(c);
        #endif
        Header += c;
        if (c == '\n') {
          if (CurrentLine.length() == 0) {
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();
            #ifdef DEBUG
              Serial.println(Header);
            #endif
            if (Header.indexOf("GET / ") < 0) {
              if (Header.indexOf("GET /on ") >= 0) {
                RelaySet(true);
              } else if (Header.indexOf("GET /off ") >= 0) {
                RelaySet(false);
              } else {
                int Offset = Header.indexOf("GET /");
                if (Offset >= 0) {
                  Command = Header.substring(Offset+5);
                  Offset = Command.indexOf(" ");
                  if (Offset > 0) {
                    Command = Command.substring(0, Offset);
            } } } }
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
            CurrentLine = "";
          }
        } else if (c != '\r') {
          CurrentLine += c;
      } }
    }
    Header = "";
    client.stop();
    #ifdef DEBUG
      Serial.println("client disconnected");
      Serial.println("");
    #endif
    if (Command.length() > 0) {
      Serial.print("start [");
      Serial.print(Command);
      Serial.println("]...");
      while (Command.length() > 0) {
        if (Command.startsWith("+")) {
          RelaySet(true);
          Command = Command.substring(1);
        } else if (Command.startsWith("-")) {
          RelaySet(false);
          Command = Command.substring(1);
        } else {
          int Delay = Command.toInt();
          Serial.print("  delay ");
          Serial.println(Delay);
          delay(Delay * 1000);
          Command = Command.substring(String(Delay).length());
      } }
      Serial.println("done");
} } }

//==================================================================
// end
//==================================================================
