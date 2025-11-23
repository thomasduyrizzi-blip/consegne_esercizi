




import socket
import time
import threading
import json
import paho.mqtt.client as mqtt
from collections import deque
from datetime import datetime
from multiping import multi_ping


{
"hosts_1": {"name": "server1", "address": "8.8.8.8","ports": [22, 80, 443]},








"hosts_2": {"name": "router", "address": "192.168.1.1", "ports": [22]}


}


class Host:
  def __init__(self, nome, address, controllo_porte, nome_file=None):
      self.nome = nome
      self.address = address
      self.controllo_porte = controllo_porte
      self.stato = None
      self.primo = None
      self.ultimo = None
      self.porte_stato = {}
      self.valore_dizionario = None
      self.nome_file = nome_file




  def legge(self):
      diz = {}
      lista = []
      i = 0
      with open(self.nome_file, 'r') as file:
          dati = json.load(file)
          for x in dati:
              i = i + 1
              for c in dati[x]:
                  elemento = dati[x][c]
                  lista.append(elemento)
                  if len(lista) == 3:
                      diz[str(i)] = lista
                      lista = []
      return diz




  def __repr__(self):
      return f"Host(nome={self.nome}, address={self.address}, controllo_porte={self.controllo_porte})"




  def creo_host(self, nome, address, controllo_porte):
      host = Host(nome, address, controllo_porte, nome_file=None)
      return host




  def scan_ports_sequential(self, target_ip, ports):
      risultati = {}
      for port in ports:
          try:
              with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                  s.settimeout(0.25)
                  res = s.connect_ex((target_ip, port))
                  if res == 0:
                      risultati[port] = "aperta"
                  else:
                      risultati[port] = "chiusa"
          except Exception:
              risultati[port] = "errore"
      return risultati




  def tempo(self):
      client = mqtt.Client()
      try:
          client.connect("localhost", 1883, 60)
          client.loop_start()
      except Exception as e:
          print("impossibile connettersi", e)




      while True:
          q = deque()
          i = -1
          n, a, t = "", "", ""
          valore = self.legge()




          for e in valore:
              for x in valore[e]:
                  i = i + 1
                  if i == 0:
                      n = x
                  elif i == 1:
                      a = x
                  else:
                      t = x
                      creazione = self.creo_host(n, a, t)
                      q.append(creazione)
                      i = -1




          if not q:
              time.sleep(120)
              continue




          for h in q:
              indirizzo = []
              indirizzo.append(h.address)
          try:
              responses, no_responses = multi_ping(indirizzo, timeout=2, retry=2)
          except Exception as e:
              print("errore multi_ping:", e)
              responses = {}
              no_responses = indirizzo.copy()




          for host in q:
              addr = host.address
              if addr in responses:
                  host.stato = "raggiungibile"
                  host.ultimo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                  host.valore_dizionario = responses[addr]
              else:
                  host.stato = "non raggiungibile"
                  host.ultimo = None
                  host.valore_dizionario = None








              if host.stato == "raggiungibile":
                  host.porte_stato = self.scan_ports_sequential(host.address, host.controllo_porte)
              else:
                  host.porte_stato = {}
                  for port in host.controllo_porte:
                      host.porte_stato[port] = "non raggiungibile"




              print(f"{host.nome} ({host.address}), stato: {host.stato}, last_delay: {host.valore_dizionario}, porte: {host.porte_stato}")




              topic = f"nome_studente: {host.nome}"
              payload = {
                  "nome": host.nome,
                  "address": host.address,
                  "stato": host.stato,
                  "porte": host.porte_stato,
                  "ultimo": host.ultimo,
                  "last_delay": host.valore_dizionario
              }
              try:
                  client.publish(topic, json.dumps(payload))
              except Exception:
                  None




          time.sleep(120)








if __name__ == "__main__":
  nome_file = "dati.json"
  host = Host(nome="Host1", address="192.168.1.1", controllo_porte=[22, 80, 443], nome_file=nome_file)
  thread = threading.Thread(target=host.tempo)
  thread.daemon = True
  thread.start()
  while True:
      time.sleep(1)
