import queue
import sys
import os
import asyncore
import socket
import threading
from ManageDB import *
from Parser import *
from Utility import *

global database
global numFindFile
global listFindFile
global numFindSNode
global listFindSNode

global superNodo # Indica se il programma in esecuzione e' un SuperNodo o un Peer
global ipSuperNodo # Indica l'ip del SuperNodo a cui il Peer e' collegato
global portSuperNodo # Indica la porta del SuperNodo a cui il Peer e' collegato
global sessionId # Indica il sessionId del Peer

class Peer:

    def __init__(self,ipv4,ipv6):
        self.ipv4=ipv4
        self.ipv6=ipv6
        self.port=Utility.PORT                        # da sostituire con Utility.generatePort()
        self.stop_queue = queue.Queue(1)
        u1 = ReceiveServerIPV4(self.stop_queue,self.ipv4,self.port,(3,self.ipv4,self.port))
        self.server_thread = threading.Thread(target=u1)#crea un thread e gli assa l'handler per il server da far partire
        self.stop_queueIpv6 = queue.Queue(1)
        u2 = ReceiveServerIPV6(self.stop_queueIpv6,self.ipv6,self.port,(3,self.ipv6,self.port))
        self.server_threadIP6 = threading.Thread(target=u2)
        self.server_thread.start()#parte
        self.server_threadIP6.start()


class ReceiveServerIPV4(asyncore.dispatcher):
    """Questa classe rappresenta un server per accettare i pacchetti
    degli altri peer."""
    def __init__(self, squeue, ip, port, data_t):
        asyncore.dispatcher.__init__(self)
        self.squeue = squeue
        self.data_t = data_t #max near, mio ip e mia porta
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)#crea socket ipv6
        self.set_reuse_addr()#riusa indirizzo, evita problemi indirizzo occupato
        self.bind((ip, port)) #crea la bind del mio ip e porta
        self.listen(5)# sta in ascolto di 5 persone max

    def handle_accepted(self, socket_peer, address_peer):
        handler = ReceiveHandler(socket_peer, address_peer, self.data_t)

    def __call__(self):
        while self.squeue.qsize() == 0:
            asyncore.loop(timeout=1, count=5)

class ReceiveServerIPV6(asyncore.dispatcher):
    """Questa classe rappresenta un server per accettare i pacchetti
    degli altri peer."""
    def __init__(self, squeue, ip, port, data_t):
        asyncore.dispatcher.__init__(self)
        self.squeue = squeue
        self.data_t = data_t #max near, mio ip e mia porta
        self.create_socket(socket.AF_INET6,socket.SOCK_STREAM)#crea socket ipv6
        self.set_reuse_addr()#riusa indirizzo, evita problemi indirizzo occupato
        self.bind((ip, port)) #crea la bind del mio ip e porta
        self.listen(5)# sta in ascolto di 5 persone

    def handle_accepted(self, socket_peer, address_peer):
        handler = ReceiveHandler(socket_peer, address_peer, self.data_t)

    def __call__(self):
        while self.squeue.qsize() == 0:
            asyncore.loop(timeout=1, count=5)

