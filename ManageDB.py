# SUPERNODES:   IP          PORT
# PEERS:        SESSIONID   IP      PORT
# FILES:        SESSIONID   NAME    MD5
# PACKETS:      ID      DATE

import sqlite3
import time

class ManageDB:

    # Metodo che inizializza il database
    def __init__(self):

        try:

            # Creo la connessione al database e creo un cursore ad esso
            conn = sqlite3.connect("data.db")
            c = conn.cursor()

            # Creo la tabella dei supernodi e la cancello se esiste
            c.execute("DROP TABLE IF EXISTS SUPERNODES")
            c.execute("CREATE TABLE SUPERNODES (IP TEXT NOT NULL, PORT TEXT NOT NULL)")

            # Creo la tabella dei peer e la cancello se esiste
            c.execute("DROP TABLE IF EXISTS PEERS")
            c.execute("CREATE TABLE PEERS (SESSIONID TEXT NOT NULL, IP TEXT NOT NULL, PORT TEXT NOT NULL)")

            # Creo la tabella dei file e la cancello se esiste
            c.execute("DROP TABLE IF EXISTS FILES")
            c.execute("CREATE TABLE FILES (SESSIONID TEXT NOT NULL, NAME TEXT NOT NULL, MD5 TEXT NOT NULL)")

            # Creo la tabella dei packetId e la cancello se esiste
            c.execute("DROP TABLE IF EXISTS PACKETS")
            c.execute("CREATE TABLE PACKETS (ID TEXT NOT NULL, DATE INTEGER NOT NULL)")

            # Imposto il tempo di cancellazione dei packets
            self.deleteTime = 300

            conn.commit()

        except sqlite3.Error as e:

            # Gestisco l'eccezione
            if conn:
                conn.rollback()

            raise Exception("Errore - init: %s:" % e.args[0])

        finally:

            # Chiudo la connessione
            if conn:
                conn.close()

    # Metodo che aggiunge un peer
    def addPeer(self, sessionId, ip, port):

        try:

            # Creo la connessione al database e creo un cursore ad esso
            conn = sqlite3.connect("data.db")
            c = conn.cursor()

            # Aggiungo il peer se non e' presente
            c.execute("SELECT COUNT(IP) FROM PEERS WHERE IP=:INDIP AND PORT=:PORTA", {"INDIP": ip, "PORTA": port})
            count = c.fetchall()

            if(count[0][0] == 0):
                c.execute("INSERT INTO PEERS (SESSIONID, IP, PORT) VALUES (?,?,?)" , (sessionId, ip, port))
            conn.commit()

        except sqlite3.Error as e:

            # Gestisco l'eccezione
            if conn:
                conn.rollback()

            raise Exception("Errore - addPeer: %s:" % e.args[0])

        finally:

            # Chiudo la connessione
            if conn:
                conn.close()

    # Metodo che aggiunge un supernodo
    def addSuperNode(self, ip, port):

        try:

            # Creo la connessione al database e creo un cursore ad esso
            conn = sqlite3.connect("data.db")
            c = conn.cursor()

            # Aggiungo il supernodo se non e' presente
            c.execute("SELECT COUNT(IP) FROM SUPERNODES WHERE IP=:INDIP AND PORT=:PORTA", {"INDIP": ip, "PORTA": port})
            count = c.fetchall()

            if(count[0][0] == 0):
                c.execute("INSERT INTO SUPERNODES (IP, PORT) VALUES (?,?)" , (ip, port))
            conn.commit()

        except sqlite3.Error as e:

            # Gestisco l'eccezione
            if conn:
                conn.rollback()

            raise Exception("Errore - addSuperNode: %s:" % e.args[0])

        finally:

            # Chiudo la connessione
            if conn:
                conn.close()


# SUPERNODES:   IP          PORT
# PEERS:        SESSIONID   IP      PORT
# FILES:        SESSIONID   NAME    MD5
# PACKETS:      ID      DATE

manager = ManageDB()

print("Aggiungo peer")
manager.addPeer("123", "1.1.1.1", "3000")

print("Aggiungo supernodo")
manager.addSuperNode("10.10.10.10", "80")
