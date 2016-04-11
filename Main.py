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
global superNodo

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
                '''
                msgRet = 'AQUE'
                # Prendo i campi del messaggio ricevuto
                pkID = fields[0]
                ipDest = fields[1]
                portDest = fields[2]
                ttl = fields[3]
                name = fields[4]

                # Controllo se il packetId è già presente se è presente non rispondo alla richiesta
                # E non la rispedisco
                if database.checkPkt(pkID)==False:
                    database.addPkt(pkID)
                    # Esegue la risposta ad una query
                    msgRet = msgRet + pkID
                    ip = Utility.MY_IPV4 + '|' + Utility.MY_IPV6
                    port = '{:0>5}'.format(Utility.PORT)
                    msgRet = msgRet + ip + port
                    l = database.findMd5(name.strip(' '))
                    for i in range(0, len(l)):
                        f = database.findFile(l[i][0])
                        r = msgRet
                        r = r + l[i][0] + str(f[0][0]).ljust(100, ' ')
                        t1 = Sender(r, ipDest, portDest)
                        t1.run()

                    # controllo se devo divulgare la query
                    if int(ttl) >= 1:
                        ttl='{:0>2}'.format(int(ttl)-1)
                        msg="QUER"+pkID+ipDest+portDest+ttl+name
                        lista=database.listClient()
                        if len(lista)>0:
                            t2 = SenderAll(msg, lista)
                            t2.run()
                '''

            elif command=="AQUE":
                # TODO implementare metodo aque
                '''pkID = fields[0]
                if database.checkPkt(pkID)==True and fields[3] not in listFindFile:
                    global numFindFile
                    numFindFile+=1
                    ipServer = fields[1]
                    portServer = fields[2]
                    md5file = fields[3]
                    filename = str(fields[4]).strip()
                    listFindFile.append(fields)
                    print(str(numFindFile) + " " + ipServer + " " + md5file + " " + filename)'''

            # Gestisco arrivo pacchetto supre
            elif command=="SUPE":
                pkID=fields[0]
                if database.checkPkt(pkID)==False:
                    database.addPkt(pkID)
                    #se sono un supernodo rispondo con asup
                    if superNodo:
                        ip=Utility.MY_IPV4+"|"+Utility.MY_IPV6
                        port='{:0>5}'.format(Utility.PORT)
                        msgRet="ASUP"+pkID+ip+port
                        t=Sender(msgRet,fields[1],fields[2])
                        t.run()

                    #decremento il ttl e controllo se devo inviare
                    # TODO la SUPE va divulgata ai supernodi e ai peer
                    # TODO divulgare la SUPE
                    '''
                    ttl = int(fields[3])-1
                    if ttl > 0:
                        ttl='{:0>2}'.format(ttl)
                        msg="SUPE"+pkID+fields[1]+fields[2]+ttl

                        lista=database.listClient()
                        if len(lista)>0:
                            t1 = SenderAll(msg,lista )
                            t1.run()'''

            elif command=="ASUP":
                pkID=fields[0]
                ip=fields[1]
                port=fields[2]
                if database.checkPkt(pkID)==True:
                    database.addSuperNode(ip,port)

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
database = ManageDB()
# TODO completare con la lista dei near iniziali
database.addClient(ip="172.030.007.001|fc00:0000:0000:0000:0000:0000:0007:0001",port="3000")
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
        print("1. Visualizza Peer")
        print("2. Visualizza File")
        print(" ")
        sel=input("Inserisci il numero del comando da eseguire ")
        if sel=='1':
            True
            # TODO visualizzare elenco peer connessi
        elif sel=='2':
            True
            # TODO visualizzare elenco file caricati ne supernodo

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
        print(" ")
        sel=input("Inserisci il numero del comando da eseguire ")
        if sel=='1':
            True
            # TODO ricerca supernodo e login al supernodo selezionato
        elif sel=='2':
            True
            # TODO aggiugi un file al supernodo
        elif sel=='3':
            True
            # TODO rimuovi un file dal supernodo
        elif sel=='4':
            True
            # TODO ricerca di un file al supernodo
        elif sel=='5':
            True
            # TODO logout dal supernodo


# i = db.findFile(md5="1"*32)
# print("valore i: "+i[0][0])

#if not os.path.exists(pathDir):
#    os.makedirs(pathDir)

