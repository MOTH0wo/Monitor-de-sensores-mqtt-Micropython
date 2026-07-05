from machine import Pin, ADC, time_pulse_us
from umqtt.simple import MQTTClient
import network
import time
import ujson

# Configuración WiFi
WIFI_SSID = "tu_red"
WIFI_PASSWORD = "tu_password"

# Configuración MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "esp32_sensores"

TOPIC_INFRAROJO = b"iot/sensor/infrarojo"
TOPIC_GAS = b"iot/sensor/gas"
TOPIC_ULTRA = b"iot/sensor/ultrasonico"

# Sensores (Cambiar segun tu disposicion de pines)
trigger = Pin(27, Pin.OUT)
echo = Pin(14, Pin.IN)
infrarojo = Pin(13, Pin.IN)
gas = ADC(Pin(12))
gas.atten(ADC.ATTN_11DB)

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("WiFi conectada:", wlan.ifconfig())

def conectar_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print("Conectado al broker MQTT")
    return client

conectar_wifi()
client = conectar_mqtt()

while True:
    # Sensor Ultrasonico
    trigger.value(0)
    time.sleep_us(2)
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)
    duracion = time_pulse_us(echo, 1, 30000)
    distancia = (duracion * 0.0343) / 2
    estado_ultra = "OK" if duracion > 0 else "Error"

    # Sensor infrarojo
    movimiento = infrarojo.value()
    if movimiento == 0:
        estado_infrarojo = "Persona detectada"
    else:
        estado_infrarojo = "Sin movimiento"

    # Sensor de Gas
    valor_gas = gas.read()
    if valor_gas < 1500:
        estado_gas = "Normal"
    elif valor_gas < 2500:
        estado_gas = "Precaucion"
    else:
        estado_gas = "PELIGRO"

    linea = "INFRAROJO:{}|GAS:{}|ULTRA:{:.2f}|ESTADO_GAS:{}|ESTADO_INFRAROJO:{}|ESTADO_ULTRA:{}".format(
        movimiento, valor_gas, distancia, estado_gas, estado_infrarojo, estado_ultra)
    print(linea)

    # --- Payloads: mismos campos y estructura que tu script de PC ---
    payload_infrarojo = ujson.dumps({"valor": movimiento, "estado": estado_infrarojo})
    payload_gas = ujson.dumps({"valor": valor_gas, "estado": estado_gas})
    payload_ultra = ujson.dumps({"valor": round(distancia, 2), "estado": estado_ultra})

    try:
        client.publish(TOPIC_INFRAROJO, payload_infrarojo)
        client.publish(TOPIC_GAS, payload_gas)
        client.publish(TOPIC_ULTRA, payload_ultra)
    except Exception as ex:
        print("Error al publicar MQTT:", ex)
        try:
            client = conectar_mqtt()   # reintenta reconectar si se cayó
        except Exception as ex2:
            print("No se pudo reconectar:", ex2)

    time.sleep(5)
