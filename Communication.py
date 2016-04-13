from Utility import *
import socket

# questa classe non e' un thread, ma ne genera per inviare i dati
class Communication:

    @staticmethod
    def senderAll(messaggio, listaNear):
        for i in range(0, len(listaNear)):
            ip = listaNear[i][0]
            porta = listaNear[i][1]

            Communication.sender(messaggio, ip, porta, 1)

    # Metodo che invia semplicemente il messaggio a ip e porta
    @staticmethod
    def sender(messaggio, ip, port, flag):
        try:
            r = 0 #random.randrange(0, 100)
            ipv4, ipv6 = Utility.getIp(ip)
            if r < 50:
                a = ipv4
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                a = ipv6
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

            sock.connect((a, int(port)))
            print('inviato a ' + a+':'+str(port) + ' : ' + messaggio)
            sock.sendall(messaggio.encode())
            if flag == 1:
                sock.close()
            else:
                return sock
        except Exception as e:
            print("Errore Peer down " + ip + " " + port)

    # Costruttore che inizializza gli attributi del Worker
    @staticmethod
    def downloader(ipp2p, pp2p, md5, name):

        r = 0#random.randrange(0,100)
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

    @staticmethod
    def aFinder(sock):
        # ricevo i primi 10 Byte che sono "ARET" + n_chunk
        recv_mess = sock.recv(7).decode()

        if recv_mess[:4] == "AFIN":
            numMd5 = int(recv_mess[4:7])

            # Leggo MD5 NAME NUM PEER dal socket
            for i in range(0, numMd5):
                tmp = sock.recv(119)  # leggo la lunghezza del chunk
                while len(tmp) < 119:
                    tmp += sock.recv(119 - len(tmp))
                    if len(tmp) == 0:
                        raise Exception("Socket close")

                # Eseguo controlli di coerenza su ciò che viene ricavato dal socket
                if not tmp[-3:].decode(errors='ignore').isnumeric():
                    raise Exception("Packet loss")

                # Salvo cie che e stato ricavato in ListFindFile
                Utility.listFindFile.append([tmp[:16].decode(), tmp[16:-3].decode(), int(tmp[-3:].decode())])

                # Ottengo la lista dei peer che hanno lo stesso md5
                numPeer = Utility.listFindFile[Utility.numFindFile][2]
                for j in range(0, numPeer):

                    # Leggo i dati di ogni peer dal socket
                    buffer = sock.recv(60)  # Leggo il contenuto del chunk
                    while len(buffer) < 60:
                        tmp = sock.recv(60 - len(buffer))
                        buffer += tmp
                        if len(tmp) == 0:
                            raise Exception("Socket close")

                    # Salvo ciò che e stato ricavato in Peer List
                    Utility.listFindPeer.append([tmp[:55].decode(), int(tmp[-5:].decode())])
