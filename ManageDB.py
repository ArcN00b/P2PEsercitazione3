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
                c.execute("UPDATE FILES SET NAME=:NOME WHERE MD5=:COD" , {"NOME": fileName, "COD": Md5})
                conn.commit()
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

    # Metodo che aggiunge un packetId
    def addPkt(self, id):
        try:

            # Creo la connessione al database e creo un cursore ad esso
            conn = sqlite3.connect("data.db")
            c = conn.cursor()

            # Rimuovo i packets meno recenti ed aggiungo il packet
            c.execute("DELETE FROM PACKETS WHERE DATE < datetime('now', 'LOCALTIME', ?)" , ("-" + str(self.deleteTime) + " SECONDS",) )
            conn.commit()

            # Inserisco il packet solamento se non presente
            c.execute("SELECT COUNT(ID) FROM PACKETS WHERE ID=:COD", {"COD": id})
            count = c.fetchall()
            if(count[0][0] == 0):
                c.execute("INSERT INTO PACKETS (ID, DATE) VALUES ( ?, DATETIME('NOW', 'LOCALTIME'))" , (id,))

            conn.commit()

        except sqlite3.Error as e:

            # Gestisco l'eccezione
            if conn:
                conn.rollback()

            raise Exception("Errore - addPkt: %s:" % e.args[0])

        finally:

            # Chiudo la connessione
            if conn:
                conn.close()

    # Metodo che ricerca un packetId, ritorna True se e' presente, altrimenti False
    def checkPkt(self, id):
        try:

            # Creo la connessione al database e creo un cursore ad esso
            conn = sqlite3.connect("data.db")
            c = conn.cursor()

            # Elimino i packets meno recenti e verifico se e' presente il packet
            c.execute("DELETE FROM PACKETS WHERE DATE < datetime('now', 'LOCALTIME', ?)" , ("-" + str(self.deleteTime) + " SECONDS",) )
            conn.commit()
            c.execute("SELECT COUNT(ID) FROM PACKETS WHERE ID=:COD" , {"COD": id} )
            conn.commit()

            count  = c.fetchall()

            # Ritorno True se il packet e' presente, altrimenti False
            if(count[0][0] == 1):
                return True
            elif(count[0][0] == 0):
                return False
            else:
                raise Exception("Errore - checkPkt: packetId multipli con stesso id")

        except sqlite3.Error as e:

            raise Exception("Errore - checkPkt: %s:" % e.args[0])

        finally:

            # Chiudo la connessione
            if conn:
                conn.close()



# SUPERNODES:   IP          PORT
# PEERS:        SESSIONID   IP      PORT
# FILES:        SESSIONID   NAME    MD5
# PACKETS:      ID      DATE

manager = ManageDB()

print("Aggiungo Peer")
manager.addPeer("123", "1.1.1.1", "3000")
manager.addPeer("456", "1.1.1.2", "3000")
manager.addPeer("789", "1.1.1.3", "3000")
print("Lista Peer")
all_rows = manager.listPeer()
for row in all_rows:
    print('{0} {1} {2}'.format(row[0],row[1],row[2]))
print("")


print("Aggiungo SuperNodo")
manager.addSuperNode("10.10.10.10", "80")
manager.addSuperNode("20.20.20.20", "80")
print("Lista SuperNodi")
all_rows = manager.listSuperNode()
for row in all_rows:
    print('{0} {1}'.format(row[0],row[1]))
print("")


print("Metodo findPeer flag 1")
all_rows = manager.findPeer(0,"1.1.1.3","3000",1)
for row in all_rows:
    print('{0}'.format(row[0]))
print("")


print("Metodo findPeer flag 2")
all_rows = manager.findPeer("123",0,0,2)
for row in all_rows:
    print('{0} {1}'.format(row[0],row[1]))
print("")


print("Aggiungo File")
manager.addFile("123","pippo","1111")
manager.addFile("123","pluto","2222")
manager.addFile("456","pluto2","2222")
manager.addFile("456","paperino","3333")
print("Lista File")
all_rows = manager.listFile()
for row in all_rows:
    print('{0} {1} {2}'.format(row[0],row[1],row[2]))
print("")


print("Rimuovo File")
manager.removeFile("123","2222")
print("Lista File")
all_rows = manager.listFile()
for row in all_rows:
    print('{0} {1} {2}'.format(row[0],row[1],row[2]))
print("")


print("Lista File da SessionID")
all_rows = manager.listFileForSessionId("456")
for row in all_rows:
    print('{0} {1}'.format(row[0],row[1]))
print("")


print("Rimuovo tutti File da SessionID")
manager.removeAllFileForSessionId("456")
print("Lista File")
all_rows = manager.listFile()
for row in all_rows:
    print('{0} {1} {2}'.format(row[0],row[1],row[2]))
print("")

