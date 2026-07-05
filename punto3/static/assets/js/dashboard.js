/*
   File dashboard.js
   Contiene tutta la logica JavaScript della pagina graph.html:
   orologio, grafico, tabella sensori, piantina occupazione,
   marker cliccabili e refresh automatico.
 */

// Orologio in tempo reale nel topbar, esso permette di rendere più realistico l'invio di dati dai sensori

function updateClock() {
    // Cerca nella pagina l'elemento con id="clock" (il quale è nel topbar di graph.html)
    var el = document.getElementById('clock');
    // Viene effettuato un controllo di sicurezza: se per qualche motivo l'elemento non esiste,
    // "el" sarebbe null e chiamare .textContent su null darebbe errore.
    if (el) el.textContent = new Date().toLocaleString('it-IT');
    // "new Date()" crea un oggetto con la data e ora attuali del dispositivo.
    // ".toLocaleString('it-IT')" lo converte in una stringa leggibile nel
    // formato italiano (gg/mm/aaaa hh:mm:ss), che viene poi mostrata nella topbar
}

// Esegue la funzione "updateClock" ogni 1000 millisecondi (ossia 1 secondo),
// così l'orologio nel topbar avanza in tempo reale.
setInterval(updateClock, 1000);
// Chiamata immediata: senza questa riga, l'orologio resterebbe vuoto per
// il primo secondo, in attesa del primo scatto di setInterval
updateClock();


// Configurazione sensori 

// Elenco statico dei tuoi 11 sensori, con il nome tecnico usato nelle rotte
// del server (es. "01_occ", deve corrispondere esattamente al nome del file
// CSV senza estensione) e un'etichetta leggibile da mostrare nell'interfaccia.
var SENSORS = [
    { name: '01_occ',        label: 'Occupancy' },
    { name: '02_win',        label: 'Windows' },
    { name: '03_light',      label: 'Light (Luce)' },
    { name: '04_plug',       label: 'Plug Loads [W]' },
    { name: '05_temp_in',    label: 'Temp. Interna [C]' },
    { name: '06_rhu_in',     label: 'Umidità Interna [%]' },
    { name: '07_rad_global', label: 'Radiazione Globale [W/m2]' },
    { name: '08_temp_out',   label: 'Temp. Esterna [C]' },
    { name: '09_rhu_out',    label: 'Umidità Esterna [%]' },
    { name: '10_wsp',        label: 'Velocità Vento [m/s]' },
    { name: '11_wdi',        label: 'Direzione Vento [°]' },
];


// Popola il select del sensore
function populateSensorSelect() {
    // Prende il menu a tendina <select id="sensor-select"> di graph.html,
    // che nell'HTML è vuoto: le opzioni vengono aggiunte qui dinamicamente.
    var sel = document.getElementById('sensor-select');
    if (!sel) return;   // se l'elemento non esiste, esce subito senza fare nulla

    // Scorre l'array SENSORS e, per ciascun sensore, crea una nuova opzione
    // del menu a tendina.
    SENSORS.forEach(function(s) {
        var opt = document.createElement('option');   // crea un elemento <option> vuoto
        opt.value = s.name;          // valore "tecnico" dell'opzione (es. "01_occ"),
                                      // sarà questo il valore letto quando l'utente sceglie
        opt.textContent = s.label;   // testo visibile all'utente nel menu (es. "Occupancy")
        sel.appendChild(opt);        // inserisce l'opzione appena creata dentro il <select>
    });
}


// Carica e disegna il grafico del sensore selezionato

