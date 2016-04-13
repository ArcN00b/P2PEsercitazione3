import re

# Classe che implementa i metodi per eseguire controlli e suddivisioni del messaggio ricevuto
class Parser:

    # Metodo statico che si occupa di suddividere i vari campi di data in modo consono
    @staticmethod
    def parse(data):

        # Inizializzo il contenitore dei vari campi
        fields = {}

        # Prendo i primi 4 caratteri maiuscoli all'interno di data e li inserisco in command
        command = data[0:4]

        # Parsing SUPE
        if command == 'SUPE':
            fields[0] = data[4:20]      # PKTID[16B]
            fields[1] = data[20:75]     # IPP2P[55B]
            fields[2] = data[75:80]     # PP2P[5B]
            fields[3] = data[80:82]     # TTL[2B]

        # Parsing ASUP
        elif command == 'ASUP':
            fields[0] = data[4:20]      # PKTID[16B]
            fields[1] = data[20:75]     # IPP2P[55B]
            fields[2] = data[75:80]     # PP2P[5B]

        # Parsing LOGI
        elif command == 'LOGI':
            fields[0] = data[4:59]      # IPP2P[55B]
            fields[1] = data[59:64]     # PP2P[5B]

        # Parsing ALGI
        elif command == 'ALGI':
            fields[0] = data[4:20]      # SessionID[16B]

        # Parsing ADFF
        elif command == 'ADFF':
            fields[0] = data[4:20]      # SessionID[16B]
            fields[1] = data[20:52]     # MD5[32B]
            fields[2] = data[52:152]    # FileName[100B]

        # Parsing DEFF
        elif command == 'DEFF':
            fields[0] = data[4:20]      # SessioID[16B]
            fields[1] = data[20:52]     # MD5[32B]

        # Parsing LOGO
        elif command == 'LOGO':
            fields[0] = data[4:20]      # SessionID[16B]

        # Parsing ALOG
        elif command == 'ALGO':
            fields[0] = data[4:7]       # Num Delete[3B]

        # Parsing QUER
        elif command == 'QUER':
            fields[0] = data[4:20]      # PKTID[16B]
            fields[1] = data[20:75]     # IPP2P[55B]
            fields[2] = data[75:80]     # PP2P[5B]
            fields[3] = data[80:82]     # TTL[2B]
            fields[4] = data[82:102]    # Ricerca[20B]

        # Parsing AQUE
        elif command == 'AQUE':
            fields[0] = data[4:20]      # PKTID[16B]
            fields[1] = data[20:75]     # IPP2P[55B]
            fields[2] = data[75:80]     # PP2P[5B]
            fields[3] = data[80:112]    # MD5[32B]
            fields[4] = data[112:212]   # FileName[100B]

        elif command == 'FIND':
            fields[0] = data[4:20]      # SessioID[16B]
            fields[1] = data[-20:]      # Ricerca[20B]

        elif command == 'AFIN':
            fields[0] = data[4:7]       # Num idm5[3B]

        # Parsing RETR
        elif command == 'RETR':
            fields[0] = data[4:36]  # MD5[32B]

        # Parsing ARET
        elif command == 'ARET':
            fields[0] = data[4:10] #Num Chunk

        # Se questo else viene eseguito significa che il comando ricevuto non e previsto
        else:
            print('Errore durante il parsing del messaggio\n')

        # Eseguo il return del comando e dei campi del messaggio
        return command, fields


'''
    # Metodo statico che controlla la corretta formattazione del parametro data
    @staticmethod
    def check(data):

        # Inizializzo la lista di comandi e un flag degli errori
        command_list = ['QUER', 'AQUE', 'NEAR', 'ANEA', 'RETR', 'ARET']
        error = False

        # Controllo che il comando sia effettivamente tra quelli riconosciuti
        command = data[0:4]
        if command not in command_list:
            error = True
            print('Errore, comando (' + command + ') non riconosciuto \n')

        # Se il comando e QUER eseguo questi controlli tramite regex
        if command == 'QUER' and not error:
            p = re.compile('[\dA-Z]{16}(\d{3}\.){3}\d{3}\|([\da-fA-F]{4}\:){7}[\da-fA-F]{4}\d{5}\d{2}[\da-zA-Z\.\ ]{20}$')
            if p.search(data) == None:
                error = True

        # Se il comando e AQUE eseguo questi controlli tramite regex
        elif command == 'AQUE' and not error:
            p = re.compile('[\dA-Z]{16}(\d{3}\.){3}\d{3}\|([\da-fA-F]{4}\:){7}[\da-fA-F]{4}\d{5}[\da-zA-Z]{32}[\da-zA-Z\.\ ]{100}$')
            if p.search(data) == None:
                error = True

        # Se il comando e NEAR eseguo questi controlli tramite regex
        elif command == 'NEAR' and not error:
            p = re.compile('[\dA-Z]{16}(\d{3}\.){3}\d{3}\|([\da-fA-F]{4}\:){7}[\da-fA-F]{4}\d{5}\d{2}$')
            if p.search(data) == None:
                error = True

        # Se il comando e ANEA eseguo questi controlli tramite regex
        elif command == 'ANEA' and not error:
            p = re.compile('[\dA-Z]{16}(\d{3}\.){3}\d{3}\|([\da-fA-F]{4}\:){7}[\da-fA-F]{4}\d{5}$')
            if p.search(data) == None:
                error = True

        # Se il comando e RETR eseguo questi controlli tramite regex
        elif command == 'RETR' and not error:
            p = re.compile('[\da-zA-Z]{32}$')
            if p.search(data) == None:
                error = True

        # Se il comando e ARET suddivido data in questo modo
        elif command == 'ARET' and not error:
            p = re.compile('\d{6}')
            if p.search(data) == None:
                error = True

        # Se questo else viene eseguito significa che il comando ricevuto non e previsto
        if not error:
            print('Il messaggio e ben formattato\n')
        else:
            print('Errore' + data + '\n')

    '''
'''
# Testing
from Parser import *

ip='127.000.000.001|fc00:0000:0000:0000:0000:0000:0007:0001'
id='1234567890123456'
port='03000'
ttl='99'
md5='00000000000000001234567890123456'
ricerca='pippo'+' '*(20-len('pippo'))
name='paperino'+' '*(100-len('paperino'))

# Check Supe
comand,campi=Parser.parse("SUPE"+id+ip+port+ttl)
#Check asup
comand,campi=Parser.parse("ASUP"+id+ip+port)
#Check logi
comand,campi=Parser.parse("LOGI"+ip+port)
#Check alog
comand,campi=Parser.parse("ALGI"+id)
#Check Adff
comand,campi=Parser.parse("ADFF"+id+md5+name)
#Check deff
comand,campi=Parser.parse("DEFF"+id+md5)
#Check LOGO
comand,campi=Parser.parse("LOGO"+id)
#check ALOG
comand,campi=Parser.parse("ALGO001")
#check QUER
comand,campi=Parser.parse("QUER"+id+ip+port+ttl+ricerca)
# check AQUE
comand,campi=Parser.parse("AQUE"+id+ip+port+md5+name)

True
True
'''
