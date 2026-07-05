# Monitor-de-sensores-mqtt-Micropython

Sistema de monitoreo en tiempo real sencillo con tres sensores (infrarrojo, gas y ultrasónico) conectados a un ESP32, que publica las lecturas directamente a un broker MQTT público. Un dashboard web (HTML + Paho MQTT + Chart.js) se suscribe a esos mismos tópicos y muestra los datos en vivo con tarjetas de estado, gráficas y un log de mensajes.

El ESP32 se conecta directamente a WiFi y publica al broker por MQTT estándar (puerto 1883). El dashboard web se conecta al **mismo broker** pero por MQTT sobre WebSocket (puerto 8084), que es como los navegadores pueden hablar MQTT sin un puente intermedio.
 
## Componentes del proyecto
 
| Archivo | Rol |
|---|---|
| `main.py` | Firmware MicroPython que corre en el ESP32: lee los sensores y publica por MQTT |
| `dashboard.html` | Panel web standalone que se suscribe al broker y visualiza los datos en tiempo real |
| `umqtt/simple.py` | Driver MQTT para MicroPython (dependencia externa, ver más abajo) |
 
## Hardware necesario
 
| Componente | Cantidad | Notas |
|---|---|---|
| ESP32 (con WiFi) | 1 | Requiere WiFi para publicar directo al broker |
| Sensor infrarrojo (PIR o similar) | 1 | Salida digital, 0 = detectado |
| Sensor de gas (MQ-2 / MQ-5) | 1 | Salida analógica, vía ADC |
| Sensor ultrasónico (HC-SR04) | 1 | Trigger + Echo |
| Cables / protoboard | — | Para las conexiones |
 
## Conexiones (ESP32)
 
| Pin lógico | GPIO | Función |
|---|---|---|
| Trigger (ultrasónico) | 27 | Salida |
| Echo (ultrasónico) | 14 | Entrada |
| Infrarrojo | 13 | Entrada digital |
| Gas | 12 | Entrada analógica (ADC) |
 
> Ajusta los números de pin en `main.py` según tu placa específica.
 
## Instalación — ESP32 (`main.py`)
 
1. Flashea el ESP32 con el firmware de MicroPython.
2. Edita en `main.py` las credenciales de tu red:
```python
   WIFI_SSID = "tu_red"
   WIFI_PASSWORD = "tu_password"
```
3. Si tu build de MicroPython no incluye `umqtt.simple`, sube manualmente la carpeta `umqtt/` con `simple.py` al dispositivo.
4. Copia `main.py` a la raíz del sistema de archivos del ESP32 (Thonny, `mpremote`, `ampy`, etc.).
5. Reinicia el ESP32. Si el archivo se llama `main.py`, arranca automáticamente y comienza a publicar cada 5 segundos.
6. Verifica en la consola serial (`print(linea)`) que las lecturas se vean correctas antes de confiar en el dashboard.
## Instalación — Dashboard (`dashboard.html`)
 
1. Abre `dashboard.html` directamente en cualquier navegador moderno (no necesita servidor, es un archivo standalone).
2. En la barra de conexión, verifica los campos:
   - **Broker Host:** `broker.emqx.io` (mismo broker que usa el ESP32)
   - **Puerto WS:** `8084` (puerto WebSocket seguro del broker, distinto al 1883 que usa el ESP32)
   - **Client ID:** se genera automáticamente si lo dejas vacío
3. Haz clic en **Conectar**. El dashboard se suscribe automáticamente a los tres tópicos y empieza a mostrar datos en cuanto el ESP32 publique.
## Tópicos MQTT
 
| Tópico | Payload (JSON) | Ejemplo |
|---|---|---|
| `iot/sensor/infrarojo` | `{"valor": int, "estado": str}` | `{"valor": 0, "estado": "Persona detectada"}` |
| `iot/sensor/gas` | `{"valor": int, "estado": str}` | `{"valor": 1800, "estado": "Precaucion"}` |
| `iot/sensor/ultrasonico` | `{"valor": float, "estado": str}` | `{"valor": 45.32, "estado": "OK"}` |
 
## Notas importantes
 
- **Puertos distintos, mismo broker:** el ESP32 usa MQTT "crudo" por el puerto 1883, mientras que el navegador necesita MQTT sobre WebSocket (puerto 8084) porque los navegadores no pueden abrir sockets TCP directos. Esto es normal y no requiere ningún puente adicional — ambos hablan con el mismo broker público.
- **Broker público:** `broker.emqx.io` es un broker de pruebas gratuito y compartido. Cualquiera con el mismo tópico puede ver tus datos. Para un proyecto en producción o personalizado, se recomienda un broker propio o privado con autenticación.
- **Dashboard:** Se hizo uso de la IA para realizar el dashboard con el fin de ahorrar tiempo.
- **Sin puente serial:** a diferencia de versiones anteriores de este proyecto que usaban un script de Python en la PC (`pyserial` + `paho-mqtt`) como puente entre el ESP32 y el broker, esta versión hace que el ESP32 publique directamente — el script de puente ya no es necesario.
 
## Posibles mejoras
 
- [ ] Broker MQTT propio (Mosquitto local o servicio privado) en vez del público.
- [ ] Autenticación MQTT (usuario/contraseña o certificados TLS).
- [ ] Persistencia histórica de datos (base de datos o exportación CSV desde el dashboard).
- [ ] Notificaciones push cuando el estado de gas llegue a "PELIGRO".
- [ ] Reconexión automática de WiFi en el ESP32 si se cae la red (no solo la del broker).
