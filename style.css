# File server.py
# Il server Flask che riceve i dati inviati dai sensori (tramite il client.py)
# e li conserva in memoria, mettendoli a disposizione del front-end
# (index.html file dedicato alla pagina di login, graph.html per la pagina dedicata ai grafici e alla mappa)


from flask import Flask, request, redirect, url_for         # Flask = framework web
                                                            # request = dati della richiesta in arrivo
                                                            # redirect/url_for = permette di reindirizzare il browser ad altre pagine
import json   # permette di trasformare dati Python in stringhe JSON (e viceversa), da mandare/ricevere via HTTP

# Crea l'applicazione Flask. "__name__" dice a Flask in quale file/modulo
# si trova questo script, così può individuare correttamente le cartelle (come "static", dove sono presenti le pagine HTML).
app = Flask(__name__)

# Viene definito un dizionario Python tenuto in memoria. Esso verrà svuotato ogni volta che
# il server viene riavviato. Le chiavi sono i nomi dei sensori
# (es. "01_occ"), i valori sono liste di tuple contenenti le varie informazioni (timestamp, misure)
db = {}


@app.route('/', methods=['GET'])
def main():
    # Quando qualcuno visita la pagina principale del sito (indirizzo "/")
    # con una richiesta GET, viene automaticamente
    # reindirizzato alla pagina di login (index.html), impedendo che si possa raggiungere 
    # la pagina dei grafici senza prima passare dal login.
    # "url_for('static', filename='index.html')" costruisce l'URL corretto
    # per raggiungere il file index.html dentro la cartella "static"
    return redirect(url_for('static', filename='index.html'))


@app.route('/login', methods=['POST'])
def login():
    # Questa funzione viene chiamata quando il form di login in index.html
    # viene inviato (metodo POST). Non viene fatto nessun controllo reale
    # di username/password, quindi qualunque dato inserito porta comunque
    # l'utente alla pagina dei grafici (graph.html)
    return redirect(url_for('static', filename='graph.html'))


@app.route('/graph', methods=['GET'])
def graph():
    # Questa funzione permette di far in modo che se qualcuno visita direttamente l'indirizzo "/graph"
    # (senza passare, quindi, effettuare il login), egli viene comunque mandato alla pagina dei grafici,
    # evitando così ogni possibile errore
    return redirect(url_for('static', filename='graph.html'))


@app.route('/sensors', methods=['GET'])
def sensors():
    # Restituisce l'elenco di tutti i nomi dei sensori che hanno inviato
    # almeno un dato 
    # "db.keys()" prende le chiavi del dizionario (quindi i nomi dei sensori)
    # "list(...)" le trasforma in una lista
    # "json.dumps(...)" converte questa lista in una stringa JSON, ossia l'unico
    # formato che si può restituire come testo in una risposta HTTP.
    # Il "200" è il codice di stato HTTP che significa "richiesta riuscita".
    return json.dumps(list(db.keys())), 200


@app.route('/sensors/<s>', methods=['POST'])
def add_data(s):
    # Questa funzione viene chiamata quando client.py invia un nuovo dato
    # per il sensore "s". "<s>" significa che quella parte dell'URL viene presa e passata come parametro
    # alla funzione con lo stesso nome (s).

    # "request.values['data']" prende il campo "data" inviato dal client
    # nel corpo della richiesta POST: ossia il timestamp della misurazione, come stringa.
    data = request.values['data']

    # "request.values['val']" prende il campo "val" inviato dal client: è una
    # stringa in formato JSON che rappresenta un dizionario di misure (es. '{"ki": "1", "o1_1": "0"}'). 
    # "json.loads(...)" la converte nuovamente in un vero dizionario Python, pronto per essere salvato
    val = json.loads(request.values['val'])

    # Se il sensore "s" esiste già come chiave nel nostro "database" (dizionario),
    # aggiunge una nuova tupla (timestamp, valori) alla lista già esistente
    if s in db:
        db[s].append((data, val))
    else:
        # Altrimenti (quando è la prima volta che questo sensore invia un dato),
        # crea una nuova lista con questa prima tupla dentro, a questo punto tutte le 
        # prossime misurazioni di questo sensore verranno aggiunte a questa lista
        db[s] = [(data, val)]

    # Risponde al client (client.py) confermando che il dato è stato ricevuto
    # e salvato correttamente ("200" = richiesta riuscita)
    return 'ok', 200


@app.route('/sensors/<s>', methods=['GET'])
def get_data(s):
    # Questa funzione viene chiamata dal front-end (dashboard.js) quando
    # vuole leggere tutti i dati storici di un sensore specifico "s"
    # (es. quindi quando si vuole disegnare il grafico o aggiornare la tabella).

    # Controlla se questo sensore esiste (quindi se ha già inviato almeno un dato)
    if s in db:
        # Costruisce una lista di righe da restituire al front-end.
        r = []

        # Scorre tutte le misurazioni salvate per questo sensore, una per una,
        # usando l'indice "i" (0, 1, 2, ...) per numerarle in ordine di arrivo.
        for i in range(len(db[s])):
            # Per ogni misurazione, aggiunge alla lista "r" una nuova riga con:
            #   - "i": la posizione progressiva della misura (0 = la prima ricevuta)
            #   - "db[s][i][0]": il timestamp di quella misura
            #   - "db[s][i][1]": il dizionario con i valori di quella misura
            r.append([i, db[s][i][0], db[s][i][1]])

        # Converte la lista "r" in una stringa JSON e la restituisce al
        # front-end, con codice di stato 200 (che demarca il successo)
        return json.dumps(r), 200
    else:
        # Se, invece, il sensore richiesto non esiste ancora nel database (nessun dato
        # ricevuto finora con questo nome), risponde con un messaggio di errore
        # e codice di stato HTTP 404 (risorsa non trovata).
        return 'sensor not found', 404


# Questo blocco viene eseguito solo se il file viene lanciato direttamente
# (es. con "python server.py" dal terminale), non se viene importato come
# modulo da un altro script
if __name__ == '__main__':
    # Avvia il server Flask
    # "host='0.0.0.0'" fa sì che il server accetti connessioni da qualunque
    # indirizzo di rete (non solo da "localhost")
    # "port=80" è la porta standard HTTP su cui il server rimane in ascolto.
    # "debug=True" attiva la modalità di sviluppo, che fa in modo che il server si riavvii
    # automaticamente quando viene modificato il codice, e mostra errori dettagliati
    # nel browser in caso di problemi 
    app.run(host='0.0.0.0', port=80, debug=True)
