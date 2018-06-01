# -*- coding: utf-8 -*-

import socket
import threading
import sys

class Servidor:
    # Definim contructor de la classe Servidor
    def __init__(self, IP_client="localhost", Port=5555):
        print "/** SERVIDOR TCP **\ [IP:"+str(IP_client)+"|PORT:"+str(Port)+"]"
        print "¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨\n"
        self.clients = {} # Diccionari que associa un client amb el seu socket de conexio respectiu.
        self.canals = {"General": []}  # Diccionari que associa els canals amb els usuaris que hi han en cada canal. Per defecte, inicialitzem un canal General (o Canal de Benvinguda) on van a parar inicialment tots els usuaris que es conecten al servidor.
        # Crea un socket de tipus TCP
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Enllaçem la IP del client al port de benvinguda del servidor
        self.socket_server.bind((str(IP_client), int(Port)))
        # Maxim de clients que es podran conectar
        self.socket_server.listen(10)
        # Desactivem la propietat bloquejant del socket (lo que ens permet que el proces segueixi executant-se si el buffer del socket esta buit).
        self.socket_server.setblocking(False)
        # Creem dos threads que executaran constant junt amb el thread principal.
        accepta_entrants = threading.Thread(target=self.accepta_con) # Thread que gestionara l'acceptacio de les conexions entrants, assignacio de sockets... dels diferents clients que es conectin al servidor.
        gestiona_entrants = threading.Thread(target=self.gestiona_con) # Thread que gestionara la comunicacio entre servidor i clients.
        # Activa l'opcio d'executar els threads en mode 'Daemon'
        accepta_entrants.setDaemon(True)
        gestiona_entrants.setDaemon(True)
        # Inicia els threads
        accepta_entrants.start() 
        gestiona_entrants.start()
        print "[*INFO*] Entra help per veure la llista de cmd disponibles.\n" 

        # Thread Principal: Executa Servidor fins que s'entri la comanda exit.
        while 1:
            cmd = raw_input()
            if cmd == "exit":
                self.socket_server.close()
                sys.exit()
            elif cmd == "help": print " - exit ---> Tanca el programa servidor. \n"
            else: print "[*CONTROL*]-> Comanda Incorrecte"

                
    # Funcio que espera la conexio d'un client al socket de benvinguda i estableix un nou socket de conexio entre el servidor i el client. 
    def accepta_con(self):
        while 1:
            try: 
                socket_conexio, addr = self.socket_server.accept()
                nom_enviat = False
                usuari = ''
                # Espera a rebre el nom d'usuari del client.
                while nom_enviat == False:
                    nick = socket_conexio.recv(1024)
                    if nick:
                        nom_enviat = True
                        usuari = nick
                # Comprova si el usuari ja existeix al xat. Si es aixi tanca el socket de conexio.       
                if self.clients.has_key(usuari):
                    print "[*CONTROL*]-> S'ha denegat el socket de conexio al usuari "+usuari+". Nom d'usuari ja existent."
                    socket_conexio.send("[*SERVIDOR*]-> S'ha perdut la conexio. Nom d'usuari ja existent.")
                    socket_conexio.close()
                else:
                    socket_conexio.setblocking(False) # Socket no bloquejant
                    self.clients[usuari] = socket_conexio # afageix nou socket a llista de clients.
                    self.canals.get("General").append(usuari)
                    socket_conexio.send("[*SERVIDOR*]-> S'ha establert conexio amb el servidor. Benvingut al XAT TCP "+str(usuari)+"!!!\n[*SERVIDOR*]-> Entra help per veure les comandes disponibles.\n")
                    print "[*CONTROL*]-> S'ha assignat un socket de conexio al usuari "+usuari+" i s'ha afegit a la llista."
                    
            except:
                pass
            
    # Funcio que gestiona la recepcio i el enviament de missatges dels diferents clients. Tambe gestiona les comandes que envien els clients.
    def gestiona_con(self):
        while 1:
            if len(self.clients) > 0:
                for usuari in list(self.clients):
                    try:
                        missatge = self.clients[usuari].recv(1024) # Guarda a missatge el contingut del buffer del socket del usuari.
                        if missatge:
                            cmd = missatge.split() # Separa el missatge en 2 strings, un per la comanda i l'altre per l'argument (EX: CREA esports -> cmd[0] = CREA i cmd[1] = esports)
                            if cmd[0] == "CREA":
                                if len(cmd) != 2:
                                    self.clients[usuari].send("\n[*SERVIDOR*]-> No s'ha pogut crear el canal. Comanda incorrecte.")
                                else:
                                    # Comprova si ja existeix el canal
                                    if self.canals.has_key(cmd[1]):
                                        self.clients[usuari].send("\n[*SERVIDOR*]-> No s'ha pogut crear el canal. El canal ja existeix.")
                                    else:
                                        # Borra el usuari del canal que estava previament (Un usuari nomes pot estar en un canal).
                                        for i in self.canals.values():
                                            if usuari in i: i.remove(usuari)    
                                        self.canals[cmd[1]] = [usuari] # Crea el nou canal i afageix el usuari a la llista d'usuaris del canal
                                        self.clients[usuari].send("\n[*SERVIDOR*]-> Has creat el canal "+cmd[1]+"\n[*SERVIDOR*]-> Estas al canal "+cmd[1])
                                        print "\n[*CONTROL*]-> S'ha creat el canal "+cmd[1]+".\n"+str(self.canals)
                            elif cmd[0] == "CANVIA":
                                if len(cmd) != 2:
                                    self.clients[usuari].send("\n[*SERVIDOR*]-> No s'ha pogut canviar de canal. Comanda incorrecte.")
                                else:
                                    if self.canals.has_key(cmd[1]):
                                        # Borra al usuari del canal que estava.
                                        for i in self.canals.values():
                                            if usuari in i: i.remove(usuari)
                                        self.canals.get(cmd[1]).append(usuari) # Afageix el usuari a la llista d'usuaris del canal
                                        self.clients[usuari].send("[*SERVIDOR*]-> Estas al canal "+cmd[1])
                                        print "[*CONTROL*]-> Afegit usuari "+usuari+" al canal "+cmd[1]+".\n"+str(self.canals)
                                    else:
                                         self.clients[usuari].send("\n[*SERVIDOR*]-> El canal no existeix.")
                            elif cmd[0] == "MOSTRA_CANALS":
                                self.clients[usuari].send("\n** Llista Canals ** \n¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨\n"+str(self.canals.keys()))
                            elif cmd[0] == "MOSTRA_TOTS":
                                self.clients[usuari].send("\n** Llista Usuaris ** \n¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨\n"+str(self.canals.items()))
                            elif cmd[0] == "MOSTRA_USUARIS":
                                for i in self.canals.keys():
                                    if usuari in self.canals[i]: self.clients[usuari].send("\n** Llista Usuaris del canal "+str(i)+"** \n¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨\n"+str(self.canals[i]))
                            elif cmd[0] == "PRIVAT":
                                if len(cmd) < 3:
                                    self.clients[usuari].send("\n[*SERVIDOR*]-> No s'ha enviat el missatge privat. Comanda Incorrecta.")
                                else:
                                    # Busquem en els canals
                                    for i in self.canals.keys():
                                        #Comprovem que el emisor i el destinatari estiguin al mateix canal
                                        if usuari in self.canals[i]:
                                            if cmd[1] in self.canals[i]:
                                                m = missatge.split(cmd[0]+" "+cmd[1]) #separem del missatge enviat la cadena formada per la comanda i l'argument
                                                m = m[1].lstrip() # Eliminem espais en blanc de l'esquerra de la cadena
                                                self.envia_privat(usuari, cmd[1], m) # Envia el missatge privat
                                            else:
                                                self.clients[usuari].send("\n[*SERVIDOR*]-> No existeix el usuari "+cmd[1]+" en el canal.")
                                                break                                            
                            else:
                                self.envia_a_tots(usuari, missatge) 
                    except:
                        pass
                    
    # Envia missatge privat a un usuari.
    def envia_privat(self, emisor, desti, mssg):
        self.clients[desti].send("[PRIVAT|"+str(emisor)+"]-> "+str(mssg))

    # Metode que envia un missatge a tots els usuaris del mateix canal. 
    def envia_a_tots(self, emisor, mssg):
        for i in self.canals.keys():
            if emisor in self.canals[i]:
                for usr in self.canals[i]:
                    try:
                        if usr != emisor:
                            self.clients[usr].send("["+str(emisor)+"]-> "+str(mssg))
                    except:
                        del self.clients[usr] #si no pot enviar el missatge vol dir que el client s'ha desconectat i per tant es borra de la llista.
                break

# Programa Principal
if __name__ == "__main__": 
    servidor1 = Servidor()
