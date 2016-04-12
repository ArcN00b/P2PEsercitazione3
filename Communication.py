from builtins import print

from Utility import *
import threading
import socket
import logging

# questa classe non e' un thread, ma ne genera per inviare i dati
class SenderAll:
    # Costruttore che inizializza gli attributi del Worker
    def __init__(self, messaggio, listaNear):
        # definizione thread del client
        self.messaggio = messaggio
        self.listaNear = listaNear

    # Funzione che lancia il worker e controlla la chiusura improvvisa
    def run(self):
        for i in range(0, len(self.listaNear)):
            messaggio = self.messaggio
            ip = self.listaNear[i][0]
            porta = self.listaNear[i][1]

            s = Sender(messaggio, ip, porta)
            s.start()

class Sender:
    # Costruttore che inizializza gli attributi del Worker
    def __init__(self, messaggio, ip, port):
        # definizione thread del client
        self.messaggio = messaggio
        self.ip = ip
        self.port = port

    # Funzione che lancia il worker e controlla la chiusura improvvisa
    def start(self):
        try:
            r = random.randrange(0, 100)
            ipv4, ipv6 = Utility.getIp(self.ip)
            if r < 50:
                a = ipv4
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                a = ipv6
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

            sock.connect((a, int(self.port)))
            print('inviato a ' + a+':'+str(self.port) + ' : ' + self.messaggio)
            sock.sendall(self.messaggio.encode())
            sock.close()
        except Exception as e:
            print("Errore Peer down " + self.ip + " " + self.port)

class Downloader(threading.Thread):
    # Costruttore che inizializza gli attributi del Worker
    def __init__(self, ipp2p, pp2p, md5, name):
        # definizione thread del client
        threading.Thread.__init__(self)
        self.ipp2p = ipp2p
        self.pp2p = pp2p
        self.md5 = md5
        self.name = name

    # Funzione che lancia il worker e controlla la chiusura improvvisa
    def run(self):
        #try:
        ipp2p = self.ipp2p
        pp2p = self.pp2p
        md5 = self.md5
        name = self.name

        r = random.randrange(0,100)
        ipv4, ipv6 = Utility.getIp(ipp2p)
        if r < 50:
            ind = ipv4
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            ind = ipv6
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        sock.connect((ind, int(pp2p)))
        mess = 'RETR' + md5
        sent = sock.send(mess.encode())
        if sent is None or sent < len(mess):
            print('recupero non effettuato')
            sock.close()
            return

        # ricevo i primi 10 Byte che sono "ARET" + n_chunk
        recv_mess = sock.recv(10).decode()
        if recv_mess[:4] == "ARET":
            num_chunk = int(recv_mess[4:])
            count_chunk = 0

            # apro il file per la scrittura
            f = open(Utility.PATHDIR + name.rstrip(' '), "wb")  # Apro il file rimuovendo gli spazi finali dal nome

            # Finchè i chunk non sono completi
            print("Download in corso", end='\n')
            for count_chunk in range(0, num_chunk):
                tmp = sock.recv(5)  # leggo la lunghezza del chunk
                while len(tmp) < 5:
                    tmp += sock.recv(5 - len(tmp))
                    if len(tmp) == 0:
                        raise Exception("Socket close")

                # Eseguo controlli di coerenza su ciò che viene ricavato dal socket
                if tmp.decode(errors='ignore').isnumeric() == False:
                    raise Exception("Packet loss")
                chunklen = int(tmp.decode())
                buffer = sock.recv(chunklen)  # Leggo il contenuto del chunk

                # Leggo i dati del file dal socket
                while len(buffer) < chunklen:
                    tmp = sock.recv(chunklen - len(buffer))
                    buffer += tmp
                    if len(tmp) == 0:
                        raise Exception("Socket close")

                f.write(buffer)  # Scrivo il contenuto del chunk nel file

            f.close()
            print("Download completato")

        sock.close()
