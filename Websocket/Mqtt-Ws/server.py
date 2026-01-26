import asyncio
import json
import logging

import tornado.web
import tornado.websocket
import aiomqtt

BROKER = "test.mosquitto.org"
TOPICS = [
    ("sensor/temperature", 0),
    ("sensor/humidity", 0),
    ("sensor/pressure", 0),
]

clients = set()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class SensorHandler(tornado.web.RequestHandler):
    def get(self, sensor_name):
        # /sensor/temperature -> sensor_temperature.html
        template_name = f"{sensor_name}.html"
        self.render(template_name)


class WSHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket aperto")
        clients.add(self)

    def on_close(self):
        print("WebSocket chiuso")
        clients.discard(self)


async def mqtt_listener():
    logging.info("Connessione al broker MQTT...")
    async with aiomqtt.Client(BROKER) as client:
        # subscribe multiplo
        await client.subscribe(TOPICS)
        logging.info(f"Iscritto ai topic: {TOPICS}")

        async for message in client.messages:
            payload = message.payload.decode()
            data = json.loads(payload)

            # determinare il tipo di sensore dal payload
            sensor_type = data.get("sensor", "unknown")

            ws_message = json.dumps({
                "sensor": sensor_type,
                "value": data.get("value"),
                "unit": data.get("unit"),
                "timestamp": data.get("timestamp")
            })

            # inoltro ai client WebSocket
            dead_clients = []
            for c in clients:
                try:
                    await c.write_message(ws_message)
                except Exception:
                    dead_clients.append(c)

            for dc in dead_clients:
                clients.discard(dc)


async def main():
    logging.basicConfig(level=logging.INFO)

    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/sensor/(.+)", SensorHandler),
            (r"/ws", WSHandler),
        ],
        template_path="templates",
    )

    app.listen(8888)
    print("Server Tornado avviato su http://localhost:8888")

    asyncio.create_task(mqtt_listener())
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