class ReceiveHandler(asyncore.dispatcher):

    def __init__(self, conn_sock, near_address, data):
        asyncore.dispatcher.__init__(self,conn_sock)
        self.dataRec = ''
        self.near_address = near_address
        self.data_tuple = data

    def response(self,data):
        # Metodo gestisce tutto
        print(data)
        print('\n\r')

        if len(data) > 0:
            # converto i comandi
            command, fields = Parser.parse(data.decode())

            if command == "RETR":
                # Imposto la lunghezza dei chunk e ottengo il nome del file a cui corrisponde l'md5
                chuncklen = 512
                peer_md5 = fields[0]
                obj = database.findFile(peer_md5)

                if len(obj) > 0:
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
                    self.send(mess)

                    # Apro il file in lettura e ne leggo una parte
                    f = open(filename, 'rb')
                    r = f.read(chuncklen)
                    i=0

                    # Finchè il file non termina
                    while len(r) > 0:

                        # Invio la lunghezza del chunk
                        print(i)
                        i=i+1
                        mess = str(len(r)).zfill(5).encode()
                        print(mess)
                        print(r)
                        print('\n')
                        self.send(mess+r)
                        #time.sleep(0.001)

                        # Invio il chunk
                        #mess = r
                        #print(mess)
                        #print('\n')
                        #self.send(mess)

                        # Proseguo la lettura del file
                        r = f.read(chuncklen)
                    # Chiudo il file
                    print(num_chunk)
                    f.close()
                    time.sleep(7)

            elif(command == "QUER"):
                # TODO implementare metodo quer
                True

            elif command=="AQUE":
                # TODO implementare metodo aque
                True

            #Procedura LOGI
            elif command=='LOGI':
                if superNodo:
                    ip=fields[0]
                    port=fields[1]
                    try:
                        l=database.findPeer('',ip,port,1)
                        if len(l)>0:
                            ssID=l[0][0]
                        else:
                            ssID=Utility.generateId(16)
                        database.addPeer(ssID,ip,port)
                    except Exception as e:
                        ssID='0'*16

                    msgRet='ALGI'+ssID
                    t=Sender(msgRet,ip,port)
                    t.run()

            # Procedura ALGI
            elif command=='ALGI':
                if not superNodo:
                    s='0'*16
                    ssID=fields[0]
                    if ssID==s:
                        global ipSuperNodo
                        global portSuperNodo
                        ipSuperNodo=''
                        portSuperNodo=''
                    else:
                        global sessionId
                        sessionId=ssID

            #Procedura ADFF
            elif command=='ADFF':
                if superNodo:
                    ssID=fields[0]
                    md5=fields[1]
                    name=fields[2]
                    l=database.findPeer(sessionId,'','',2)
                    if len(l)>0:
                        database.addFile(ssID,name,md5)

            # Procedura DEFF
            elif command=='DEFF':
                if superNodo:
                    ssID=fields[0]
                    md5=fields[1]
                    l=database.findPeer(ssID,'','',2)
                    if len(l)>0:
                        database.removeFile(ssID,md5)

            # Procedura LOGO
            elif command=='LOGO':
                if superNodo:
                    ssID=fields[0]
                    l=database.findPeer(ssID,'','',2)
                    if len(l)>0:
                        sessionId=''
                        canc=database.removeAllFileForSessionId(ssID)
                        msgRet='ALGO'+'{:0>3}'.format(canc)

            # Procedura ALGO
            elif command=='ALGO':
                if not superNodo:
                    delete=fields[0]
                    print('Logout effetuato, cancellati: '+delete)

            # Gestisco arrivo pacchetto supe
            elif command=="SUPE":
                pkID=fields[0]
                if database.checkPkt(pkID)==False:
                    database.addPkt(pkID)
                    # Se sono un supernodo rispondo con asup
                    if superNodo:
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
                        listaP=database.listPeer()
                        if len(listaP)>0:
                            tP = SenderAll(msg,listaP)
                            tP.run()
                        listaS=database.listSuperNode()
                        if len(listaS)>0:
                            tS = SenderAll(msg,listaS)
                            tS.run()

            elif command=="ASUP":
                pkID=fields[0]
                ip=fields[1]
                port=fields[2]
                if superNodo==True and database.checkPkt(pkID)==True:
                    database.addSuperNode(ip,port)
                else:
                    findPeer=False
                    for i in range(0,len(listFindSNode)):
                        if listFindSNode[i][1]==ip and listFindSNode[i][2]==port:
                            findPeer=True

                    if database.checkPkt(pkID)==True and findPeer:
                        global numFindSNode
                        numFindSNode+=1
                        listFindSNode.append(fields)
                        print(str(numFindSNode) + " " + ip + " " + port)



            else:
                print("ricevuto altro")

        self.close()


    # Questo e il metodo che viene chiamato quando ci sono delle recive
    def handle_read(self):

        # Ricevo i dati dal socket ed eseguo il parsing
        self.dataRec = self.recv(2048)
        # controllo lunghezza dati ricevuta
        #try:
        self.response(self.dataRec)
        #except Exception:
        #    self.response(self.dataRec)
        self.close()

    #def handle_error(self):
    #    self.response(self.dataRec)

numFindFile=0
listFindFile=[]
sessionId=''
ipSuperNodo=''
portSuperNodo=''
numFindSNode=0
listFindSNode=[]

database = ManageDB()
# TODO completare con la lista dei near iniziali
database.addSuperNode(ip="172.030.007.001|fc00:0000:0000:0000:0000:0000:0007:0001",port="3000")
#database.addClient(ip="172.030.007.001|fc00:0000:0000:0000:0000:0000:0007:0001",port="3000")
#database.addClient(ip="172.030.007.002|fc00:0000:0000:0000:0000:0000:0007:0002",port="3000")

#database.addFile("1"*32, "live brixton.jpg")

#faccio scegliere all'utente se e supernodo o meno
sel=input("Sei supernodo [s/n] ? ")
while not(sel=='s' or  sel=='n'):
    sel=input("Sei supernodo [s/n] ? ")

ipv4, ipv6 = Utility.getIp(Utility.MY_IPV4 +"|" + Utility.MY_IPV6)
p=Peer(ipv4,ipv6)

