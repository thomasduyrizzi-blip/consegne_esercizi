import json
from bson import ObjectId
import tornado.ioloop
import tornado.web
import motor.motor_tornado

def oid(s):
    return ObjectId(s)

def to_json(doc):
    doc["id"] = str(doc.pop("_id"))
    return doc

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.settings["db"]

    def json_body(self):
        return json.loads(self.request.body)

class HotelHandler(BaseHandler):

    async def get(self, id_hotel=None):
        if id_hotel is None:
            hotels = await self.db.hotels.find().to_list(None)
            return self.write({"hotels": [to_json(h) for h in hotels]})
        hotel = await self.db.hotels.find_one({"_id": oid(id_hotel)})
        if not hotel:
            self.set_status(404)
            return self.write({"errore": "Hotel non trovato"})
        hotel = to_json(hotel)
        recs = await self.db.reviews.find({"hotel_id": oid(id_hotel)}).to_list(None)
        hotel["recensioni"] = [to_json(r) for r in recs]
        self.write(hotel)

    async def post(self, id_hotel=None):
        dati = self.json_body()
        result = await self.db.hotels.insert_one(dati)
        self.set_status(201)
        self.write({"id": str(result.inserted_id)})

    async def put(self, id_hotel):
        dati = self.json_body()
        await self.db.reviews.delete_many({"hotel_id": oid(id_hotel)})
        await self.db.hotels.replace_one({"_id": oid(id_hotel)}, dati)
        self.write({"messaggio": "Hotel aggiornato"})

    async def delete(self, id_hotel):
        await self.db.hotels.delete_one({"_id": oid(id_hotel)})
        await self.db.reviews.delete_many({"hotel_id": oid(id_hotel)})
        self.write({"messaggio": "Hotel eliminato"})

class RecensioneHandler(BaseHandler):

    async def get(self, id_hotel, id_recensione=None):
        if id_recensione is None:
            recs = await self.db.reviews.find({"hotel_id": oid(id_hotel)}).to_list(None)
            return self.write({"recensioni": [to_json(r) for r in recs]})
        rec = await self.db.reviews.find_one({"_id": oid(id_recensione)})
        if not rec:
            self.set_status(404)
            return self.write({"errore": "Recensione non trovata"})
        self.write(to_json(rec))

    async def post(self, id_hotel, id_recensione=None):
        dati = self.json_body()
        dati["hotel_id"] = oid(id_hotel)
        result = await self.db.reviews.insert_one(dati)
        self.set_status(201)
        self.write({"id": str(result.inserted_id)})

    async def put(self, id_hotel, id_recensione):
        dati = self.json_body()
        await self.db.reviews.replace_one({"_id": oid(id_recensione)}, dati)
        self.write({"messaggio": "Recensione aggiornata"})

    async def delete(self, id_hotel, id_recensione):
        await self.db.reviews.delete_one({"_id": oid(id_recensione)})
        self.write({"messaggio": "Recensione eliminata"})

def crea_app():
    client = motor.motor_tornado.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["hotel_db"]
    return tornado.web.Application([
        (r"/hotels", HotelHandler),
        (r"/hotels/([a-fA-F0-9]{24})", HotelHandler),
        (r"/hotels/([a-fA-F0-9]{24})/recensioni", RecensioneHandler),
        (r"/hotels/([a-fA-F0-9]{24})/recensioni/([a-fA-F0-9]{24})", RecensioneHandler),
    ], db=db)

if __name__ == "__main__":
    app = crea_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