function loadChart() {
    // Legge il valore attualmente selezionato nel menu a tendina dei sensori
    // (es. "01_occ") e in quello del numero di righe da mostrare (es. "100")
    // così da mostrare il grafico del sensore e il numero di misurazioni desiderato dall'utente
    var sensorName = document.getElementById('sensor-select').value;
    var limit      = parseInt(document.getElementById('rows-select').value);
    // "parseInt" converte la stringa "100" restituita dal menu in un vero numero intero 100
    var container  = document.getElementById('chart-container');

    if (!sensorName) {
        // Se nessun sensore è selezionato (es. subito dopo il caricamento
        // della pagina prima che populateSensorSelect() abbia finito), mostra un
        // messaggio invece di provare a caricare dati inesistenti.
        container.innerHTML = '<p class="empty-state">Seleziona un sensore.</p>';
        return;
    }

    // Messaggio temporaneo mostrato mentre si aspetta la risposta del server
    container.innerHTML = '<p class="empty-state">Caricamento…</p>';

    // Richiesta AJAX (asincrona) al server, verso la rotta GET /sensors/<nome>.
    // "$.getJSON" è una funzione di jQuery che fa una richiesta GET e si aspetta
    // una risposta in formato JSON, che poi passa già "pronta" (come array/oggetto
    // JavaScript, non come testo grezzo) alla funzione di callback
    $.getJSON('/sensors/' + sensorName, function(data) {
        // "data" è la lista di tutte le misurazioni ricevute finora per questo sensore,
        // ciascuna nel formato [indice, timestamp, dizionario_valori]

        if (!data || data.length === 0) {
            // Se il sensore non ha ancora nessun dato (es. il client non ha ancora
            // inviato nulla per questo sensore), avvisa l'utente invece di disegnare
            // un grafico vuoto o generare un errore.
            container.innerHTML = '<p class="empty-state">Nessun dato disponibile per questo sensore.</p>';
            return;
        }

        // "slice(-limit)" prende solo le ULTIME "limit" righe dell'array (es. le ultime
        // 100), per non sovraccaricare il grafico se il sensore ha già migliaia di misure
        var slice = data.slice(-limit);

        // Prende i nomi delle colonne (es. "tempOut [C]") dal dizionario di valori
        // della prima riga selezionata: si assume che tutte le righe di questo
        // sensore abbiano sempre le stesse colonne.
        var columns = Object.keys(slice[0][2]);
        // Costruisce l'intestazione della tabella dati richiesta da Google Charts:
        // prima colonna "Timestamp", poi una colonna per ciascuna misura del sensore.
        var header  = ['Timestamp'].concat(columns);
        var chartRows = [header];   // la prima riga della tabella dati deve essere l'intestazione

        // Per ciascuna misurazione nello "slice", costruisce una riga della tabella:
        slice.forEach(function(entry) {
            // "entry" è [indice, timestamp, dizionario_valori]; "entry[1]" è il timestamp
            var row = [entry[1]];
            // Per ciascuna colonna, aggiunge il valore numerico corrispondente
            columns.forEach(function(col) {
                // "entry[2][col]" prende il valore di quella colonna dal dizionario
                // "parseFloat(...)" lo converte da stringa a numero decimale
                // "|| 0" è una rete di sicurezza: se parseFloat restituisse NaN
                // (es. valore mancante o non numerico), viene usato 0 al suo posto,
                // evitando che il grafico si rompa per un dato malformato.
                row.push(parseFloat(entry[2][col]) || 0);
            });
            chartRows.push(row);
        });

        // Svuota il messaggio "Caricamento…" e prepara il contenitore per il grafico vero.
        container.innerHTML = '';
        container.style.minHeight = '320px';

        // Aspetta che la libreria Google Charts sia pronta (caricata in modo
        // asincrono all'avvio della pagina) prima di disegnare.
        google.charts.setOnLoadCallback(function() {
            // Converte l'array "chartRows" nel formato a "tabella dati" richiesto
            // internamente da Google Charts.
            var dataTable = google.visualization.arrayToDataTable(chartRows);

            // Cerca nell'array SENSORS l'oggetto corrispondente al sensore corrente,
            // per usarne l'etichetta leggibile come titolo del grafico.
            var sensor = SENSORS.find(function(s) { return s.name === sensorName; });

            // Oggetto di configurazione grafica del grafico (titolo, font, colori, ecc.)
            var options = {
                title: sensor ? sensor.label : sensorName,   // se non trovato, usa il nome tecnico
                titleTextStyle: { fontName: 'DM Sans', fontSize: 14, bold: true, color: '#1e293b' },
                hAxis: { title: 'Timestamp', textStyle: { fontName: 'DM Sans', fontSize: 11 } },
                vAxis: { minValue: 0,         textStyle: { fontName: 'DM Sans', fontSize: 11 } },
                legend: { position: 'bottom',  textStyle: { fontName: 'DM Sans', fontSize: 12 } },
                chartArea: { left: 60, right: 20, top: 40, bottom: 80, width: '100%', height: '100%' },
                colors: ['#3b82f6','#22c55e','#f59e0b','#ef4444','#8b5cf6','#06b6d4'],
                backgroundColor: 'transparent',
                areaOpacity: 0.15,
            };

            // Crea un grafico ad area ("AreaChart") dentro il div "chart-container"
            // e lo disegna usando i dati e le opzioni preparati sopra
            var chart = new google.visualization.AreaChart(container);
            chart.draw(dataTable, options);
        });

    }).fail(function() {
        // ".fail(...)" viene eseguita se la richiesta $.getJSON fallisce del tutto
        // (es. server spento, errore di rete), non se il sensore è semplicemente vuoto.
        container.innerHTML = '<p class="empty-state">Errore nel caricamento dei dati.</p>';
    });
}


