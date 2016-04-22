import queue
import sys
import os
import asyncore
import logging
import socket
import threading
import os
from ManageDB import *
from Parser import *
from Utility import *
from Communication import *
from Server import *
from Utility import *

logging.basicConfig(level=logging.DEBUG)

#faccio scegliere all'utente se e supernodo o meno
sel=input("Sei supernodo [s/n] ? ")
while sel not in ['s', 'n']:
    sel=input("Sei supernodo [s/n] ? ")

#se sono supernodo metto porta 80 e sessionId='0000000000000000'
#altrimenti metto porta 3000
if sel=='s':
    Utility.sessionId='0'*16
    Utility.superNodo=True
else:
    Utility.superNodo=False

ipv4, ipv6 = Utility.getIp(Utility.MY_IPV4 + "|" + Utility.MY_IPV6)
Server_Peer(ipv4, ipv6)

#MENU
while True:
    print("1. Connetti/Aggiorna a Supernodo")
    print("2. Aggiungi File")
    print("3. Rimuovi File")
    print("4. Ricerca File")
    print("5. Logout")
    print("6. Visualizza File")
    print("7. Aggiungi Supernodo")
    print("8. Visualizza Supernodi")
    if Utility.superNodo:
        print("9. Visualizza Peer")
    print(" ")
    sel=input("Inserisci il numero del comando da eseguire ")

    #Connessione a un supernodo, funziona solo se sei un peer
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
        listaP=Utility.database.listPeer(2)
        if len(listaP)>0:
            tP = SenderAll(msg, listaP)
            tP.run()

        # Invio la richiesta a tutti i SuperNodi
        listaS=Utility.database.listSuperNode()
        if len(listaS)>0:
            tS = SenderAll(msg, listaS)
            tS.run()

        if not Utility.superNodo:
            # Visualizzo le possibili scelte
            #print("Scegli il supernodo a cui vuoi collegarti")

            i = -1
            while i not in range(0, Utility.numFindSNode +1):
                i = int(input("Scegli il supernodo a cui vuoi collegarti\n"))
                if Utility.database.checkPkt(pktID) == False:
                    break

            if Utility.numFindSNode == 0:
                print ("Nessun supernodo trovato")

            elif i > 0:
                # LOGOUT
                if Utility.sessionId != '':
                    msg='LOGO'+Utility.sessionId
                    ts = SenderAndWait(msg,Utility.ipSuperNodo,int(Utility.portSuperNodo))
                    ts.run()
                    sock = ts.getSocket()
                    ## ricezione delle logout
                    tr = Receiver(sock=sock)
                    ## lunghezza ALGO = 4 + 3
                    data = tr.receive(len=7)
                    ts.close()
                    command, fields = Parser.parse(data.decode())
                    ## Azzero le variabili e stampo
                    delete = fields[0]
                    print('Logout effetuato, cancellati: ' + delete)
                    Utility.sessionId = ''

                # LOGIN
                i = i - 1;
                ipDest = Utility.listFindSNode[i][1]
                portDest = Utility.listFindSNode[i][2]
                msg="LOGI"+ip+port

                try:
                    ts = SenderAndWait(msg, ipDest, portDest)
                    ts.run()
                    sock = ts.getSocket()

                    tr = Receiver(sock=sock)
                    ## lunghezza algi 4 + 16
                    data = tr.receive(len=20)
                    ts.close()
                    command, fields = Parser.parse(data.decode())

                    if Utility.sessionId == '':
                        # controllo se ho ricevuto un sessionId valido se si lo salvo altrimenti no
                        s = '0' * 16
                        ssID = fields[0]
                        if ssID == s:
                            Utility.ipSuperNodo = ''
                            Utility.portSuperNodo = ''
                        else:
                            Utility.sessionId = ssID
                            Utility.ipSuperNodo = ipDest
                            Utility.portSuperNodo = portDest

                except Exception as e:
                    print(e)


        else:
            print("Operazione completata")

    #Aggiunta di un file
    elif sel=='2':
        #Controllo se ho un sessionId, quindi se sono loggato a un supernodo
        if Utility.sessionId!='':
            #prendo la lista dei file
            lst = os.listdir(Utility.PATHDIR)

            print("Numero File     Nome File")
            for i in range(0,len(lst)):
                print(str(i+1)+"    "+lst[i])

            i = -1
            while i not in range(0, len(lst)+1):
                i = int(input("Inserisci il numero del file da aggiungere "))

            fileScelto=i-1

            #genero md5
            md5=Utility.generateMd5(Utility.PATHDIR+lst[fileScelto])
            name=lst[fileScelto].ljust(100,' ')
            #Aggiungo il file al mio database
            Utility.database.addFile(Utility.sessionId,name,md5)
            #Controllo se devo inviare il messaggio di aggiunta al mio supernodo, se sono peer
            if not Utility.superNodo:
                #Creo il messaggio da inviare al supernodo
                msg='ADFF'+Utility.sessionId+md5+name
                ts = Sender(msg,Utility.ipSuperNodo,int(Utility.portSuperNodo))
                ts.run()
        else:
            print("Effettuare Login")

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
                    print(str(i+1) + "   " + lst[i][0] + " " + lst[i][1])

                # Chiedo quale file rimuovere
                i = -1
                while i not in range(0, len(lst)+1):
                    i = int(input("Scegli il file da cancellare "))

                fileScelto=i-1
                # Elimino il file
                Utility.database.removeFile(Utility.sessionId,lst[fileScelto][0])

                #Controllo se non sono supernodo, se si devo comunicare che ho cancellato il file
                if not Utility.superNodo:
                    #genero il messaggio da mandare al supernodo con il file eliminato
                    md5=lst[fileScelto][0]
                    name=lst[fileScelto][1]
                    msg='DEFF'+Utility.sessionId+md5+name
                    ts = Sender(msg,Utility.ipSuperNodo,int(Utility.portSuperNodo))
                    ts.run()
                    print("Operazione completata")
            else:
                print("Non ci sono file nel database")
        else:
            print("Effettuare Login")

    #Ricerca
    elif sel=='4':
        if Utility.sessionId != '':
            sel = input("Inserisci stringa da ricercare ")
            while len(sel) > 20:
                sel = input("Stringa Troppo Lunga,reinserisci ")
            search = sel.ljust(20, ' ')
            msg = "FIND" + Utility.sessionId + search
            Utility.listFindFile = []
            Utility.listFindPeer = []
            numFindFile = 0
            ts = SenderAndWait(msg, Utility.ipSuperNodo, int(Utility.portSuperNodo))
            ts.run()
            sock = ts.getSocket()

            # Aspetto la risposta della FIND
            tf = AFinder(sock)
            tf.run()
            ts.close()

            # Visualizzo le possibili scelte
            if len(Utility.listFindFile) == 0:
                print("Nessun risultato")
            else:
                print("Scelta MD5                                Nome")
                for i in range(0, len(Utility.listFindFile)):
                    print(str(i+1) + " " + Utility.listFindFile[i][0] + "   " + Utility.listFindFile[i][1])

                # Chiedo quale file scaricare
                sel = -1
                while sel not in range(0, len(Utility.listFindFile) + 1):
                    sel = int(input("Scegli il file da scaricare oppure no (0 Non scarica nulla) "))

                # Ora devo visualizzare da chi scaricare il file (ricordando che quanti peer ha ogni md5 e nella listFindFile)
                if sel > 0:
                    md5file = Utility.listFindFile[sel - 1][0]
                    filename = str(Utility.listFindFile[sel - 1][1]).strip()
                    end = sel - 1
                    begin = 0
                    if end != 0:
                        for i in range(0, end):
                            begin += Utility.listFindFile[i][2]

                    # Ora begin contiene l'indice di ListFindPeer in cui si trovano i peer che hanno quel md5 selezionato
                    print("Scelta IP                                                  Porta")
                    for i in range(0, Utility.listFindFile[end][2]):
                        print(str(i + 1) + " " + Utility.listFindPeer[begin + i][0] + "   " + str(Utility.listFindPeer[begin + i][1]))

                    # Chiedo quale file scaricare
                    sel = -1
                    while sel not in range(0, Utility.listFindFile[end][2] + 1):
                        sel = int(input("Scegli il file da scaricare oppure no (0 Non scarica nulla) "))

                    # Se la selezione e maggiore di 0 e quindi voglio scaricare
                    if sel > 0:
                        index = begin + sel - 1
                        ipp2p = Utility.listFindPeer[index][0]
                        pp2p = Utility.listFindPeer[index][1]

                        # Se l'ip scelto non è il proprio
                        if ipp2p != Utility.MY_IPV4 + "|" + Utility.MY_IPV6:
                            try:
                                td = Downloader(ipp2p, pp2p, md5file, filename)
                                td.run()
                            except Exception as e:
                                print(e)
                        else:
                            print("Non è possibile scaricare da se stessi")

        else:
            print("Effettuare Login")

    #logout, fuziona solo se sei un peer loggato
    elif sel=='5':
        #Controllo se ho un sessionId, quindi se sono loggato a un supernodo
        if Utility.sessionId!='':
            if not Utility.superNodo:
                # genero e invio il messaggio di logout al supernodo
                msg='LOGO'+Utility.sessionId
                ts = SenderAndWait(msg,Utility.ipSuperNodo,int(Utility.portSuperNodo))
                ts.run()
                sock = ts.getSocket()
                ## ricezione delle logout
                tr = Receiver(sock=sock)
                ## lunghezza ALGO = 4 + 3
                data = tr.receive(len=7)
                ts.close()
                command, fields = Parser.parse(data.decode())
                ## Azzero le variabili e stampo
                delete = fields[0]
                print('Logout effetuato, cancellati: ' + delete)
                Utility.sessionId = ''
            else:
                print("Sei un supernodo")
        else:
            print("Effettuare Login")

    #Visualizza file supernodo o peer
    elif sel=='6':
        #Controllo se sono supernodo, se lo sono stampo anche la colonna sessionId
        if Utility.superNodo:
            # Ottengo la lista dei file dal database
            lst = Utility.database.listFile()

            # Visualizzo la lista dei file
            if len(lst) > 0:
                print("SessionID        MD5                                        Nome")
                for i in range(0,len(lst)):
                    print(lst[i][0] + " " + lst[i][2]+" "+lst[i][1])

            else:
                print("Non ci sono file nel database")
        else:
            # Ottengo la lista dei file dal database
            lst = Utility.database.listFileForSessionId(Utility.sessionId)
            # Visualizzo la lista dei file
            if len(lst) > 0:
                print("MD5                                        Nome")
                for i in range(0,len(lst)):
                    print(lst[i][0] + " " + lst[i][1])
            else:
                print("Non ci sono file nel database")

    #Aggiorna supernodi
    elif sel=='8':
        if Utility.superNodo:
            print("Sei un supernodo")
        else:
            print("Sei un peer, connesso al supernodo "+Utility.ipSuperNodo+" "+Utility.portSuperNodo)
        print("Lista supernodi salvati")
        lst=Utility.database.listSuperNode()
        # Visualizzo la lista dei peer collegati
        if len(lst) > 0:
            print("IP                                                      Porta")
            for i in range(0,len(lst)):
                print(lst[i][0] + " " + lst[i][1])
        else:
            print("Non ci peer collegati")

    #Visualizza Peer
    elif sel=='9':
        if Utility.superNodo:
            lst=Utility.database.listPeer(1)
            # Visualizzo la lista dei peer collegati
            if len(lst) > 0:
                print("SessionID        IP                                                      Porta")
                for i in range(0,len(lst)):
                    print(lst[i][0] + " " + lst[i][2]+" "+lst[i][1])
            else:
                print("Non ci peer collegati")

    #Aggiungi supernodo al database
    elif sel=='7':
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
        Utility.database.addSuperNode(ip,port)

    else:
        print("Commando Errato, attesa nuovo comando ")

