# Applicazione Web per la visualizzazione di sensori realtime

## Obiettivo

Realizzare un' **applicazione web** che permetta di **visualizzare in tempo reale i dati provenienti da più sensori**, utilizzando:

- MQTT per la distribuzione dei dati
- WebSocket per l’invio dei dati al browser
- Chart.js per la visualizzazione grafica

---

## Contesto applicativo

I dati dei sensori vengono pubblicati su un broker MQTT secondo la seguente struttura di topic:
```
sensor/
├── temperature
├── humidity
└── <sensore a scelta>
```

Ogni sensore pubblica periodicamente dati simulati.

---

## Parte backend (da completare)

Viene fornita una **versione iniziale del backend** che gestisce un solo sensore (`sensor/temperature`).

Si richiede di:

1. Estendere il backend per gestire più sensori (`temperature`, `humidity` e un sensore a scelta)
2. Iscriversi ai rispettivi topic MQTT
3. Inviare i dati al client WebSocket in formato JSON, includendo:
   - tipo di sensore
   - valore
   - unità di misura
   - timestamp

---

## Parte frontend

### 1. Pagina iniziale – Selezione sensore

Realizzare una pagina HTML iniziale che consenta di:

- selezionare un sensore tramite un menu a tendina (`<select>`)
- reindirizzare l’utente alla pagina dedicata al sensore scelto

---

### 2. Pagine dedicate ai sensori

Per ogni sensore deve essere presente una **pagina HTML dedicata**.

Ogni pagina deve visualizzare:

1. **Dati grezzi** (JSON ricevuto via WebSocket)
2. **Dati formattati** (valore, unità, orario)
3. **Dashboard grafica** con Chart.js

Ogni pagina deve:
- aprire una connessione WebSocket
- ricevere i dati dal server
- visualizzare solo i dati del sensore corrispondente

---

## Chart.js

### Cos’è Chart.js

Chart.js è una libreria JavaScript che consente di disegnare grafici utilizzando l’elemento HTML `<canvas>`.  
Il grafico è un **oggetto JavaScript** che contiene dati e opzioni di visualizzazione.

Documentazione ufficiale:  
https://www.chartjs.org/docs/latest/

---

### 1. Inclusione della libreria

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```
Questa riga rende disponibile l’oggetto globale Chart.

2. Canvas HTML
```
<canvas id="chart"></canvas>
```

Il grafico verrà disegnato all’interno di questo elemento.

3. Creazione del grafico (struttura generale)
```
const ctx = document.getElementById("chart");

const chart = new Chart(ctx, {
    type: "line",        // tipo di grafico (line = grafico a linee)
    data: {
        labels: [],      // asse orizzontale (tempo, indice, ecc.)
        datasets: [{
            label: "Valore sensore", // nome della linea nel grafico
            data: [],                // valori numerici del sensore
            borderWidth: 2
        }]
    },
    options: {
        animation: false
    }
});
```
4. Significato degli elementi principali

```type```
Specifica il tipo di grafico. In questo esercizio si utilizza line.

```labels```
È un array che rappresenta l’asse orizzontale del grafico
(es. orario di acquisizione dei dati).

```datasets```
Contiene uno o più insiemi di dati da visualizzare.
In questo esercizio è sufficiente un solo dataset.

```data```
È l’array dei valori numerici che verranno disegnati nel grafico.

5. Aggiornamento del grafico in tempo reale

Quando arriva un nuovo dato dal WebSocket:
```html
chart.data.labels.push(orario);
chart.data.datasets[0].data.push(valore);
chart.update();
```

```push()```
Aggiunge un nuovo elemento in fondo a un array.

```labels.push(orario)```
Aggiunge un nuovo valore sull’asse orizzontale.

```data.push(valore)```
Aggiunge il nuovo valore del sensore.

```chart.update()```
Ridisegna il grafico con i nuovi dati.

6. Limitare il numero di punti (consigliato)
```
if (chart.data.labels.length > 20) {
    chart.data.labels.shift();
    chart.data.datasets[0].data.shift();
}
```

```shift()```
rimuove il primo elemento dell’array

- consente di visualizzare solo gli ultimi N valori

- evita grafici troppo affollati