// Aggiorna la tabella dei sensori attivi

function loadSensorTable() {
    // Chiede al server l'elenco di tutti i nomi dei sensori che hanno inviato
    // almeno un dato finora (rotta GET /sensors di server.py)
    $.getJSON('/sensors', function(list) {
        // Mostra nel riquadro statistiche in alto quanti sensori sono attivi
        document.getElementById('sensor-count').textContent = list.length;

        var tbody = document.getElementById('sensor-tbody');
        tbody.innerHTML = '';   // svuota la tabella (rimuove il messaggio "Caricamento…"
                                 // o le righe della volta precedente, prima di ricostruirla)

        if (list.length === 0) {
            // Nessun sensore attivo: mostra una riga unica di avviso invece di
            // lasciare la tabella completamente vuota.
            tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:#64748b;">Nessun sensore attivo</td></tr>';
            return;
        }

        // Per ciascun nome di sensore nell'elenco, fa una richiesta separata
        // per ottenere i suoi dati e costruire la riga di tabella corrispondente.
        list.forEach(function(sName) {
            $.getJSON('/sensors/' + sName, function(data) {
                // Cerca l'etichetta leggibile in SENSORS; se non trovata, usa il
                // nome tecnico come ripiego (" || {} " evita un errore se .find
                // non trova nulla e restituisce undefined).
                var label = (SENSORS.find(function(s) { return s.name === sName; }) || {}).label || sName;

                // Prende l'ultima misurazione ricevuta per questo sensore, se esiste.
                var last = data && data.length ? data[data.length - 1] : null;

                // "last[1]" è il timestamp dell'ultima misura, "—" se non c'è nessun dato.
                var ts = last ? last[1] : '—';

                // "last[2]" è il dizionario dei valori; "Object.values(...)" ne prende
                // solo i valori (scartando i nomi delle colonne); ".slice(0,2)" tiene
                // solo i primi due valori (per non riempire troppo la tabella se un
                // sensore ha molte colonne); ".join(', ')" li unisce in una stringa
                // leggibile separata da virgole.
                var vals = last ? Object.values(last[2]).slice(0,2).join(', ') : '—';

                // Costruisce dinamicamente una nuova riga <tr> con le tre celle
                // (etichetta, ultimo valore, timestamp) e la aggiunge alla tabella.
                var tr = document.createElement('tr');
                tr.innerHTML =
                    '<td>' + label + '</td>' +
                    '<td>' + vals  + '</td>' +
                    '<td>' + ts    + '</td>';
                tbody.appendChild(tr);
            });
        });
    });
}


// Mappa della smart home (SVG colorata per occupazione)

