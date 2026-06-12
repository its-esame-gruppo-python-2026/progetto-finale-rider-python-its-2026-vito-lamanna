from flask import Blueprint, request, jsonify, render_template
from werkzeug.exceptions import BadRequest  #per riconoscere errori legati alle richieste HTTP (come BadRequest)
from src.handlers.riders_handlers import inserisci_rider_handlers, list_rider_handlers, inserisci_recensione_handlers, aggiorna_recensione_handlers, delete_rider_handlers

riders_bp = Blueprint("riders", __name__, url_prefix="/riders")

@riders_bp.route('/insert_rider', methods=['POST'])
def insert_rider():
    try:
        dati_inseriti = request.get_json()
        risposta_json, codice_http = inserisci_rider_handlers(dati_inseriti)
        return jsonify(risposta_json), codice_http
    except BadRequest as e:
        return jsonify({
            "Errore":"Il formato del JSON inviato non è valido. Controlla la sintassi (virgole, virgolette, graffe, valori variabili).", 
            "Dettaglio tecnico": str(e)
            }),400
    except Exception as e:
        return jsonify({"Errore Server": str(e)}), 500

#query parameters
@riders_bp.route('/list_rider', methods=['GET'])
def list_rider():
    try:
        url_originale = request.environ.get('RAW_URI', request.url)
        if url_originale.endswith('?'):
            return jsonify({
                "Errore sintassi URL": 
                "Hai inserito il punto interrogativo senza specificare alcun filtro. Rimuovi il '?' o usa '?vehicle=nome_veicolo'."
            }), 400
        stringa_grezza = request.query_string.decode('utf-8')
        if stringa_grezza:
            if stringa_grezza.startswith('=') or 'vehicle=' not in stringa_grezza:
                return jsonify({
                    "Errore sintassi URL": 
                    "Hai formattato male i filtri. Usa il comando completo '?vehicle=nome_veicolo'"
                }), 400
        parametro_url = request.args
        risposta_json, codice_http = list_rider_handlers(parametro_url)
        return jsonify(risposta_json), codice_http
    except Exception as e:
        return jsonify({"Errore Server": str(e)}), 500
    
@riders_bp.route('/insert_review', methods=['POST'])
def insert_review():
    try:
        dati_inseriti = request.get_json()
        risposta_json, codice_http = inserisci_recensione_handlers(dati_inseriti)
        return jsonify(risposta_json), codice_http
    except BadRequest as e:
        return jsonify({
            "Errore":"Il formato del JSON inviato non è valido. Controlla la sintassi (virgole, virgolette, graffe, valori variabili).", 
            "Dettaglio tecnico": str(e)
            }),400
    except ValueError as e:
        return jsonify({"Errore": str(e)}), 400
    except Exception as e:
        return jsonify({"Errore Server": str(e)}), 500

@riders_bp.route('/update_review', methods=['POST'])
def update_review():
    try:
        dati_inseriti = request.get_json()
        risposta_json, codice_http = aggiorna_recensione_handlers(dati_inseriti)
        return jsonify(risposta_json), codice_http
    except BadRequest as e:
        return jsonify({
            "Errore":"Il formato del JSON inviato non è valido. Controlla la sintassi (virgole, virgolette, graffe, valori variabili).", 
            "Dettaglio tecnico": str(e)
            }),400
    except ValueError as e:
        return jsonify({"Errore": str(e)}), 400
    except Exception as e:
        return jsonify({"Errore Server": str(e)}), 500

#path parameters
@riders_bp.route('/delete_rider/<int:rider_id>', methods=['DELETE'])
def delete_rider(rider_id):
    try:
        risposta_json, codice_http = delete_rider_handlers(rider_id)
        return jsonify(risposta_json), codice_http
    except Exception as e:
        return jsonify({"Errore Server": str(e)}), 500