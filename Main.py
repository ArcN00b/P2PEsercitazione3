import queue
import sys
import os
import asyncore
import socket
import threading
from ManageDB import *
from Parser import *
from Utility import *
from Communication import *
from Server import *
from Utility import *
import os


ipv4, ipv6 = Utility.getIp(Utility.MY_IPV4 +"|" + Utility.MY_IPV6)
Server_Peer(ipv4, ipv6)

#faccio scegliere all'utente se e supernodo o meno
sel=input("Sei supernodo [s/n] ? ")
while not(sel=='s' or  sel=='n'):
    sel=input("Sei supernodo [s/n] ? ")

if sel=='s':
    #Sono un suprenodo
    Utility.superNodo=True
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
            Utility.database.addPkt(pktID)
            Utility.numFindSNode = 0
            Utility.listFindSNode = []

            # Invio la richiesta a tutti i Peer, cosi' reinoltrano la richiesta
            listaP=Utility.database.listPeer()
            if len(listaP)>0:
                tP = SenderAll(msg, listaP)
                tP.run()

            # Invio la richiesta a tutti i SuperNodi
            listaS=Utility.database.listSuperNode()
            if len(listaS)>0:
                tS = SenderAll(msg, listaS)
                tS.run()
        # Visualizza File del supernodo
        elif sel=='2':
            # Ottengo la lista dei file dal database
            lst = Utility.database.listFile()

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
    Utility.superNodo=False
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
            Utility.database.addPkt(pktID)
            Utility.numFindSNode = 0
            Utility.listFindSNode = []

            # Invio la richiesta a tutti i Peer, cosi' reinoltrano la richiesta
            listaP=Utility.database.listPeer()
            if len(listaP)>0:
                tP = SenderAll(msg, listaP)
                tP.run()

            # Invio la richiesta a tutti i SuperNodi
            listaS=Utility.database.listSuperNode()
            if len(listaS)>0:
                tS = SenderAll(msg, listaS)
                tS.run()

            # Visualizzo le possibili scelte
            print("Scegli il supernodo a cui vuoi collegarti")

            i = -1
            while i not in range(0, Utility.numFindSNode +1):
                i = int(input("Scegli il supernodo a cui vuoi collegarti\n"))
                if Utility.database.checkPkt(pktID) == False:
                    break

            if Utility.numFindSNode == 0:
                print ("Nessun supernodo trovato")

            elif i > 0:
                i = i - 1;
                ipDest = Utility.listFindSNode[i][1]
                portDest = Utility.listFindSNode[i][2]
                msg="LOGI"+ip+port
                Utility.ipSuperNodo = ipDest
                Utility.portSuperNodo = portDest

                try:
                    t1 = Sender(msg, ipDest, portDest)
                    t1.start()
                except Exception as e:
                    print(e)

        #Aggiunta di un file
        elif sel=='2':
            #Controllo se ho un sessionId, quindi se sono loggato a un supernodo
            if Utility.sessionId!='':
                sel=input('Inserici nome file da aggiungere ')
                #genero md5
                md5=Utility.generateMd5(Utility.PATHDIR+sel)
                name=sel.ljust(100,' ')
                #Aggiungo il file al mio database
                Utility.database.addFile(Utility.sessionId,name,md5)
                #Creo il messaggio da inviare al supernodo
                msg='ADFF'+Utility.sessionId+md5+name
                t=Sender(msg,Utility.ipSuperNodo,int(Utility.portSuperNodo))
                t.start()
        # Rimozione di un file
        elif sel=='3':
            #Controllo se ho un sessionId, quindi se sono loggato a un supernodo
            if Utility.sessionId!='':
                # Ottengo la lista dei file dal database
                lst = Utility.database.listFileForSessionId(Utility.sessionId)

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
                    Utility.database.removeFile(Utility.sessionId,lst[i][0])
                    print("Operazione completata")
                else:
                    print("Non ci sono file nel database")
                    True

                #genero il messaggio da mandare al supernodo con il file eliminato
                md5=lst[i][0]
                name=lst[i][1]
                msg='DEFF'+Utility.sessionId+md5+name
                t=Sender(msg,Utility.ipSuperNodo,int(Utility.portSuperNodo))
                t.start()
        elif sel=='4':
            True
            # TODO ricerca di un file al supernodo
        elif sel=='5':
            #Controllo se ho un sessionId, quindi se sono loggato a un supernodo
            if Utility.sessionId!='':
                # genero e invio il messaggio di logout al supernodo
                msg='LOGO'+Utility.sessionId
                t=Sender(msg,Utility.ipSuperNodo,int(Utility.portSuperNodo))
                t.start()

        elif sel=='6':
            # Ottengo la lista dei file dal database
            lst = Utility.database.listFileForSessionId()

            # Visualizzo la lista dei file
            if len(lst) > 0:
                print("Scelta MD5                                        Nome")
                for i in range(0,len(lst)):
                    print(str(i) + "   " + lst[i][0] + " " + lst[i][1])
            else:
                print("Non ci sono file nel database")

        else:
            print("Commando Errato, attesa nuovo comando ")

