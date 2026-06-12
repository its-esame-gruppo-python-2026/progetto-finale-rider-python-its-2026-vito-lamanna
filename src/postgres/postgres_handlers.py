import os
import psycopg2
from flask import jsonify

def connessione_db():
    return psycopg2.connect(
        host = os.getenv("DB_HOST", "localhost"),
        port = os.getenv("DB_PORT", "5432"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        database = os.getenv("DB_NAME")
    )

def inizializza_db():
    comandi = (
        """
        CREATE TABLE IF NOT EXISTS riders(
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            vehicle VARCHAR(255) NOT NULL,
            total_deliveries INTEGER NOT NULL DEFAULT 0,
            CONSTRAINT check_rider_vehicle CHECK (LOWER(vehicle) IN ('auto', 'moto', 'scooter', 'bicicletta', 'furgone'))
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS reviews(
            id SERIAL PRIMARY KEY,
            rider_id INTEGER NOT NULL REFERENCES riders(id) ON DELETE CASCADE,
            customer_name VARCHAR(255) NOT NULL,
            rating INTEGER NOT NULL CHECK (rating>=1 AND rating<=5),
            comment TEXT
        );
        """
    )

    conn_db = None
    try:
        conn_db = connessione_db()
        cursore = conn_db.cursor()

        for comando in comandi:
            cursore.execute(comando)

        conn_db.commit()
        cursore.close()
        print("Database PostgreSQL inizializzato con successo (tabelle create/verificate)!")

    except (Exception, psycopg2.DatabaseError) as e:
        raise Exception(f"Errore durante l'inizializzazione del database: {e}")
    finally:
        if conn_db is not None:
            conn_db.close()

def inserisci_rider_nel_db(nome, veicolo, consegne_totali):
    conn_db = None
    try:
        conn_db = connessione_db()
        cursore = conn_db.cursor()

        query = """
            INSERT INTO riders (name, vehicle, total_deliveries)
            VALUES (%s, %s, %s)
            RETURNING id;
        """

        cursore.execute(query, (nome, veicolo, consegne_totali))
        id_generato = cursore.fetchone()[0]
        conn_db.commit()
        cursore.close()
        return id_generato
    except (Exception, psycopg2.DatabaseError) as e:
        raise Exception(f"Errore database: {e}")
    finally:
        if conn_db is not None:
            conn_db.close()

def list_rider_db():
    conn_db = None
    try:
        conn_db = connessione_db()
        cursore = conn_db.cursor()

        query = """
            SELECT r.id, r.name, r.vehicle, r.total_deliveries,
                COALESCE(ROUND(AVG(rev.rating), 1), 0.0), COUNT(rev.id)
            FROM riders r
            LEFT JOIN reviews rev ON r.id = rev.rider_id
            GROUP BY r.id
            ORDER BY r.id;
        """

        cursore.execute(query)
        risultato = cursore.fetchall()
        cursore.close()
        return risultato
    except (Exception, psycopg2.DatabaseError) as e:
        raise Exception(f"Errore database: {e}")
    finally:
        if conn_db is not None:
            conn_db.close()

def list_rider_filtrata_db(veicolo_da_filtrare):
    conn_db = None
    try:
        conn_db = connessione_db()
        cursore = conn_db.cursor()

        query = """
            SELECT r.id, r.name, r.vehicle, r.total_deliveries,
               COALESCE(ROUND(AVG(rev.rating), 1), 0.0), COUNT(rev.id)
            FROM riders r
            LEFT JOIN reviews rev ON r.id = rev.rider_id
            WHERE LOWER(r.vehicle) = LOWER(%s)
            GROUP BY r.id
            ORDER BY r.id;
        """

        cursore.execute(query, (veicolo_da_filtrare,))
        risultato = cursore.fetchall()
        cursore.close()
        return risultato
    except (Exception, psycopg2.DatabaseError) as e:
        raise Exception(f"Errore database: {e}")
    finally:
        if conn_db is not None:
            conn_db.close()

def media_voti_rider_db(rider_id):
    conn_db = None
    try:
        conn_db = connessione_db()
        cursore = conn_db.cursor()

        query = """
            SELECT COALESCE(ROUND(AVG(rating), 1), 0.0)
            FROM reviews
            WHERE rider_id = %s;
        """

        cursore.execute(query, (rider_id,))
        risultato = cursore.fetchone()
        cursore.close()
        return risultato[0] if risultato else 0.0
    except (Exception, psycopg2.DatabaseError) as e:
        raise Exception(f"Errore database: {e}")
    finally:
        if conn_db is not None:
            conn_db.close()


def esegui_reset_db():
    reset_attivo = os.getenv("ABILITA_RESET_DB", "False").lower() == "true"
    if not reset_attivo:
        print("Reset DB non attivo, salto il reset.")
        return #interrompe la funzione
    else:
        conn_db = None
        try:
            conn_db = connessione_db()
            cursore = conn_db.cursor()
            
            cursore.execute("TRUNCATE TABLE riders, reviews RESTART IDENTITY CASCADE;")

            riders_fittizi = [
            ("Michela", "moto", 120),
            ("Marco", "auto", 45),
            ("Alessandra", "scooter", 210),
            ("Francesca", "bicicletta", 80),
            ("Giorgo", "bicicletta", 10),
            ("Andrea", "furgone", 23),
            ("Nicola", "furgone", 3),
            ("Sara", "moto", 15),
            ("Paola", "scooter", 74)
            ]

            riders_id_generati = []
            for name, vehicle, total_deliveries in riders_fittizi:
                cursore.execute("""
                    INSERT INTO riders (name, vehicle, total_deliveries) 
                    VALUES (%s, %s, %s) RETURNING id;
                """, (name, vehicle, total_deliveries))

                id_nuovo_rider = cursore.fetchone()[0]
                riders_id_generati.append(id_nuovo_rider)

            recensioni_fittizie = [
                (riders_id_generati[0], "Angela", 5, "Super veloce e gentilissimo!"),
                (riders_id_generati[6], "Gianluca", 4, "Tutto perfetto, cibo ancora caldo."),
                (riders_id_generati[1], "Roberto", 3, "Consegna un po' in ritardo ma accettabile."),
                (riders_id_generati[2], "Sofia", 5, "Il miglior rider della zona, consigliatissimo!"),
                (riders_id_generati[3], "Luca", 2, "La pizza era un po' fredda purtroppo."),
                (riders_id_generati[1], "Elena", 5, "Puntuale e super professionale, consigliato!"),
                (riders_id_generati[2], "Marco", 4, "Consegna rapida, panino perfetto ed ancora ben caldo."),
                (riders_id_generati[3], "Davide", 1, "Il rider ha sbagliato strada e il cibo è arrivato in ritardo e freddo."),
                (riders_id_generati[7], "Chiara", 5, "Consegnato in anticipo con una gentilezza d'altri tempi. Cinque stelle strameritate!"),
                (riders_id_generati[4], "Stefano", 3, "Consegna nella norma, senza lodi e senza infamia."),
                (riders_id_generati[5], "Alessia", 5, "Ottimo servizio, il furgone garantisce che le vaschette grandi arrivino intatte."),
                (riders_id_generati[8], "Fabio", 2, "Ha faticato a trovare il citofono e l'ordine si è leggermente rovesciato nel tragitto.")
            ]

            for rider_id, customer_name, rating, comment in recensioni_fittizie:
                cursore.execute("""
                    INSERT INTO reviews (rider_id, customer_name, rating, comment)
                    VALUES (%s, %s, %s, %s);
                """, (rider_id, customer_name, rating, comment))

            conn_db.commit()
            print("Database resettato e popolato con successo!")
        
        except Exception as e:
            if conn_db:
                conn_db.rollback()
                print(f"Errore durante il reset del database: {str(e)}")
        finally:
            if conn_db:
                cursore.close()
                conn_db.close()

def controllo_id_rider_in_db(rider_id):
    conn_db = None
    try:
        conn_db = connessione_db()
        cursore = conn_db.cursor()

        cursore.execute("""
                    SELECT id, name, vehicle, total_deliveries
                    FROM riders
                    WHERE id = %s
                """, (rider_id,))

        risultato = cursore.fetchone()
        cursore.close()
        if risultato:
            return True
        else:
            return False
    except (Exception, psycopg2.DatabaseError) as e:
        raise Exception(f"Errore database: {e}")
    finally:
        if conn_db is not None:
            conn_db.close()

def inserisci_recensione_db(rider_id, customer_name, rating, comment):
    conn_db = None
    try:
        conn_db = connessione_db()
        cursore = conn_db.cursor()

        query = """
            INSERT INTO reviews (rider_id, customer_name, rating, comment)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """

        cursore.execute(query, (rider_id, customer_name, rating, comment))
        id_generato = cursore.fetchone()[0]
        conn_db.commit()
        cursore.close()
        return id_generato
    except (Exception, psycopg2.DatabaseError) as e:
        raise Exception(f"Errore database: {e}")
    finally:
        if conn_db is not None:
            conn_db.close()

def aggiorna_recensione_db(id_review, comment):
    conn_db = None
    try:
        conn_db = connessione_db()
        cursore = conn_db.cursor()

        query = """
            UPDATE reviews 
            SET comment = %s
            WHERE id = %s
        """

        cursore.execute(query, (comment, id_review))
        conn_db.commit()
        cursore.close()
        return id_review
    except (Exception, psycopg2.DatabaseError) as e:
        raise Exception(f"Errore database: {e}")
    finally:
        if conn_db is not None:
            conn_db.close()

def controllo_id_review_in_db(id_review):
    conn_db = None
    try:
        conn_db = connessione_db()
        cursore = conn_db.cursor()

        cursore.execute("""
                    SELECT id, rating, comment
                    FROM reviews
                    WHERE id = %s
                """, (id_review,))

        risultato = cursore.fetchone()
        cursore.close()
        if risultato:
            return True
        else:
            return False
    except (Exception, psycopg2.DatabaseError) as e:
        raise Exception(f"Errore database: {e}")
    finally:
        if conn_db is not None:
            conn_db.close()

def cancella_rider_e_recensioni_db(rider_id):
    conn_db = None
    try:
        conn_db = connessione_db()
        cursore = conn_db.cursor()

        cursore.execute("""
                    DELETE FROM riders
                    WHERE id = %s
                """, (rider_id,))

        righe_cancellate = cursore.rowcount
        conn_db.commit()
        cursore.close()
        if righe_cancellate>0:
            return True
        else:
            return False
    except (Exception, psycopg2.DatabaseError) as e:
        raise Exception(f"Errore database: {e}")
    finally:
        if conn_db is not None:
            conn_db.close()