function loadFloorplan() {
    // Mappa: id del rettangolo SVG nella piantina 
    //  - "room_o1" ha 5 sotto-sensori (o1_1...o1_5), perché nella piantina
    //   esiste un solo rettangolo per l'intera zona O1.
    //  - "room_mr" non ha nessuna colonna corrispondente nel CSV: resterà
    //   sempre colorata "nessun dato" (azzurrino), il che è corretto, dato
    //   che il dataset non include un sensore di occupazione per quella stanza.
    var roomColumns = {
        'room_ki': ['ki'],
        'room_o1': ['o1_1', 'o1_2', 'o1_3', 'o1_4', 'o1_5'],
        'room_o2': ['o2'],
        'room_o3': ['o3'],
        'room_o4': ['o4'],
    };

    // Interroga il server per i dati del sensore di occupazione.
    $.getJSON('/sensors/01_occ', function(data) {
        if (!data || data.length === 0) return;   // nessun dato ancora ricevuto: esce senza colorare nulla

        // Prende l'ultima misurazione ricevuta (l'unica che ci interessa per
        // sapere lo stato attuale di occupazione, non lo storico)
        var lastEntry = data[data.length - 1];
        var values = lastEntry[2];   // dizionario {intestazione_colonna_completa: valore_stringa}

        // Le chiavi di "values" sono le intestazioni COMPLETE del CSV,
        // es. "o1_3 [0:vacant 1:occupied]". Costruisce un secondo dizionario
        // con chiavi "brevi" (solo la prima parola prima dello spazio,
        // es. "o1_3"), così il confronto con roomColumns non dipende dal
        // testo esatto scritto tra parentesi quadre nell'intestazione originale.
        var shortValues = {};
        Object.keys(values).forEach(function(fullKey) {
            var shortKey = fullKey.trim().split(' ')[0];
            // ".trim()" rimuove eventuali spazi bianchi accidentali a inizio/fine stringa;
            // ".split(' ')[0]" spezza la stringa in base agli spazi e prende solo il
            // primo pezzo (il nome breve della colonna, prima della parentesi quadra).
            shortValues[shortKey] = values[fullKey];
        });

        // Per ciascuna stanza definita in roomColumns, calcola il colore corretto.
        Object.keys(roomColumns).forEach(function(roomId) {
            var columns = roomColumns[roomId];

            // Per ogni colonna di questa stanza:
            //      1) prende il valore corrispondente da "shortValues" (map)
            //      2) scarta quelle non presenti nei dati, cioè "undefined" (filter)
            //      3) converte le stringhe rimanenti in numeri decimali (map)
            var nums = columns
                .map(function(col) { return shortValues[col]; })
                .filter(function(v) { return v !== undefined; })
                .map(function(v) { return parseFloat(v); });

            var color = '#b3d4f0';   // colore di default: azzurrino, "nessun dato disponibile"

            if (nums.length > 0) {
                // "some(...)" restituisce true se almeno uno dei valori soddisfa
                // la condizione (diverso da zero). Se anche un solo sotto-sensore
                // della stanza segna occupazione, l'intera stanza viene colorata di rosso;
                // diventa verde solo se tutti i suoi sotto-sensori sono esattamente zero.
                var anyOccupied = nums.some(function(v) { return v !== 0; });
                color = anyOccupied ? '#fca5a5' : '#86efac';   // rosso : verde
            }

            // Cerca l'elemento SVG con questo id e, se esiste, gli imposta il
            // nuovo colore di riempimento (l'attributo "fill" degli elementi SVG).
            var el = document.getElementById(roomId);
            if (el) el.setAttribute('fill', color);
        });
    });
}


// Piantina sensori: click su marker apre il grafico del sensore

