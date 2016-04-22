import random
import time
import hashlib
import ManageDB
import socket
import threading

class Utility:

    MY_IPV4="172.030.007.002"
    MY_IPV6="fc00:0000:0000:0000:0000:0000:0007:0002"

    #MY_IPV4="127.000.000.001"
    #MY_IPV6="0000:0000:0000:0000:0000:0000:0000:0001"

    PORT=3000
    PATHDIR='/home/simone/Immagini/'

    listFindPeer = []
    listFindFile = []
    listResultFile = []
    numFindSNode=0
    listFindSNode=[]
    superNodo=False # Indica se il programma in esecuzione e' un SuperNodo o un Peer
    ipSuperNodo='' # Indica l'ip del SuperNodo a cui il Peer e' collegato
    portSuperNodo='' # Indica la porta del SuperNodo a cui il Peer e' collegato
    sessionId='' # Indica il sessionId del Peer
    database = ManageDB.ManageDB()

    database.addSuperNode("172.030.007.004|fc00:0000:0000:0000:0000:0000:0007:0004","03000")

    # Metodo che genera un numero random nel range [1024, 65535]
    @staticmethod
    def generatePort():
        random.seed(time.process_time())
        return random.randrange(1024, 65535)
    # Questo metodo genera un packet id randomico
    # Chiede di quanti numeri deve essere il valore generato
    @staticmethod
    def generateId(lunghezza):
        random.seed(time.process_time())
        seq = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        val = ''
        for i in range(0, lunghezza):
            val = val + random.choice(seq)
        return val

    # Metodo per generare l'md5 di un file, va passato il percorso assoluto
    @staticmethod
    def generateMd5(path):

        #path="/home/flavio/Scrivania/pippo.txt"
        # Inizializzo le variabili che utilizzerò
        f = open(path, 'rb')
        hash = hashlib.md5()

        # Per una lettura più efficiente suddivido il file in blocchi
        buf = f.read(4096)
        while len(buf) > 0:
            hash.update(buf)
            buf = f.read(4096)

        # Return del digest
        return hash.hexdigest()

        # Ritorna i due ip data la stringa generale
        # Ritorna prima ipv4 e poi ipv6

    @staticmethod
    def getIp(stringa):
        t = stringa.find('|')
        if t != -1:

            ''' Modifico così questa funzione poiche se usiamo una connect di un indirizzo come 127.000.000.001
                purtroppo da errore, così trasformo l'ip sopra in 127.0.0.1'''
            ipv4 = ''
            tmp = stringa[0:t].split('.')
            for grp in tmp:
                if len(grp.lstrip('0')) == 0:
                    ipv4 += '0.'
                else:
                    ipv4 += grp.lstrip('0') + '.'
            ipv4 = ipv4[0:-1]
            # estrazione ipv6
            ipv6 = ''
            tmp = stringa[t+1:].split(':')
            for grp in tmp:
                w = grp.lstrip('0')
                if len(w) != 0:
                    ipv6 += w + ':'
                else:
                    ipv6 += '0:'
            ipv6 = ipv6[0:-1]
            return ipv4, ipv6
        else:
            return '', ''

