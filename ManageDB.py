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
            self.deleteTime = 20

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

    # Metodo ritorna la lista di supernodi
    def listSuperNode(self):
        count=None
        try:
            # Connessione
            conn=sqlite3.connect("data.db")
            c=conn.cursor()

            c.execute("SELECT * FROM SUPERNODES")
            count=c.fetchall()

            conn.commit()

        except sqlite3.Error as e:
            # Gestisco l'eccezione
            if conn:
                conn.rollback()

            raise Exception("Errore - listSuperNode: %s:" % e.args[0])
        finally:
            # Chiudo la connessione
            if conn:
                conn.close()
            if count is not None:
                return count

    # Metodo che ritorna la lista dei peer
    def listPeer(self):
        count=None
        try:
            # Connessione
            conn=sqlite3.connect("data.db")
            c=conn.cursor()

            c.execute("SELECT * FROM PEERS")
            count=c.fetchall()

            conn.commit()

            return conn

        except sqlite3.Error as e:
            # Gestisco l'eccezione
            if conn:
                conn.rollback()

            raise Exception("Errore - listPeer: %s:" % e.args[0])
        finally:
            # Chiudo la connessione
            if conn:
                conn.close()
            if count is not None:
                return count

    # Metodo per trovare un peer
    def findPeer(self,sessionId,ip,port,flag):
        count=None
        try:
            # Connessione
            conn=sqlite3.connect("data.db")
            c=conn.cursor()

            if flag==1:
                c.execute("SELECT SESSIONID FROM PEERS WHERE IP=:INDIP AND PORT=:PORTA", {"INDIP": ip, "PORTA": port})
                count = c.fetchall()
            elif flag==2:
                c.execute("SELECT IP,PORT FROM PEERS WHERE SESSIONID=:SID", {"SID": sessionId})
                count = c.fetchall()

            conn.commit()

        except sqlite3.Error as e:
            # Gestisco l'eccezione
            if conn:
                conn.rollback()

            raise Exception("Errore - findPeer: %s:" % e.args[0])
        finally:
            # Chiudo la connessione
            if conn:
                conn.close()
            if count is not None:
                return count

    # Metodo che aggiunge un file
    def addFile(self,sessionId,fileName,Md5):
        try:

            # Creo la connessione al database e creo un cursore ad esso
            conn = sqlite3.connect("data.db")
            c = conn.cursor()

            # Aggiungo il file se non e' presente
            c.execute("SELECT * FROM FILES WHERE NAME=:FNAME AND MD5=:M AND SESSIONID=:SID", {"FNAME": fileName, "M": Md5, "SID":sessionId})
            count = c.fetchall()

            if(len(count)==0):
                c.execute("INSERT INTO FILES (SESSIONID, NAME, MD5) VALUES (?,?,?)" , (sessionId, fileName, Md5))
            conn.commit()

        except sqlite3.Error as e:

            # Gestisco l'eccezione
            if conn:
                conn.rollback()

            raise Exception("Errore - addFile: %s:" % e.args[0])

        finally:

            # Chiudo la connessione
            if conn:
                conn.close()

    # Metodo che rimuove un file
    def removeFile(self,sessionId,Md5):
        try:

            # Creo la connessione al database e creo un cursore ad esso
            conn = sqlite3.connect("data.db")
            c = conn.cursor()

            c.execute("DELETE FROM FILES WHERE SESSIONID=:SID AND MD5=:M", {"SID": sessionId, "M": Md5})
            conn.commit()

        except sqlite3.Error as e:

            # Gestisco l'eccezione
            if conn:
                conn.rollback()

            raise Exception("Errore - removeFile: %s:" % e.args[0])

        finally:

            # Chiudo la connessione
            if conn:
                conn.close()

    # Metodo che rimuove tutti i file di un sessionId
    def removeAllFileForSessionId(self,sessionId):
        count=None
        try:

            # Creo la connessione al database e creo un cursore ad esso
            conn = sqlite3.connect("data.db")
            c = conn.cursor()

            c.execute("SELECT COUNT(MD5) FROM FILES WHERE SESSIONID=:SID", {"SID": sessionId})
            count = c.fetchall()

            if (count[0][0]>0):
                c.execute("DELETE FROM FILES WHERE SESSIONID=:SID", {"SID": sessionId})
                conn.commit()

        except sqlite3.Error as e:

            # Gestisco l'eccezione
            if conn:
                conn.rollback()

            raise Exception("Errore - removeAllFileForSessionId: %s:" % e.args[0])

        finally:

            # Chiudo la connessione
            if conn:
                conn.close()
            if count is not None:
                return count[0][0]

    # Metodo per avere la lista di file per un sessionID
    def listFileForSessionId(self,sessionId):
        count=None
        try:
            # Connessione
            conn=sqlite3.connect("data.db")
            c=conn.cursor()

            c.execute("SELECT MD5,NAME FROM FILES WHERE SESSIONID=:SID",{"SID":sessionId})
            count=c.fetchall()

            conn.commit()

        except sqlite3.Error as e:
            # Gestisco l'eccezione
            if conn:
                conn.rollback()

            raise Exception("Errore - listFileForSessionId: %s:" % e.args[0])
        finally:
            # Chiudo la connessione
            if conn:
                conn.close()
            if count is not None:
                return count

    # Metodo ritorna tutta la tabella files
    def listFile(self):
        count=None
        try:
            # Connessione
            conn=sqlite3.connect("data.db")
            c=conn.cursor()

            c.execute("SELECT * FROM FILES")
            count=c.fetchall()

            conn.commit()

        except sqlite3.Error as e:
            # Gestisco l'eccezione
            if conn:
                conn.rollback()

            raise Exception("Errore - listFile: %s:" % e.args[0])
        finally:
            # Chiudo la connessione
            if conn:
                conn.close()
            if count is not None:
                return count

    # Metodo per ricerca nome file da sessionId e Md5
    def findFile(self,sessionId,Md5):
        count=None
        try:
            # Connessione
            conn=sqlite3.connect("data.db")
            c=conn.cursor()

            c.execute("SELECT NAME FROM FILES WHERE SESSIONID=:SID AND MD5=:M",{"SID":sessionId,"M":Md5})
            count=c.fetchall()

            conn.commit()

        except sqlite3.Error as e:
            # Gestisco l'eccezione
            if conn:
                conn.rollback()

            raise Exception("Errore - listFileForSessionId: %s:" % e.args[0])
        finally:
            # Chiudo la connessione
            if conn:
                conn.close()
            if count is not None:
                return count







# SUPERNODES:   IP          PORT
# PEERS:        SESSIONID   IP      PORT
# FILES:        SESSIONID   NAME    MD5
# PACKETS:      ID      DATE
'''
manager = ManageDB()

print("Aggiungo peer")
manager.addPeer("123", "1.1.1.1", "3000")

print("Aggiungo supernodo")
manager.addSuperNode("10.10.10.10", "80")'''