function initSensorMarkers() {
    // Seleziona tutti gli elementi della pagina con classe "sensor-marker"
    // (i gruppi <g> disegnati nella seconda piantina di graph.html) e, per
    // ciascuno, collega tre comportamenti interattivi diversi.
    document.querySelectorAll('.sensor-marker').forEach(function(marker) {

        // Comportamento 1: click sul marker
        marker.addEventListener('click', function() {
            // "this" dentro questa funzione si riferisce al marker specifico
            // su cui è avvenuto il click (ognuno ha i propri attributi data-*)
            var sensorName = this.getAttribute('data-sensor');

            // Imposta il menu a tendina dei sensori sul sensore corrispondente
            // al marker cliccato, poi richiama loadChart() per aggiornare subito
            // il grafico con questo nuovo sensore selezionato.
            var select = document.getElementById('sensor-select');
            select.value = sensorName;
            loadChart();

            // Fa scorrere automaticamente la pagina fino al grafico, in modo
            // fluido ("smooth"), così l'utente vede subito il risultato del click
            // anche se il grafico si trova più in alto nella pagina.
            document.getElementById('chart-container').scrollIntoView({ behavior: 'smooth' });
        });

        // Comportamento 2: il mouse passa sopra il marker (hover).
        marker.addEventListener('mouseenter', function() {
            // Ingrandisce leggermente il cerchio (da raggio 8 a 10) per dare un
            // feedback visivo che il marker è "attivo" sotto il puntatore.
            var circle = this.querySelector('circle');
            circle.setAttribute('r', '10');

            // Mostra il tooltip (il riquadro nero definito in graph.html), riempendolo
            // con l'etichetta leggibile del sensore (es. "Temp. Interna (O1)").
            var label = this.getAttribute('data-label');
            var tooltip = document.getElementById('sensor-tooltip');
            tooltip.textContent = label;
            tooltip.style.display = 'block';
        });

        // Comportamento 3: il mouse si sposta dal marker.
        marker.addEventListener('mouseleave', function() {
            // Riporta il cerchio alla dimensione originale (raggio 8) e nasconde
            // di nuovo il tooltip, annullando gli effetti del "mouseenter".
            this.querySelector('circle').setAttribute('r', '8');
            document.getElementById('sensor-tooltip').style.display = 'none';
        });
    });
}


// Aggiorna timestamp 

function updateLastUpdate() {
    // Riempie la statistica "Ultimo aggiornamento" in alto con la data/ora
    // corrente del dispositivo, ogni volta che i dati vengono ricaricati
    // (non è il timestamp dell'ultima misura del sensore, ma il momento
    // in cui questa pagina ha effettivamente aggiornato le informazioni).
    var el = document.getElementById('last-update');
    if (el) el.textContent = new Date().toLocaleString('it-IT');
}


// Init: tutto ciò che deve accadere quando la pagina è pronta

// "$(document).ready(...)" è la sintassi jQuery che esegue la funzione al
// suo interno solo DOPO che l'intero documento HTML è stato caricato e
// interpretato dal browser (evita di cercare elementi che non esistono ancora)
$(document).ready(function() {
    // Avvia il caricamento della libreria Google Charts, specificando che
    // ci serve il pacchetto "corechart" (contiene AreaChart e altri grafici base)
    // Questo caricamento è asincrono: per questo, più sopra in loadChart(),
    // il disegno vero e proprio avviene dentro "google.charts.setOnLoadCallback".
    google.charts.load('current', { packages: ['corechart'] });

    // Sequenza di inizializzazione, eseguita una sola volta al caricamento della pagina:
    populateSensorSelect();   // riempie il menu a tendina dei sensori
    loadChart();              // disegna il primo grafico (sensore di default)
    loadSensorTable();        // popola la tabella di stato sensori
    loadFloorplan();          // colora la piantina in base all'occupazione
    updateLastUpdate();       // scrive l'orario del primo caricamento
    initSensorMarkers();      // rende cliccabili/interattivi i marker sulla piantina 2

    // Collega il bottone "Aggiorna Grafico" alla funzione loadChart, così un
    // click manuale forza subito un ricaricamento (senza aspettare)
    document.getElementById('btn-refresh').addEventListener('click', loadChart);

    // Quando l'utente cambia sensore dal menu a tendina, ricarica subito il
    // grafico con il nuovo sensore selezionato ("change" scatta ogni volta
    // che il valore del <select> viene modificato dall'utente).
    document.getElementById('sensor-select').addEventListener('change', loadChart);

    // Auto-refresh: ogni 5000 millisecondi (5 secondi), ripete l'aggiornamento
    // di grafico, tabella, piantina e orario "ultimo aggiornamento" — questo è
    // ciò che rende la dashboard "viva" senza bisogno di ricaricare la pagina.
    setInterval(function() {
        loadChart();
        loadSensorTable();
        loadFloorplan();
        updateLastUpdate();
    }, 5000);
});
