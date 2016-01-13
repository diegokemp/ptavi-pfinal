from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import socketserver
import sys
from XMLHandler import XMLHandler
import time
import json
import random
import hashlib

class proxyxml():

    def __init__(self, fichero):

        parser = make_parser()
        cHandler = XMLHandler()
        parser.setContentHandler(cHandler)
        try:
            parser.parse(open(fichero))
        except FileNotFoundError:
            print("->Fichero xml no encontrado")

        self.diccionario = cHandler.get_tags()

class ProxySIPHandler(socketserver.DatagramRequestHandler):
    dicc = {}
    diccpass = {}

    def json2passwd(self, archivojson):
        archivo = open(archivojson, "r")
        self.diccpass = json.load(archivo)

    def json2registered(self, archivojson):
        archivo2 = open(archivojson, "r")
        self.dicc = json.load(archivo2)

    def caduca(self, actual):
        dicc2 = self.dicc.copy()
        for key in dicc2.keys():
            if (dicc2[key][1]) < actual:
                del self.dicc[key]
                print("---->Usuario CADUCADO")

    def register2json(self, nombre):
        archivo = open(nombre, "w")
        datjson = json.dump(self.dicc, archivo)

    def passwd2json(self, nombre):
        archivo = open(nombre, "w")
        datjson2 = json.dump(self.diccpass, archivo)

    def handle(self):
        archivojson = self.diccionario["datapath"]
        archivopass = self.diccionario["datapass"]
        self.json2registered(archivojson)
        self.json2passwd(archivopass)
        curr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.caduca(curr)
        self.register2json(archivojson)
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            lineutf = line.decode('utf-8')
            if lineutf != "":
                method = lineutf.split(" sip:")
                if method[0]=="REGISTER":
                    tracker = lineutf.split("Expires: ")
                    tracker = tracker[1].split("\r\n")
                    expires = tracker[0]
                    exp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + float(expires)))
                    emi_usr = lineutf.split(":")
                    emi_usr = emi_usr[1]
                    if expires != "0":
                        if tracker[1] != "":
                            response = tracker[1].split("response=")
                            response = response[1]
                            print(response)
                            passwd = self.diccpass[emi_usr][1]
                            passwdb = (bytes(passwd, 'utf-8'))
                            nonce = self.diccpass[emi_usr][0]
                            print(nonce)
                            nonceb = (bytes(nonce, 'utf-8'))

                            m = hashlib.md5()
                            m.update(passwdb + nonceb)
                            response2 = m.hexdigest()
                            print(response2)
                            if response == response2:
                                print("->Register autorizado")

                                portsereg = lineutf.split(" SIP/2.0")
                                portsereg = portsereg[0].split(":")
                                portsereg = portsereg[2]

                                self.dicc[emi_usr] = [portsereg, exp]
                                self.register2json(archivojson)
                                register_resp = (b"SIP/2.0 200 OK\r\n\r\n")
                                print("    Enviando 200 OK")
                            else:
                                print("---->Response no valido")
                        else:
                            print("->Register no autorizado")
                            print("    Creando nonce")
                            print(self.diccpass)
                            self.diccpass[emi_usr][0] = str(random.randint(100000000000000,999999999999999))
                            self.passwd2json(archivopass)
                            print(self.diccpass[emi_usr][0])
                            nonce = self.diccpass[emi_usr][0]
                            register_resp = (b"SIP/2.0 401 Unauthorized\r\n" + \
                                        b"WWW Authenticate: nonce=" + bytes(nonce,'utf-8'))
                            print("    Enviando nonce...")
                        self.wfile.write(register_resp)
                    else:
                        del self.dicc[emi_usr]
                        self.register2json(archivojson)
                        print("->Usuario borrado(expires = 0)")

                elif method[0]=="INVITE":
                    print("->Recibido: INVITE")
                    isregistered = lineutf.split("o=")
                    isregistered = isregistered[1].split(" ")
                    isregistered = isregistered[0]
                    for key in self.dicc.keys():
                        if key == isregistered:
                            print("    Usuario encontrado")
                            rec_usr = lineutf.split(":")
                            rec_usr = rec_usr[1].split(" ")
                            rec_usr = rec_usr[0]
                            rec_port = self.dicc[rec_usr][0]
                            #puertobuscar por @
                            mensaje = lineutf
                            print("->Enviando INVITE")
                            my_socket.connect(("127.0.0.1", int(rec_port)))
                            my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
                            print("    Esperando respuesta...")
                            data = my_socket.recv(1024)
                            respuesta = data.decode('utf-8')
                            resp = respuesta.split(" ")
                            if resp[1] == "100":
                                print("->Recibido: 100 Trying")
                                if resp[3] == "180":
                                    print("->Recibido: 180 Ring")
                                    if resp[5] == "200":
                                        print("->Recibido: 200 OK")

                                        mensaje = lineutf
                                        print("->Enviando 100 180 200")
                                        self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                                        self.wfile.write(b"SIP/2.0 180 Ring\r\n\r\n")
                                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")

                elif method[0]=="ACK":
                    print("Recibido: ACK")
                    mensaje = lineutf
                    print("->Enviando ACK")
                    my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
                elif method[0]=="BYE":
                    print("Recibido: BYE")
                    rec_usr = lineutf.split(":")
                    rec_usr = rec_usr[1].split(" ")
                    rec_usr = rec_usr[0]
                    rec_port = self.dicc[rec_usr][0]
                    mensaje = lineutf
                    print("->Enviando BYE")
                    my_socket.connect(("127.0.0.1", int(rec_port)))
                    my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
                    print("    Esperando respuesta...")
                    data = my_socket.recv(1024)
                    respbye = data.decode('utf-8')
                    if respbye == "":
                        data = my_socket.recv(1024)
                        respbye = data.decode('utf-8')
                    respbye = respbye.split(" ")
                    if respbye[1] == "200":
                        print("->Recibido 200 OK")
                        print("->Enviando 200 OK")
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")

            if not line:
                break

if __name__ == "__main__":
    try:
        XML = sys.argv[1]
    except:
        print("Usage: python3 proxy_registrar.py <file.xml>")
    proxyobj = proxyxml(XML)
    ProxySIPHandler.diccionario = proxyobj.diccionario
    proxyname = proxyobj.diccionario["servname"]
    proxyport = proxyobj.diccionario["servport"]
    proxyip = proxyobj.diccionario["servip"]
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv = socketserver.UDPServer((proxyip, int(proxyport)), ProxySIPHandler)

    print("Server " + proxyname + " listening at port " + proxyport + "...")
    serv.serve_forever()
