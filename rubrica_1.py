
import asyncio
import re




import tornado.web












rubrica = {
  1: {
      "id": 1,
      "nome": "Mario Rossi",
      "telefono": "3331234567",
      "email": "mario.rossi@example.com",
      "citta": "Roma"
  },
  2: {
      "id": 2,
      "nome": "Luisa Bianchi",
      "telefono": "3399876543",
      "email": "luisa.bianchi@example.com",
      "citta": "Milano"
  },
  3: {
      "id": 3,
      "nome": "Carlo Verdi",
      "telefono": "3209998888",
      "email": "carlo.verdi@example.com",
      "citta": "Napoli"
  }
}
class RubricaHandler(tornado.web.RequestHandler):
  def get(self, rubrica_id=None):
      self.set_header("Content-Type", "application/json")




      if rubrica_id  :
          oggetto = rubrica.get(int(rubrica_id))
          if oggetto:
              self.set_status(200)
              self.write(oggetto)
          else:
              self.set_status(404)
              self.write({"error": "id non trovato"})
      else:
          self.set_status(200)
          self.write({"Rubrica":  list(rubrica.values())})




  def post(self):
      self.set_header("Content-Type", "application/json")
      data = tornado.escape.json_decode(self.request.body)
      controllare = self.controllo(data)
      if controllare == True:
          new_id = str(len(rubrica) + 1)
          rubrica[new_id] = {"id": new_id, **data}
          self.set_status(201)
          self.write(rubrica[new_id])


  def controllo(self, data):
   #   self.set_header("Content-Type", "application/json")
     # data = tornado.escape.json_decode(self.request.body)
      pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
      for i in data:
          lunghezza_citta = len(data["citta"])
          lunghezza_nome = len(data["name"])
          mail = data["email"]
          telefono = data["telefono"]
          if (lunghezza_nome < 2 or lunghezza_nome == ""):
              self.set_status(400)
              self.write({"error": "lista troppo corta o oggetto vuoto"})
              return False
          if (lunghezza_citta < 3 or lunghezza_citta== ""):
              self.set_status(400)
              self.write({"error": "lista troppo corta o oggetto vuoto"})
              return False
          if (len(telefono) > 15 or len(telefono) < 6):
              self.set_status(400)
              self.write({"error": "numero telefonico troppo corto o lungo"})
              return False
          if re.match(pattern, mail):
              None
          else:
              self.set_status(400)
              self.write({"error": "formato mail non valida"})
              return False
      return True


  def delete(self, rubrica_id):
          self.set_header("Content-Type", "application/json")
          rubrica_id = int(rubrica_id)
          if rubrica_id in rubrica:
              del rubrica[rubrica_id]
              self.set_status(204)
          else:
              self.set_status(404)
              self.write({"error": "contatto in rubrica non trovato"})
  def put(self, rubrica_id):
      self.set_header("Content-Type", "application/json")
      data = tornado.escape.json_decode(self.request.body)
      controllare = self.controllo(data)
      if controllare == True:
          if rubrica_id in rubrica:
              rubrica_id = int(rubrica_id)
              self.write(rubrica[rubrica_id])




def make_app():
  return tornado.web.Application([
      (r"/rubrica", RubricaHandler),
          (r"/rubrica/([0-9]+)", RubricaHandler),
      ], debug=True)
async def main(shutdown_event):
  app = make_app()
  app.listen(8888)
  print("Server in ascolto su http://localhost:8888/rubrica")
  await shutdown_event.wait()
  print("Shutdown ricevuto, chiusura server...")




if __name__ == "__main__":
  shutdown_event = asyncio.Event()
  try:
      asyncio.run(main(shutdown_event))
  except KeyboardInterrupt:
      shutdown_event.set()  # evento completato con set 
 




