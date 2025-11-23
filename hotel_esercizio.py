import json
from bson import ObjectId
import tornado.ioloop
import tornado.web
import motor.motor_tornado




def id_obj(id_stringa):

    return ObjectId(id_stringa)


def converti_json(documento):

    documento["id"] = str(documento["_id"])
    del documento["_id"]
    return documento


class HotelHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.settings["db"]

    # --- GET HOTEL ---
    async def get(self, id_hotel=None):

        # lista hotel
        if id_hotel is None:
            lista_hotel = await self.db.hotels.find().to_list(None)
            lista_hotel = [converti_json(h) for h in lista_hotel]
            return self.write({"hotels": lista_hotel})

        hotel = await self.db.hotels.find_one({"_id": id_obj(id_hotel)})
        if not hotel:
            self.set_status(404)
            return self.write({"errore": "Hotel non trovato"})

        hotel = converti_json(hotel)


        recensioni = await self.db.reviews.find({"hotel_id": id_obj(id_hotel)}).to_list(None)
        hotel["recensioni"] = [converti_json(r) for r in recensioni]

        self.write(hotel)


    async def post(self, id_hotel=None):
        dati = json.loads(self.request.body)
        risultato = await self.db.hotels.insert_one(dati)
        self.set_status(201)
        self.write({"id": str(risultato.inserted_id)})

    async def put(self, id_hotel):
        dati = json.loads(self.request.body)

        # elimina recensioni collegate
        await self.db.reviews.delete_many({"hotel_id": id_obj(id_hotel)})

        # aggiorna hotel
        await self.db.hotels.update_one({"_id": id_obj(id_hotel)}, {"$set": dati})
        self.write({"messaggio": "Hotel aggiornato"})

    async def delete(self, id_hotel):

        await self.db.hotels.delete_one({"_id": id_obj(id_hotel)})
        await self.db.reviews.delete_many({"hotel_id": id_obj(id_hotel)})

        self.write({"messaggio": "Hotel eliminato"})



class RecensioneHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.settings["db"]

    async def get(self, id_hotel, id_recensione=None):

        if id_recensione is None:
            recensioni = await self.db.reviews.find({"hotel_id": id_obj(id_hotel)}).to_list(None)
            recensioni = [converti_json(r) for r in recensioni]
            return self.write({"recensioni": recensioni})

        recensione = await self.db.reviews.find_one({"_id": id_obj(id_recensione)})
        if not recensione:
            self.set_status(404)
            return self.write({"errore": "Recensione non trovata"})

        self.write(converti_json(recensione))

    async def post(self, id_hotel, id_recensione=None):

        dati = json.loads(self.request.body)
        dati["hotel_id"] = id_obj(id_hotel)

        risultato = await self.db.reviews.insert_one(dati)
        self.set_status(201)
        self.write({"id": str(risultato.inserted_id)})

    async def put(self, id_hotel, id_recensione):
        dati = json.loads(self.request.body)
        await self.db.reviews.update_one({"_id": id_obj(id_recensione)}, {"$set": dati})
        self.write({"messaggio": "Recensione aggiornata"})

    async def delete(self, id_hotel, id_recensione):
        await self.db.reviews.delete_one({"_id": id_obj(id_recensione)})
        self.write({"messaggio": "Recensione eliminata"})



def crea_app():
    client = motor.motor_tornado.AsyncIOMotorClient("mongodb://localhost:27017")
    database = client["hotel_db"]

    return tornado.web.Application([
        (r"/hotels", HotelHandler),
        (r"/hotels/([a-fA-F0-9]{24})", HotelHandler),
        (r"/hotels/([a-fA-F0-9]{24})/recensioni", RecensioneHandler),
        (r"/hotels/([a-fA-F0-9]{24})/recensioni/([a-fA-F0-9]{24})", RecensioneHandler),
    ], db=database)


if __name__ == "__main__":
    app = crea_app()
    app.listen(8888)
    print("Server avviato su http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
