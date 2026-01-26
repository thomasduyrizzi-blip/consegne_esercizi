import time
import random
import json
import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"

TOPICS = {
    "temperature": "sensor/temperature",
    "humidity": "sensor/humidity",
    "pressure": "sensor/pressure",
}

client = mqtt.Client()
client.connect(BROKER, 1883)

print("Simulator avviato (temperature, humidity, pressure)")

while True:
    now = int(time.time())

    temp_val = round(random.uniform(18, 30), 2)
    hum_val = round(random.uniform(30, 70), 2)
    pres_val = round(random.uniform(990, 1030), 2)

    temp_payload = {
        "sensor": "temperature",
        "value": temp_val,
        "unit": "C",
        "timestamp": now
    }

    hum_payload = {
        "sensor": "humidity",
        "value": hum_val,
        "unit": "%",
        "timestamp": now
    }

    pres_payload = {
        "sensor": "pressure",
        "value": pres_val,
        "unit": "hPa",
        "timestamp": now
    }

    client.publish(TOPICS["temperature"], json.dumps(temp_payload))
    client.publish(TOPICS["humidity"], json.dumps(hum_payload))
    client.publish(TOPICS["pressure"], json.dumps(pres_payload))

    print("Pubblicato:", temp_payload)
    print("Pubblicato:", hum_payload)
    print("Pubblicato:", pres_payload)

    time.sleep(1)
