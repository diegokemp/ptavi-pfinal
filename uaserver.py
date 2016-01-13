#!/usr/bin/python3
# -*- coding: utf-8 -*-
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socketserver
import sys
from XMLHandler import XMLHandler
import time
# import os


class uaserver():

    def __init__(self, fichero):

        parser = make_parser()
        cHandler = XMLHandler()
        parser.setContentHandler(cHandler)
        try:
            parser.parse(open(fichero))
        except FileNotFoundError:
            print("---->Fichero no encontrado")

        self.diccionario = cHandler.get_tags()


class SIPHandler(socketserver.DatagramRequestHandler):

    def handle(self):

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            lineutf = line.decode('utf-8')
            if lineutf != "":
                method = lineutf.split(" sip:")
                metodos = ["INVITE", "BYE", "ACK"]
                if method[0] in metodos:
                    if method[0] == "INVITE":
                        print("->Recibido INVITE")
                        hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                        logmen = "Received from " + "127.0.0.1" + ":" + \
                                str(self.client_address[1]) + ": " + \
                                lineutf.replace("\r\n", " ")
                        log.write(hora + " " + logmen + "\n")
                        try:
                            portaudio = lineutf.split("m=audio ")
                            portaudio = portaudio[1].split(" ")
                            portaudio = portaudio[0]
                            puertortp["rtp_send"] = portaudio
                            print(puertortp)
                            # a quien enviar rtp
                        except:
                            self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
                            break

                        usr = self.diccionario["username"]
                        rtport = self.diccionario["rtport"]
                        print("->Enviando 100 180 200 + sdp")
                        mensaje = "SIP/2.0 100 Trying\r\n\r\n" + \
                                    "SIP/2.0 180 Ring\r\n\r\n" + \
                                    "SIP/2.0 200 OK\r\n" + \
                                    "Content-Type: application/sdp\r\n\r\n" + \
                                    "v=0\r\n" + "o=" + usr + \
                                    " 127.0.0.1\r\n" + \
                                    "s=misesion\r\n" + "t=0\r\n" + \
                                    "m=audio " + rtport + " RTP"
                        hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                        logmen = "Send to " + "127.0.0.1" + \
                                ":" + self.diccionario["proxyport"] + ": " + \
                                mensaje.replace("\r\n", " ")
                        log.write(hora + " " + logmen + "\n")
                        self.wfile.write(bytes(mensaje, 'utf-8'))
                        # print(self.diccionario["rtport"])
                        # sdpok
                    elif method[0] == "ACK":
                        print("->Recibido ACK")
                        hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                        logmen = "Received from " + "127.0.0.1" + \
                                ":" + str(self.client_address[1]) + ": " + \
                                lineutf.replace("\r\n", " ")
                        log.write(hora + " " + logmen + "\n")
                        print(puertortp["rtp_send"])
                        audio_file = self.diccionario["mp3path"]
                        # os.system("chmod +x mp32rtp")
                        # exe = "./mp32rtp -i " + "127.0.0.1"
                        # exe = exe + " -p " + portaudio + " < " + audio_file
                        # os.system(exe)
                        print("enviando audio----------------")
                    elif method[0] == "BYE":
                        print("->Recibido BYE")
                        hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                        logmen = "Received from " + "127.0.0.1" + \
                                ":" + str(self.client_address[1]) + ": " + \
                                lineutf.replace("\r\n", " ")
                        log.write(hora + " " + logmen + "\n")

                        mensaje = "SIP/2.0 200 OK\r\n\r\n"
                        hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                        logmen = "Send to " + "127.0.0.1" + \
                                ":" + self.diccionario["proxyport"] + ": " + \
                                mensaje.replace("\r\n", " ")
                        log.write(hora + " " + logmen + "\n")
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                        print("->Enviando 200 OK")
                else:
                    mensaje = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
                    hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                    logmen = "Send to " + "127.0.0.1" + \
                            ":" + self.diccionario["proxyport"] + ": " + \
                            mensaje.replace("\r\n", " ")
                    log.write(hora + " " + logmen + "\n")
                    self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")
            if not line:
                break

if __name__ == "__main__":

    XML = sys.argv[1]
    uaobj = uaserver(XML)
    servIP = uaobj.diccionario["uasip"]
    servPort = uaobj.diccionario["uasport"]
    logpath = uaobj.diccionario["logpath"]
    log = open(logpath, 'w')
    hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    logmen = "Starting..."
    log.write(hora + " " + logmen + "\n")
    puertortp = {}
    SIPHandler.diccionario = uaobj.diccionario
    serv = socketserver.UDPServer((servIP, int(servPort)), SIPHandler)

    print("Usage: python3 uaserver.py <config.xml>")
    print("Listening...")
    serv.serve_forever()
