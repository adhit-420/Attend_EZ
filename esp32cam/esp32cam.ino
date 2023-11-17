#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>
 
// Provide the wifi username (WIFI_SSID) and passwords (WIFI_PASS) here
const char *WIFI_SSID = "Rishikesh's Phone";
const char *WIFI_PASS = "vgnp4148";

// Enabling the web sevrer
WebServer server(80);

// The following three variables are for defining the rrsolutions of the images
// We can check the documentation for the given module, and tweak the values accordingly
static auto loRes = esp32cam::Resolution::find(320, 240);
static auto midRes = esp32cam::Resolution::find(350, 530);
static auto hiRes = esp32cam::Resolution::find(800, 600);

// Webserver logic
void serveJpg()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr)
  {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

// Low Resolution  (320, 240)
void handleJpgLo()
{
  if (!esp32cam::Camera.changeResolution(loRes))
  {
    Serial.println("SET-LO-RES FAIL");
  }
  serveJpg();
}

// Meidum resolution (350, 530)
void handleJpgMid()
{
  if (!esp32cam::Camera.changeResolution(midRes))
  {
    Serial.println("SET-MID-RES FAIL");
  }
  serveJpg();
}

// High resolution (800, 600)
void handleJpgHi()
{
  if (!esp32cam::Camera.changeResolution(hiRes))
  {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}

// Setup function, for setting all the pinModes
// Checks if the camera has been connected or not
/*
  If yes: 
    CAMERA OK
  else: 
    CAMERA FAIL
*/
void setup()
{
  Serial.begin(115200);
  
  Serial.println();
  {
    using namespace esp32cam;

    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);

    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL"); 
  }

  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
  }

  // The following information is displayed in the serial monitor
  Serial.print("http://");
  Serial.println(WiFi.localIP());

  // Three modes of operation for the camera
  Serial.println("  /cam-lo.jpg");
  Serial.println("  /cam-hi.jpg");
  Serial.println("  /cam-mid.jpg");

  // We can choose from one of the three instantiated servers 
  server.on("/cam-lo.jpg", handleJpgLo);
  server.on("/cam-hi.jpg", handleJpgHi);
  server.on("/cam-mid.jpg", handleJpgMid);

  // Server begin
  server.begin();
}

// This is the loop function
// This function is run repeatedly 
void loop()
{
  server.handleClient();
}