if sel=='s':
    #Sono un suprenodo
    superNodo=True
    # menu del supernodo
    while True:
        print("1. Ricerca Supernodi")
        print("2. Visualizza File")
        print(" ")
        sel=input("Inserisci il numero del comando da eseguire ")
        if sel=='1':
            pktID=Utility.generateId(16)
            ip=Utility.MY_IPV4+'|'+Utility.MY_IPV6
            port='{:0>5}'.format(Utility.PORT)
            ttl='{:0>2}'.format(4)
            msg="SUPE"+pktID+ip+port+ttl
            database.addPkt(pktID)
            numFindSNode = 0
            listFindSNode = []

            # Invio la richiesta a tutti i Peer, cosi' reinoltrano la richiesta
            listaP=database.listPeer()
            if len(listaP)>0:
                tP = SenderAll(msg, listaP)
                tP.run()

            # Invio la richiesta a tutti i SuperNodi
            listaS=database.listSuperNode()
            if len(listaS)>0:
                tS = SenderAll(msg, listaS)
                tS.run()

        elif sel=='2':
            # Ottengo la lista dei file dal database
            lst = database.listFile()

            # Visualizzo la lista dei file
            if len(lst) > 0:
                print("Scelta SessionID        MD5                                        Nome")
                for i in range(0,len(lst)):
                    print(str(i) + "   " + lst[i][0] + " " + lst[i][2]+" "+lst[i][1])

            else:
                print("Non ci sono file nel database")

        else:
            print("Commando Errato, attesa nuovo comando ")

else:
    #Non sono un peer
    superNodo=False
    print("Menu del peer")
    # menu del peer normale
    while True:
        print("1. Ricerca Supernodo")
        print("2. Aggiungi File")
        print("3. Rimuovi File")
        print("4. Ricerca File")
        print("5. Logout")
        print("6. Visualizza File")
        print(" ")
        sel=input("Inserisci il numero del comando da eseguire ")
        if sel=='1':
            pktID=Utility.generateId(16)
            ip=Utility.MY_IPV4+'|'+Utility.MY_IPV6
            port='{:0>5}'.format(Utility.PORT)
            ttl='{:0>2}'.format(4)
            msg="SUPE"+pktID+ip+port+ttl
            database.addPkt(pktID)
            numFindSNode = 0
            listFindSNode = []

            # Invio la richiesta a tutti i Peer, cosi' reinoltrano la richiesta
            listaP=database.listPeer()
            if len(listaP)>0:
                tP = SenderAll(msg, listaP)
                tP.run()

            # Invio la richiesta a tutti i SuperNodi
            listaS=database.listSuperNode()
            if len(listaS)>0:
                tS = SenderAll(msg, listaS)
                tS.run()

            # Visualizzo le possibili scelte
            print("Scegli il supernodo a cui vuoi collegarti")

            i = -1
            while i not in range(0, numFindSNode +1):
                i = int(input("Scegli il supernodo a cui vuoi collegarti\n"))
                if database.checkPkt(pktID) == False:
                    break

            if numFindSNode == 0:
                print ("Nessun supernodo trovato")

            elif i > 0:
                i = i - 1;
                ipDest = listFindSNode[i][1]
                portDest = listFindSNode[i][2]
                msg="LOGI"+ip+port
                ipSuperNodo = ipDest
                portSuperNodo = portDest

                try:
                    t1 = Sender(msg, ipDest, portDest)
                    t1.run()
                except Exception as e:
                    print(e)

        elif sel=='2':
            if sessionId!='':
                sel=input('Inserici nome file da aggiungere ')
                md5=Utility.generateMd5(Utility.PATHDIR+sel)
                name=sel.ljust(100,' ')
                database.addFile(sessionId,name,md5)
                msg='ADFF'+sessionId+md5+name
                t=Sender(msg,ipSuperNodo,int(portSuperNodo))
                t.run()

        elif sel=='3':
            if sessionId!='':
                # Ottengo la lista dei file dal database
                lst = database.listFileForSessionId(sessionId)

                # Visualizzo la lista dei file
                if len(lst) > 0:
                    print("Scelta  MD5                                        Nome")
                    for i in range(0,len(lst)):
                        print(str(i) + "   " + lst[i][0] + " " + lst[i][1])

                    # Chiedo quale file rimuovere
                    i = -1
                    while i not in range(0, len(lst)):
                        i = int(input("Scegli il file da cancellare "))

                    # Elimino il file
                    database.removeFile(sessionId,lst[i][0])
                    print("Operazione completata")
                else:
                    print("Non ci sono file nel database")
                    True

                msg='DEFF'+sessionId+md5+name
                t=Sender(msg,ipSuperNodo,int(portSuperNodo))
                t.run()
        elif sel=='4':
            True
            # TODO ricerca di un file al supernodo
        elif sel=='5':
            msg='LOGO'+sessionId
            t=Sender(msg,ipSuperNodo,int(portSuperNodo))
            t.run()

        elif sel=='6':
            # Ottengo la lista dei file dal database
            lst = database.listFileForSessionId()

            # Visualizzo la lista dei file
            if len(lst) > 0:
                print("Scelta MD5                                        Nome")
                for i in range(0,len(lst)):
                    print(str(i) + "   " + lst[i][0] + " " + lst[i][1])

            else:
                print("Non ci sono file nel database")

        else:
            print("Commando Errato, attesa nuovo comando ")



