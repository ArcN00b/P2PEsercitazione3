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

        if len(data) > 0:
            # converto i comandi
            command, fields = Parser.parse(data.decode())

            if command == "RETR":
                # TODO controllare coerenza con nuovi metodi
                # Imposto la lunghezza dei chunk e ottengo il nome del file a cui corrisponde l'md5
                chuncklen = 512
                peer_md5 = fields[0]
                # TODO cambiato questo metodo perche il database e cambiato
                obj = Utility.database.findFile(Utility.sessionId,peer_md5)

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

                    # Finchè il file non termina
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

            elif command == "QUER":
                # TODO implementare metodo QUER
                True

            elif command=="AQUE":
                # TODO implementare metodo ricezione AQUE
                True

            #Procedura LOGI
            elif command=='LOGI':
                if Utility.superNodo:
                    ip=fields[0]
                    port=fields[1]
                    try:
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
                    t.run()

            # Procedura ALGI
            elif command=='ALGI':
                if not Utility.superNodo:
                    s='0'*16
                    ssID=fields[0]
                    if ssID==s:
                        Utility.ipSuperNodo=''
                        Utility.portSuperNodo=''
                    else:
                        Utility.sessionId=ssID

            #Procedura ADFF
            elif command=='ADFF':
                if Utility.superNodo:
                    ssID=fields[0]
                    md5=fields[1]
                    name=fields[2]
                    l=Utility.database.findPeer(ssID,'','',2)
                    if len(l)>0:
                        Utility.database.addFile(ssID,name,md5)

            # Procedura DEFF
            elif command=='DEFF':
                if Utility.superNodo:
                    ssID=fields[0]
                    md5=fields[1]
                    l=Utility.database.findPeer(ssID,'','',2)
                    if len(l)>0:
                        Utility.database.removeFile(ssID,md5)

            # Procedura LOGO
            elif command=='LOGO':
                if Utility.superNodo:
                    ssID=fields[0]
                    l=Utility.database.findPeer(ssID,'','',2)
                    if len(l)>0:
                        ip=l[0][0]
                        port=l[0][1]
                        canc=Utility.database.removeAllFileForSessionId(ssID)
                        msgRet='ALGO'+'{:0>3}'.format(canc)
                        t=Sender(msgRet,ip,port)

            # Procedura ALGO
            elif command=='ALGO':
                if not Utility.superNodo:
                    delete=fields[0]
                    Utility.sessionId=''
                    Utility.ipSuperNodo=''
                    Utility.portSuperNodo=''
                    print('Logout effetuato, cancellati: '+delete)

            # Gestisco arrivo pacchetto supe
            elif command=="SUPE":
                pkID=fields[0]
                if Utility.database.checkPkt(pkID)==False:
                    Utility.database.addPkt(pkID)
                    # Se sono un supernodo rispondo con asup
                    if Utility.superNodo:
                        ip=Utility.MY_IPV4+"|"+Utility.MY_IPV6
                        port='{:0>5}'.format(Utility.PORT)
                        msgRet="ASUP"+pkID+ip+port
                        t=Sender(msgRet,fields[1],fields[2])
                        t.run()
                    # Decremento il ttl e controllo se devo inviare
                    ttl = int(fields[3])-1
                    if ttl > 0:
                        ttl='{:0>2}'.format(ttl)
                        msg="SUPE"+pkID+fields[1]+fields[2]+ttl
                        listaP=Utility.database.listPeer()
                        if len(listaP)>0:
                            tP = SenderAll(msg,listaP)
                            tP.run()
                        listaS=Utility.database.listSuperNode()
                        if len(listaS)>0:
                            tS = SenderAll(msg,listaS)
                            tS.run()

            elif command=="ASUP":
                pkID=fields[0]
                ip=fields[1]
                port=fields[2]
                if Utility.superNodo==True and Utility.database.checkPkt(pkID)==True:
                    Utility.database.addSuperNode(ip,port)
                else:
                    findPeer=False
                    for i in range(0,len(Utility.listFindSNode)):
                        if Utility.listFindSNode[i][1]==ip and Utility.listFindSNode[i][2]==port:
                            findPeer=True

                    if Utility.database.checkPkt(pkID)==True and findPeer:
                        global numFindSNode
                        numFindSNode+=1
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

