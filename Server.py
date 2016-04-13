from ReceiveHandler import *
from Utility import *
import logging
import threading
import queue
import asyncore
import socket

class Server_Peer:

    def __init__(self,ipv4,ipv6):
        self.ipv4=ipv4
        self.ipv6=ipv6
        self.port=Utility.PORT                        # da sostituire con Utility.generatePort()
        self.stop_queue = queue.Queue(1)
        u1 = ReceiveServerIPV4(self.stop_queue,self.ipv4,self.port)
        self.server_thread = threading.Thread(target=u1)#crea un thread e gli assa l'handler per il server da far partire
        self.stop_queueIpv6 = queue.Queue(1)
        #u2 = ReceiveServerIPV6(self.stop_queueIpv6,self.ipv6,self.port)
        #self.server_threadIP6 = threading.Thread(target=u2)
        self.server_thread.start()#parte
        #self.server_threadIP6.start()


class ReceiveServerIPV4(asyncore.dispatcher):
    """Questa classe rappresenta un server per accettare i pacchetti
    degli altri peer."""
    def __init__(self, squeue, ip, port):
        asyncore.dispatcher.__init__(self)
        self.squeue = squeue
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)#crea socket ipv6
        self.set_reuse_addr()#riusa indirizzo, evita problemi indirizzo occupato
        self.bind((ip, port)) #crea la bind del mio ip e porta
        self.listen(5)# sta in ascolto di 5 persone max

    # definizione dell'accept delle connessioni in arrivo al server
    def handle_accepted(self, client, address):
        # client_info = client, address
        logging.debug('handle_accept() %s', address)
        ReceiveHandler(client, address)

    def __call__(self):
        try:
            asyncore.loop()
        except Exception as e:
            logging.debug(e)

    def handle_close(self):
        self.close()

class ReceiveServerIPV6(asyncore.dispatcher):
    """Questa classe rappresenta un server per accettare i pacchetti
    degli altri peer."""
    def __init__(self, squeue, ip, port):
        asyncore.dispatcher.__init__(self)
        self.squeue = squeue
        self.create_socket(socket.AF_INET6,socket.SOCK_STREAM)#crea socket ipv6
        self.set_reuse_addr()#riusa indirizzo, evita problemi indirizzo occupato
        self.bind((ip, port)) #crea la bind del mio ip e porta
        self.listen(5)# sta in ascolto di 5 persone max

    # definizione dell'accept delle connessioni in arrivo al server
    def handle_accepted(self, client, address):
        # client_info = client, address
        logging.debug('handle_accept() %s', address)
        ReceiveHandler(client, address)

    def __call__(self):
        try:
            asyncore.loop()
        except Exception as e:
            logging.debug(e)

    def handle_close(self):
        self.close()