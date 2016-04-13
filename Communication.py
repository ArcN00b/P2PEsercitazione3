from builtins import print

from Utility import *
import threading
import socket

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
            s.run()

class Sender:
    # Costruttore che inizializza gli attributi del Worker
    def __init__(self, messaggio, ip, port):
        # definizione thread del client
        self.messaggio = messaggio
        self.ip = ip
        self.port = port

    # Funzione che lancia il worker e controlla la chiusura improvvisa
    def run(self):
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
            print('inviato a ' + a +':'+str(self.port) + ' : ' + self.messaggio)
            sock.sendall(self.messaggio.encode())
            sock.close()
        except Exception as e:
            print("Errore Peer down " + self.ip + " " + str(self.port))

class SenderAndWait:
    # Costruttore che inizializza gli attributi del Worker
    def __init__(self, messaggio, ip, port):
        # definizione thread del client
        self.messaggio = messaggio
        self.ip = ip
        self.port = port
        self.sock = ''

    # Funzione che lancia il worker e controlla la chiusura improvvisa
    def run(self):
        try:
            r = random.randrange(0, 100)
            ipv4, ipv6 = Utility.getIp(self.ip)
            if r < 50:
                a = ipv4
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                a = ipv6
                self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

            self.sock.connect((a, int(self.port)))
            print('inviato a ' + a +':'+str(self.port) + ' : ' + self.messaggio)
            self.sock.sendall(self.messaggio.encode())
        except Exception as e:
            print("Errore Peer down " + self.ip + " " + str(self.port))

    def getSocket(self):
        return self.sock

    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.close()

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

class AFinder:
    # Costruttore che inizializza gli attributi del Worker
    def __init__(self, sock):
        self.sock = sock

    def run(self):
        # ricevo i primi 10 Byte che sono "ARET" + n_chunk
        recv_mess = self.sock.recv(7).decode()
        while len(recv_mess) < 7:
            recv_mess += self.sock.recv(7 - len(recv_mess)).decode()

        if recv_mess[:4] == "AFIN":
            numMd5 = int(recv_mess[4:7])

            # Leggo MD5 NAME NUM PEER dal socket
            for i in range(0, numMd5):
                tmp = self.sock.recv(119)  # leggo la lunghezza del chunk
                while len(tmp) < 119:
                    tmp += self.sock.recv(119 - len(tmp))
                    if len(tmp) == 0:
                        raise Exception("Socket close")

                print(tmp)

                # Eseguo controlli di coerenza su ciò che viene ricavato dal socket
                if not tmp[116:].decode(errors='ignore').isnumeric():
                    raise Exception("Packet loss")

                # Salvo cie che e stato ricavato in ListFindFile
                Utility.listFindFile.append([tmp[:16].decode(), tmp[16:-3].decode(), int(tmp[-3:].decode())])

                # Ottengo la lista dei peer che hanno lo stesso md5
                numPeer = Utility.listFindFile[Utility.numFindFile][2]
                for j in range(0, numPeer):

                    # Leggo i dati di ogni peer dal socket
                    buffer = self.sock.recv(60)  # Leggo il contenuto del chunk
                    while len(buffer) < 60:
                        tmp = self.sock.recv(60 - len(buffer))
                        buffer += tmp
                        if len(tmp) == 0:
                            raise Exception("Socket close")

                    # Salvo ciò che e stato ricavato in Peer List
                    Utility.listFindPeer.append([tmp[:55].decode(), int(tmp[55:].decode())])
