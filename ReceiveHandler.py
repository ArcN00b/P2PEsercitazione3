from Utility import *
from Communication import *
from Parser import *
import asyncore
import logging
import os

class ReceiveHandler(asyncore.dispatcher):

    def __init__(self, conn_sock, address):
        asyncore.dispatcher.__init__(self,conn_sock)
        self.conn_sock = conn_sock
        self.address = address
        self.out_buffer = []

##  metodo di scrittura sul buffer, quando pronto viene svuotato
##  molto utile per l'upload
    def write(self, data):
        self.out_buffer.append(data)

##  eventuale metodo per chiudere la connessione
##  questo va utilizzato se si vuole evitare di ricevere 0
    def shutdown(self):
        self.out_buffer.append(None)

##  overide metodo handle_read
    def handle_read(self):

        data = self.recv(2048)
        logging.debug(data)
        print(data)

        if len(data) > 0:
            # converto i comandi
            command, fields = Parser.parse(data.decode())

            if command == "RETR":
                # TODO controllare coerenza con nuovi metodi
                # Imposto la lunghezza dei chunk e ottengo il nome del file a cui corrisponde l'md5
                chuncklen = 512
                peer_md5 = fields[0]
                # TODO cambiato questo metodo perche il database e cambiato
                obj = Utility.database.findFile(Utility.sessionId,peer_md5,1)

                if len(obj) > 0:
                    # svuota il buffer
                    self.out_buffer = []
                    filename = Utility.PATHDIR + str(obj[0][0])
                    # lettura statistiche file
                    statinfo = os.stat(filename)
                    # imposto lunghezza del file
                    len_file = statinfo.st_size
                    # controllo quante parti va diviso il file
                    num_chunk = len_file // chuncklen
                    if len_file % chuncklen != 0:
                        num_chunk = num_chunk + 1
                    # pad con 0 davanti
                    num_chunk = str(num_chunk).zfill(6)
                    # costruzione risposta come ARET0000XX
                    mess = ('ARET' + num_chunk).encode()
                    self.write(mess)

                    # Apro il file in lettura e ne leggo una parte
                    f = open(filename, 'rb')
                    r = f.read(chuncklen)

                    # Finche il file non termina
                    while len(r) > 0:

                        # Invio la lunghezza del chunk
                        mess = str(len(r)).zfill(5).encode()
                        self.write(mess + r)
                        logging.debug('messaggio nel buffer pronto')

                        # Proseguo la lettura del file
                        r = f.read(chuncklen)
                    # Chiudo il file
                    f.close()
                    self.shutdown()

            elif command == "FIND":
                # TODO compilare manualmente listresultfile invece di inviare la query a se stesso
                pktID = Utility.generateId(16)
                #Ricavo i campi dal messaggio
                sessionID = fields[0]
                search = fields[1]

                '''# Salvo pkID, IP e Porta del peer che ha inviato FIND
                lst = Utility.database.findPeer(sessionID,None,None,2)
                Utility.listPeer.append([pkID, lst[0][0], lst[0][1]])'''

                # Preparo il messaggio da inviare ai peer
                ip = Utility.MY_IPV4 + '|' + Utility.MY_IPV6
                port = '{:0>5}'.format(Utility.PORT)
                ttl = '{:0>2}'.format(5)
                msg = "QUER" + pktID + ip + port + ttl + search
                Utility.database.addPkt(pktID)

                # Invio la query a tutti i supernodi conosciuti
                lista = Utility.database.listSuperNode()
                lista.append([Utility.MY_IPV4+'|'+Utility.MY_IPV6,Utility.PORT])
                if len(lista) > 0:
                    t1 = SenderAll(msg, lista)
                    t1.run()

                # TIME SLEEP PER ATTENDERE I RISULTATI DELLA QUERY
                time.sleep(4)

                # Estraggo i risultati da Utility.listResultFile eliminandoli
                result = [row for row in Utility.listResultFile if pktID in row]
                Utility.listResultFile = [row for row in Utility.listResultFile if pktID not in row]

                ''' Il formato delle righe di result e quello delle AQUE senza il "AQUE" quindi:

                Result[i][0] = PKTID
                Result[i][1] = IP
                Result[i][2] = PORT
                Result[i][3] = MD5
                Result[i][4] = FILENAME

                Uso questo commento per non sbagliare i campi successivamente e per debug
                MD5 list e pensata per avere in ogni riga MD5 NAME NPEER
                '''

                # Preparo le strutture dati per gestire l'invio dei risultati
                md5List = []
                peerList = []
                numMd5 = 0
                numPeer = 0

                # Suddivido i risultati per md5 diversi
                for i in range(0,len(result)):
                    # Controllo se l'md5 effettivamente e diverso
                    if result[i][3] not in md5List:
                        md5List.append([result[i][3], result[i][4], 0]) # MD5 NAME e NPEER
                        peerList.append(result[i][1], result[i][2])     # IP e PORT
                        numPeer = 1

                        # Controllo nel resto dei risultati se e presente lo stesso MD5
                        for j in range(i+1, len(result)):
                            if md5List[numMd5][0] == result[j][3]:
                                peerList.append(result[j][1], result[j][2])
                                numPeer += 1
                        md5List[numMd5][2] = numPeer
                        numMd5 += 1

                # Compongo il messaggio di ritorno stile upload
                mess = ("AFIN" + '{:0>3}'.format(len(md5List))).encode()
                self.write(mess)

                # Ora scorro entrambe le strutture compilate in precedenza così compilo il messaggio di risposta
                j = 0
                for i in range(0,len(md5List)):
                    # Preparo per l'invio MD5 NAME NumPeer
                    self.write((md5List[i][0] + md5List[i][1] + md5List[i][2]).encode())
                    logging.debug('messaggio nel buffer pronto')

                    # Ora devo inserire nel messaggio tutti i peer che hanno il file
                    for k in range (0, md5List[i][2]):
                        self.write(peerList[j][0] + peerList[j][1])
                        j += 1

                self.shutdown()

            elif command == "AFIN":
                numMd5 = fields[0]

                # Leggo MD5 NAME NUM PEER dal socket
                for i in range(0, numMd5):
                    tmp = self.recv(119)  # leggo la lunghezza del chunk
                    while len(tmp) < 119:
                        tmp += self.recv(119 - len(tmp))
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
                        buffer = self.recv(60)  # Leggo il contenuto del chunk
                        while len(buffer) < 60:
                            tmp = self.recv(60 - len(buffer))
                            buffer += tmp
                            if len(tmp) == 0:
                                raise Exception("Socket close")

                        # Salvo ciò che e stato ricavato in Peer List
                        Utility.listFindPeer.append([tmp[:55].decode(), int(tmp[-5:].decode())])

            elif command == "QUER":
                msgRet = 'AQUE'
                # Prendo i campi del messaggio ricevuto
                pkID = fields[0]
                ipDest = fields[1]
                portDest = fields[2]
                ttl = fields[3]
                name = fields[4]

                # Controllo se il packetId e già presente se e presente non rispondo alla richiesta
                # E non la rispedisco
                if not Utility.database.checkPkt(pkID):
                    Utility.database.addPkt(pkID)
                    # Esegue la risposta ad una query
                    msgRet = msgRet + pkID
                    ip = Utility.MY_IPV4 + '|' + Utility.MY_IPV6
                    port = '{:0>5}'.format(Utility.PORT)
                    msgRet = msgRet + ip + port
                    lst = Utility.database.findMd5(name.strip(' '))
                    for i in range(0, len(lst)):
                        name = Utility.database.findFile(None,lst[i][0],2)
                        r = msgRet
                        r = r + lst[i][0] + str(name[0][0]).ljust(100, ' ')
                        t1 = Sender(r, ipDest, portDest)
                        t1.run()

                    # controllo se devo divulgare la query
                    if int(ttl) >= 1:
                        ttl = '{:0>2}'.format(int(ttl) - 1)
                        msg = "QUER" + pkID + ipDest + portDest + ttl + name
                        lista = Utility.database.listSuperNode()
                        if len(lista) > 0:
                            t2 = SenderAll(msg, lista)
                            t2.run()

            # Salvo il risultato in una lista di risultati
            elif command=="AQUE":
                if Utility.database.checkPkt(fields[0]):
                    Utility.listResultFile.append(fields)

            #Procedura LOGI
            elif command=='LOGI':
                # solo il supernodo risponde a una LOGI
                if Utility.superNodo:
                    ip=fields[0]
                    port=fields[1]
                    try:
                        # se il peer e presente gli do il suo vecchio sessionId altrimenti uno nuovo
                        l=Utility.database.findPeer('',ip,port,1)
                        if len(l)>0:
                            ssID=l[0][0]
                        else:
                            ssID=Utility.generateId(16)
                        Utility.database.addPeer(ssID,ip,port)
                    except Exception as e:
                        ssID='0'*16

                    msgRet='ALGI'+ssID
                    t=Sender(msgRet,ip,port)
                    t.start()

            # Procedura ALGI
            elif command=='ALGI':
                # Solo il peer deve elaborare una algi
                if not Utility.superNodo and Utility.sessionId=='':
                    # controllo se ho ricevuto un sessionId valido se si lo salvo altrimenti no
                    s='0'*16
                    ssID=fields[0]
                    if ssID==s:
                        Utility.ipSuperNodo=''
                        Utility.portSuperNodo=''
                    else:
                        Utility.sessionId=ssID

            #Procedura ADFF
            elif command=='ADFF':
                # solo il supernodo deve elaborare una adff
                if Utility.superNodo:
                    ssID=fields[0]
                    md5=fields[1]
                    name=fields[2]
                    # controllo se il sessionId e registrato nel database
                    # se si aggiungo il file al database
                    l=Utility.database.findPeer(ssID,'','',2)
                    if len(l)>0:
                        Utility.database.addFile(ssID,name,md5)

            # Procedura DEFF
            elif command=='DEFF':
                # solo il supernodo deve elaborare una deff
                if Utility.superNodo:
                    ssID=fields[0]
                    md5=fields[1]
                    # controllo se il sessionId e registrato nel database
                    # se si rimuovo il file al database
                    l=Utility.database.findPeer(ssID,'','',2)
                    if len(l)>0:
                        Utility.database.removeFile(ssID,md5)

            # Procedura LOGO
            elif command=='LOGO':
                # solo il supernodo deve elaborare una richiesta logo
                if Utility.superNodo:
                    ssID=fields[0]
                    # controllo se il sessionId e nel database
                    l=Utility.database.findPeer(ssID,'','',2)
                    if len(l)>0:
                        # se il sessionId e presente rimuovo i suoi file e ritorno il messaggio ALGO
                        ip=l[0][0]
                        port=l[0][1]
                        #cancello tutti i file di quel sessionId
                        canc=Utility.database.removeAllFileForSessionId(ssID)
                        #cancello il peer dalla tabella dei peer
                        Utility.database.removePeer(ssID)
                        #Comunico al peer il messaggio di ritorno
                        msgRet='ALGO'+'{:0>3}'.format(canc)
                        t=Sender(msgRet,ip,port)
                        t.start()

            # Procedura ALGO
            elif command=='ALGO':
                # solo il peer deve elaborare la ALGO
                if not Utility.superNodo:
                    #Azzero le variabili e stampo
                    delete=fields[0]
                    Utility.sessionId=''
                    Utility.ipSuperNodo=''
                    Utility.portSuperNodo=''
                    print('Logout effetuato, cancellati: '+delete)

            # Procedura SUPE
            elif command=="SUPE":
                pkID=fields[0]

                # Controllo di non aver gia' ricevuto questa richiesta di SUPE
                if Utility.database.checkPkt(pkID)==False:
                    Utility.database.addPkt(pkID)

                    # Se sono un supernodo rispondo con ASUP
                    if Utility.superNodo:
                        ip=Utility.MY_IPV4+"|"+Utility.MY_IPV6
                        port='{:0>5}'.format(Utility.PORT)
                        msgRet="ASUP"+pkID+ip+port
                        t=Sender(msgRet,fields[1],fields[2])
                        t.start()

                    # Decremento il ttl e controllo se devo inviare il SUPE
                    ttl = int(fields[3])-1
                    if ttl > 0:
                        ttl='{:0>2}'.format(ttl)
                        msg="SUPE"+pkID+fields[1]+fields[2]+ttl

                        # Inoltro a tutti i peer
                        listaP=Utility.database.listPeer(2)
                        if len(listaP)>0:
                            tP = SenderAll(msg,listaP)
                            tP.run()

                        # Inoltro a tutti i supernodi
                        listaS=Utility.database.listSuperNode()
                        if len(listaS)>0:
                            tS = SenderAll(msg,listaS)
                            tS.run()

            # Procedura ASUP
            elif command=="ASUP":
                pkID=fields[0]
                ip=fields[1]
                port=fields[2]

                # Verifico che il pacchetto ricevuto sia corrispondente ad una mia SUPE
                if Utility.database.checkPkt(pkID)==True:

                    # Inserisco il supernodo nel db
                    Utility.database.addSuperNode(ip,port)

                    # Procedura per la visualizzazione dei supernodi quando ci si vuole collegare ad un supernodo
                    if Utility.superNodo==False:

                        # Verifico che il supernodo non sia gia' stato considerato
                        findPeer=False
                        for i in range(0,len(Utility.listFindSNode)):
                            if Utility.listFindSNode[i][1]==ip and Utility.listFindSNode[i][2]==port:
                                findPeer=True

                        # Se il pacchetto ASUP contiene un indirizzo di supernodo non ancora considerato
                        #   lo aggiungo ai supernodi a cui si puo' collegare il peer
                        if not findPeer:
                            Utility.numFindSNode+=1
                            Utility.listFindSNode.append(fields)
                            print(str(Utility.numFindSNode) + " " + ip + " " + port)

            else:
                logging.debug('ricevuto altro')

##   metodo che verifica la possibilita' di scrivere delle
##   informazioni sul canale
    def writable(self):
        return (len(self.out_buffer) > 0)

##  metodo per scrivere in uscita dal canale
    def handle_write(self):
        if self.out_buffer[0] is None:
            logging.debug('informazione trasferita')
            self.close()
            return

        sent = self.send(self.out_buffer[0])
        logging.debug('sto svuotando il buffer')
        # sistemare eventuale errore NoneType su out_buffer
        if sent >= len(self.out_buffer[0]):
            self.out_buffer.pop(0)
        else:
            self.out_buffer[0] = self.out_buffer[0][sent:]

##  metodo per chiudere il canale
    def handle_close(self):
        logging.debug('sto uscendo dal canale')
        self.close()

