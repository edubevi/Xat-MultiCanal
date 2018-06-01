import sys
import socket
import threading
import signal
import pickle

class Client:
        
        # Definim el constructor de la classe client.
        def __init__(self, IP_server, Port, nick):
                self.nick_client = nick
                # Creem un socket que es comunicara via TCP.
                self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Conecta el socket a la IP i al Port passats per parametre.
                try:
                        self.socket_client.connect((str(IP_server), int(Port)))

                except:
                        print "No ha estat possible la conexio amb el servidor."
                        sys.exit()

                self.socket_client.send(self.nick_client)
                
                # Crea un thread que llegira els missatges que rebra del servidor continuament.
                missatge_rebut = threading.Thread(target=self.llegeix_missatge)
                # Definim els threads com a "daemon" per tal que el thread principal segueixi executant-se i no esperi a que finalitzin els seus threads.
                missatge_rebut.setDaemon(True)
                missatge_rebut.start()
                signal.signal(signal.SIGTSTP, self.handler) # Definim la funcio handler com a un fucnio del signal SIGTSP

                while 1:
                        try:
                                missatge = raw_input()
                                if missatge == 'help':
                                        print "CREA   'nom_canal'             -> Crea un nou canal"
                                        print "CANVIA 'nom_canal'             -> Canvia de canal."
                                        print "PRIVAT 'nom_usuari' 'missatge' -> Envia un missatge privat a un usuari del canal actual."
                                        print "MOSTRA_CANALS                  -> Mostra una llista dels canals qua hi han al servidor."
                                        print "MOSTRA_USUARIS                 -> Mostra tots els usuaris que hi han en el canal actual."
                                        print "MOSTRA_TOTS                    -> Mostra tots els usuaris que hi han al servidor."
                                        
                                else:
                                        self.envia_missatge(missatge)
                        except:
                                print "Tancant Client"
                                self.socket_client.close()
                                sys.exit()


        # Metode que llegira i imprimira per pantalla les dades que envii el servidor.        
        def llegeix_missatge(self):
                while 1:
                        try:
                                msg = self.socket_client.recv(1024)
                                if msg: print msg
                        except:
                                pass
                                
        # Metode que enviara el missatge passat per parametre al servidor.      
        def envia_missatge(self, msg):
                self.socket_client.send(msg)

        # Metode que captura els signal SIGSTP (Ctrl+Z)
        def handler(self, signal, frame):
                print "\nClient tancat per signal"
                self.socket_client.close()
                sys.exit()


# Programa Principal
if __name__ == "__main__":
        print "--- Client TCP ----\n"
        nom = raw_input("Entra el nick del client: ")
        server = raw_input("Entra la IP: ")
        port = int(input("Entra el PORT: "))
        print "\n"
        client1 = Client(server,port,nom)