'''
while True:
    print("1. Ricerca")
    print("2. Aggiorna Vicini")
    print("3. Aggiungi File")
    print("4. Rimuovi File")
    print("5. Visualizza File")
    print("6. Visualizza Vicini")
    print("7. Aggiungi Vicino")
    print(" ")
    sel=input("Inserisci il numero del comando da eseguire ")
    if sel=="1":
        sel=input("Inserisci stringa da ricercare ")
        while len(sel)>20:
            sel=input("Stringa Troppo Lunga,reinserisci ")
        pktID=Utility.generateId(16)
        ip=Utility.MY_IPV4+'|'+Utility.MY_IPV6
        port='{:0>5}'.format(Utility.PORT)
        ttl='{:0>2}'.format(5)
        search=sel.ljust(20,' ')
        msg="QUER"+pktID+ip+port+ttl+search
        database.addPkt(pktID)
        numFindFile = 0
        listFindFile = []
        lista=database.listClient()
        if len(lista)>0:
            t1 = SenderAll(msg, lista)
            t1.run()

        # Visualizzo le possibili scelte
        print("Scelta  PEER                                                        MD5                       Nome")

        # Chiedo quale file scaricare
        i = -1
        while i not in range(0, numFindFile +1):
            i = int(input("Scegli il file da scaricare oppure no (0 Non scarica nulla)\n"))
            if database.checkPkt(pktID) == False:
                break

        if numFindFile == 0:
            print ("Nessun risultato di ricerca ricevuto")

        elif i > 0:
            i = i - 1;
            ipp2p = listFindFile[i][1]
            pp2p = listFindFile[i][2]
            md5file = listFindFile[i][3]
            filename = str(listFindFile[i][4]).strip()

            try:
                t1 = Downloader(ipp2p, pp2p, md5file, filename)
                t1.run()
            except Exception as e:
                print(e)

    elif sel=="2":
        listaNear=database.listClient()
        if len(listaNear)>0:
            pktID=Utility.generateId(16)
            ip=Utility.MY_IPV4+'|'+Utility.MY_IPV6
            port='{:0>5}'.format(Utility.PORT)
            ttl='{:0>2}'.format(2)
            msg="NEAR"+pktID+ip+port+ttl
            database.addPkt(pktID)
            database.removeAllClient()
            t1 = SenderAll(msg, listaNear)
            t1.run()

    elif sel=="3":

        # Rimuovo i file presenti al momento nel database
        database.removeAllFile()

        #Ottengo la lista dei file dalla cartella corrente
        lst = os.listdir(Utility.PATHDIR)

        #Inserisco i file nel database
        if len(lst) > 0:
            for file in lst:
                database.addFile(Utility.generateMd5(Utility.PATHDIR+file), file)
            print("Operazione completata")
        else:
            print("Non ci sono file nella directory")

    elif sel=="4":

        # Ottengo la lista dei file dal database
        lst = database.listFile()

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
            database.removeFile(lst[i][0])
            print("Operazione completata")
        else:
            print("Non ci sono file nel database")

    elif sel=="5":

        # Ottengo la lista dei file dal database
        lst = database.listFile()

        # Visualizzo la lista dei file
        if len(lst) > 0:
            print("MD5                                        Nome")
            for file in lst:
                print(file[0] + " " + file[1])
        else:
            print("Non ci sono file nel database")

    elif sel=="6":
        lista=database.listClient()
        print(" ")
        print("IP e PORTA")
        for i in range(0,len(lista)):
            print("IP"+str(i)+" "+lista[i][0]+" "+lista[i][1])

    elif sel=="7":
        sel=input("Inserici Ipv4 ")
        t=sel.split('.')
        ipv4=""
        ipv4=ipv4+'{:0>3}'.format(t[0])+'.'
        ipv4=ipv4+'{:0>3}'.format(t[1])+'.'
        ipv4=ipv4+'{:0>3}'.format(t[2])+'.'
        ipv4=ipv4+'{:0>3}'.format(t[3])+'|'
        sel=input("Inserici Ipv6 ")
        t=sel.split(':')
        ipv6=""
        ipv6=ipv6+'{:0>4}'.format(t[0])+':'
        ipv6=ipv6+'{:0>4}'.format(t[1])+':'
        ipv6=ipv6+'{:0>4}'.format(t[2])+':'
        ipv6=ipv6+'{:0>4}'.format(t[3])+':'
        ipv6=ipv6+'{:0>4}'.format(t[4])+':'
        ipv6=ipv6+'{:0>4}'.format(t[5])+':'
        ipv6=ipv6+'{:0>4}'.format(t[6])+':'
        ipv6=ipv6+'{:0>4}'.format(t[7])
        sel=input("Inserici Porta ")
        port='{:0>5}'.format(int(sel))
        ip=ipv4+ipv6
        database.addClient(ip,port)
    else:
        print("Commando Errato, attesa nuovo comando ")
'''

