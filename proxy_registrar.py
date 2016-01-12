from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import socketserver
import sys
from XMLHandler import XMLHandler

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

    def json2registered(self):
        try:
            archivo2 = open("registered.json", "r")
            self.dicc = json.load(archivo2)
            #print(self.dicc)
        except FileNotFoundError:
            print("No se encontro dicho archivo...")

    def caduca(self, actual):
        dicc2 = self.dicc.copy()
        for key in dicc2.keys():
            if (dicc2[key][1]) < actual:
                del self.dicc[key]
                #print(self.dicc)

    def register2json(self, nombre):
        archivo = open(nombre, "w")
        datjson = json.dump(self.dicc, archivo)

    def handle(self):
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
                    # print(expires)
                    if expires != "0":
                        if tracker[1] != "":
                            print("->Register autorizado")
                            contraseña = tracker[1].split("response=")
                            contraseña = contraseña[1]
                            # print(contraseña)

                            emi_usr = lineutf.split(":")
                            emi_usr = emi_usr[1]
                            #añadir

                            portsereg = lineutf.split(" SIP/2.0")
                            portsereg = portsereg[0].split(":")
                            portsereg = portsereg[2]
                            print("portserv" + portsereg)
                            #añadir

                            register_resp = (b"SIP/2.0 200 OK\r\n\r\n")
                        else:
                            print("->Register no autorizado")

                            register_resp = (b"SIP/2.0 401 Unauthorized\r\n" + \
                                        b"WWW Authenticate: nonce=7777777777")
                        self.wfile.write(register_resp)
                    # else:
                        #borrar
                elif method[0]=="INVITE":
                    rec_usr = lineutf.split(":")
                    rec_usr = rec_usr[1].split(" ")
                    rec_usr = rec_usr[0]
                    #puertobuscar por @
                    mensaje = lineutf
                    my_socket.connect(("127.0.0.1", 5000))
                    my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')

                    data = my_socket.recv(1024)
                    respuesta = data.decode('utf-8')
                    resp = respuesta.split(" ")
                    if resp[1] == "100":
                        print("100--")
                        if resp[3] == "180":
                            print("180--")
                            if resp[5] == "200":
                                print("200 concatenado")

                                mensaje = lineutf

                                self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                                self.wfile.write(b"SIP/2.0 180 Ring\r\n\r\n")
                                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")

                elif method[0]=="ACK":
                    mensaje = lineutf
                    my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
                elif method[0]=="BYE":
                    rec_usr = lineutf.split(":")
                    rec_usr = rec_usr[1].split(" ")
                    rec_usr = rec_usr[0]
                    #buscar
                    mensaje = lineutf
                    my_socket.connect(("127.0.0.1", 5000))
                    my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')

                    data = my_socket.recv(1024)
                    respbye = data.decode('utf-8')
                    respbye = respbye.split(" ")
                    if respbye[1] == "200":
                        print("200")
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
            if not line:
                break

if __name__ == "__main__":
    try:
        XML = sys.argv[1]
    except:
        print("Usage: python3 server.py IP port audio_file")
    proxyobj = proxyxml(XML)
    ProxySIPHandler.diccionario = proxyobj.diccionario
    proxyname = proxyobj.diccionario["servname"]
    proxyport = proxyobj.diccionario["servport"]
    proxyip = proxyobj.diccionario["servip"]
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv = socketserver.UDPServer((proxyip, int(proxyport), ProxySIPHandler)

    print("Server " + proxyname + " listening at port " + proxyport + "...")
    serv.serve_forever()
