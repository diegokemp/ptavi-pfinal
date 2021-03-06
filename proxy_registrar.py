#!/usr/bin/python3
# -*- coding: utf-8 -*-
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import socketserver
import sys
from uaserver import XMLHandler
import time
import json
import random
import hashlib
import os


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

    def rand(self):
        rand = str(random.randint(100000000000000, 999999999999999))
        return rand

    def hora_actual(self):
        hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        return hora

    def json2passwd(self, archivojson):
        archivo = open(archivojson, "r")
        self.diccpass = json.load(archivo)

    def json2registered(self, archivojson):
        if os.path.exists(archivojson):
            archivo2 = open(archivojson, "r")
        else:
            archivo2 = open(archivojson, "w")
            archivo2.write("{}")
            archivo2.close()
            archivo2 = open(archivojson, "r")
        self.dicc = json.load(archivo2)
        archivo2.close()

    def caduca(self, actual):
        dicc2 = self.dicc.copy()
        for key in dicc2.keys():
            if (dicc2[key][1]) < actual:
                del self.dicc[key]
                print("---->Usuario CADUCADO")

    def register2json(self, nombre):
        archivo = open(nombre, "w")
        datjson = json.dump(self.dicc, archivo)
        archivo.close()

    def passwd2json(self, nombre):
        archivo = open(nombre, "w")
        datjson2 = json.dump(self.diccpass, archivo)
        archivo.close()

    def handle(self):
        archivopass = self.diccionario["datapass"]
        archivojson = self.diccionario["datapath"]
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
                if method[0] == "REGISTER":
                    tracker = lineutf.split("Expires: ")
                    tracker = tracker[1].split("\r\n")
                    expires = tracker[0]
                    e = float(expires)
                    exp = time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.localtime(time.time() + e))
                    emi_usr = lineutf.split(":")
                    emi_port = emi_usr[2].split(" ")
                    emi_port = emi_port[0]
                    # portemireg
                    emi_usr = emi_usr[1]
                    # diremireg
                    hora = self.hora_actual()
                    logmen = "Received from " + "127.0.0.1" + \
                             ":" + str(self.client_address[1]) + ": " + \
                             lineutf.replace("\r\n", " ")
                    log.write(hora + " " + logmen + "\n")
                    if expires != "0":
                        # quiere registrarse
                        if tracker[1] != "":
                            # tiene response
                            response = tracker[1].split("response=")
                            response = response[1]

                            passwd = self.diccpass[emi_usr][1]
                            passwdb = (bytes(passwd, 'utf-8'))
                            nonce = self.diccpass[emi_usr][0]
                            # se lo asignamos a su @ en la primera ejec
                            nonceb = (bytes(nonce, 'utf-8'))

                            m = hashlib.md5()
                            m.update(passwdb + nonceb)
                            response2 = m.hexdigest()
                            # comparamos el response que recib y el que crea
                            if response == response2:
                                print("->Register autorizado")

                                portsereg = lineutf.split(" SIP/2.0")
                                portsereg = portsereg[0].split(":")
                                portsereg = portsereg[2]
                                # puerto servidor ua
                                self.dicc[emi_usr] = [portsereg, exp]
                                # puerto & expires
                                self.register2json(archivojson)
                                register_resp = ("SIP/2.0 200 OK\r\n\r\n")
                                print("    Enviando 200 OK")
                            else:
                                print("---->Response no valido")
                        else:
                            print("->Register no autorizado")
                            print("    Creando nonce para este ua...")
                            self.diccpass[emi_usr][0] = self.rand()
                            self.passwd2json(archivopass)
                            # guardamos el nonce por @ en pass
                            nonce = self.diccpass[emi_usr][0]
                            register_resp = "SIP/2.0 401 Unauthorized\r\n" + \
                                            "WWW Authenticate: Digest " + \
                                            "nonce=" + nonce
                            print("->Enviando 401 Unauthorized")
                        self.wfile.write(bytes(register_resp, 'utf-8'))
                        hora = self.hora_actual()
                        logmen = "Send to " + "127.0.0.1" + \
                                 ":" + str(self.client_address[1]) + ": " + \
                                 register_resp.replace("\r\n", " ")
                        log.write(hora + " " + logmen + "\n")
                    else:
                        del self.dicc[emi_usr]
                        mensaje = "SIP/2.0 200 OK\r\n"
                        self.wfile.write(bytes(mensaje, 'utf-8'))
                        hora = self.hora_actual()
                        logmen = "Send to " + "127.0.0.1" + \
                                 ":" + str(self.client_address[1]) + ": " + \
                                 mensaje.replace("\r\n", " ")
                        log.write(hora + " " + logmen + "\n")
                        self.register2json(archivojson)
                        print("->Usuario borrado(expires = 0)")

                elif method[0] == "INVITE":
                    print("->Recibido: INVITE")
                    hora = self.hora_actual()
                    logmen = "Received from " + "127.0.0.1" + \
                             ":" + str(self.client_address[1]) + ": " + \
                             lineutf.replace("\r\n", " ")
                    log.write(hora + " " + logmen + "\n")
                    isregistered = lineutf.split("o=")
                    isregistered = isregistered[1].split(" ")
                    isregistered = isregistered[0]
                    if isregistered in self.dicc.keys():
                        emi_port = self.dicc[isregistered][0]

                        rec_usr = lineutf.split(":")
                        rec_usr = rec_usr[1].split(" ")
                        rec_usr = rec_usr[0]
                        if rec_usr in self.dicc.keys():
                            print("receptor encontrado")
                            rec_port = self.dicc[rec_usr][0]
                            # puertobuscar por @
                            mensaje = lineutf
                            print("->Enviando INVITE")
                            my_socket.connect(("127.0.0.1", int(rec_port)))
                            my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
                            hora = self.hora_actual()
                            logmen = "Send to " + "127.0.0.1" + \
                                     ":" + rec_port + ": " + \
                                     mensaje.replace("\r\n", " ")
                            log.write(hora + " " + logmen + "\n")
                            print("    Esperando respuesta...")
                            resp = []
                            try:
                                data = my_socket.recv(1024)
                                respuesta = data.decode('utf-8')
                                resp = respuesta.split(" ")
                            except ConnectionRefusedError:
                                print("conection refuse")
                                conxrefuse = "SIP/2.0 404 User Not Found\r\n"
                                self.wfile.write(bytes(conxrefuse, 'utf-8'))
                                hora = self.hora_actual()
                                logmen = "Send to " + "127.0.0.1" + \
                                         ":" + emi_port + ": " + \
                                         conxrefuse.replace("\r\n", " ")
                                log.write(hora + " " + logmen + "\n")

                            if len(resp) > 1:
                                if resp[1] == "100" and resp[3] == "180":
                                    print("->Recibido: 100 Trying")
                                    print("->Recibido: 180 Ring")
                                    if resp[5] == "200":
                                        print("->Recibido: 200 OK")
                                        hora = self.hora_actual()
                                        logmen = "Received from " + \
                                                 "127.0.0.1" + \
                                                 ":" + rec_port + ": " + \
                                                 respuesta.replace("\r\n", " ")
                                        log.write(hora + " " + logmen + "\n")
                                        mens = respuesta
                                        print("->Enviando 100 180 200+sdp")
                                        self.wfile.write(bytes(mens, 'utf-8'))
                                        hora = self.hora_actual()
                                        logmen = "Send to " + "127.0.0.1" + \
                                                 ":" + emi_port + ": " + \
                                                 respuesta.replace("\r\n", " ")
                                        log.write(hora + " " + logmen + "\n")
                        else:
                            print("receptor no encontrado")
                            usr_nf = "SIP/2.0 404 User Not Found\r\n"
                            self.wfile.write(bytes(usr_nf, 'utf-8'))
                            hora = self.hora_actual()
                            logmen = "Send to " + "127.0.0.1" + \
                                     ":" + emi_port + ": " + \
                                     usr_nf.replace("\r\n", " ")
                            log.write(hora + " " + logmen + "\n")
                elif method[0] == "ACK":
                    print("Recibido: ACK")
                    rec_usr = lineutf.split(":")
                    rec_usr = rec_usr[1].split(" ")
                    rec_usr = rec_usr[0]
                    rec_port = self.dicc[rec_usr][0]
                    hora = self.hora_actual()
                    logmen = "Received from " + "127.0.0.1" + \
                             ":" + str(self.client_address[1]) + ": " + \
                             lineutf.replace("\r\n", " ")
                    log.write(hora + " " + logmen + "\n")
                    mensaje = lineutf
                    print("->Enviando ACK")
                    my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
                    hora = self.hora_actual()
                    logmen = "Send to " + "127.0.0.1" + \
                             ":" + rec_port + ": " + \
                             mensaje.replace("\r\n", " ")
                    log.write(hora + " " + logmen + "\n")
                elif method[0] == "BYE":
                    print("Recibido: BYE")
                    hora = self.hora_actual()
                    logmen = "Received from " + "127.0.0.1" + \
                             ":" + str(self.client_address[1]) + ": " + \
                             lineutf.replace("\r\n", " ")
                    log.write(hora + " " + logmen + "\n")
                    rec_usr = lineutf.split(":")
                    rec_usr = rec_usr[1].split(" ")
                    rec_usr = rec_usr[0]
                    rec_port = self.dicc[rec_usr][0]
                    mensaje = lineutf
                    print("->Enviando BYE")
                    my_socket.connect(("127.0.0.1", int(rec_port)))
                    my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
                    hora = self.hora_actual()
                    logmen = "Send to " + "127.0.0.1" + \
                             ":" + rec_port + ": " + \
                             mensaje.replace("\r\n", " ")
                    log.write(hora + " " + logmen + "\n")
                    print("    Esperando respuesta...")
                    data = my_socket.recv(1024)
                    respubye = data.decode('utf-8')
                    if respubye == "":
                        data = my_socket.recv(1024)
                        respubye = data.decode('utf-8')
                    respbye = respubye.split(" ")
                    if respbye[1] == "200":
                        print("->Recibido 200 OK")
                        hora = self.hora_actual()
                        logmen = "Received from " + "127.0.0.1" + \
                                 ":" + str(self.client_address[1]) + ": " + \
                                 respubye.replace("\r\n", " ")
                        log.write(hora + " " + logmen + "\n")
                        print("->Enviando 200 OK")
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                        hora = self.hora_actual()
                        logmen = "Send to " + "127.0.0.1" + \
                                 ":" + rec_port + ": " + \
                                 respubye.replace("\r\n", " ")
                        log.write(hora + " " + logmen + "\n")
                else:
                    print("---->> " + lineutf)
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
    logpath = proxyobj.diccionario["logpath"]
    log = open(logpath, 'w')
    hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    logmen = "Starting..."
    log.write(hora + " " + logmen + "\n")
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv = socketserver.UDPServer((proxyip, int(proxyport)), ProxySIPHandler)

    print("Server " + proxyname + " listening at port " + proxyport + "...")
    serv.serve_forever()
