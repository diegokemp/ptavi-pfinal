#!/usr/bin/python3
# -*- coding: utf-8 -*-
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socketserver
import sys
from XMLHandler import XMLHandler
# import os

class uaserver():

    def __init__(self, fichero):

        parser = make_parser()
        cHandler = XMLHandler()
        parser.setContentHandler(cHandler)
        try:
            parser.parse(open(fichero))
        except FileNotFoundError:
            print("NO HAY FICHERO")

        self.diccionario = cHandler.get_tags()


class SIPHandler(socketserver.DatagramRequestHandler):


    def handle(self):
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            lineutf = line.decode('utf-8')
            if lineutf != "":
                method = lineutf.split(" sip:")
                metodos = ["INVITE","BYE","ACK"]
                if method[0] in metodos:
                    if method[0]=="INVITE":
                        print("invite--")
                        try:
                            portaudio = lineutf.split("m=audio ")
                            portaudio = portaudio[1].split(" ")
                            portaudio = portaudio[0]
                            print(portaudio)
                            #a quien enviar rtp
                        except:
                            self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
                            break
                        print("ok--conca")
                        self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                        self.wfile.write(b"SIP/2.0 180 Ring\r\n\r\n")
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                        print(self.diccionario["rtport"])
                        #usrname/uaserverip/rtport
                        #recibir rtp
                        #sdpok
                    elif method[0]=="ACK":
                        # os.system("chmod +x mp32rtp")
                        # exe = "./mp32rtp -i " + IP_Client
                        # exe = exe + " -p " + portaudio + " < " + audio_file
                        # os.system(exe)
                        print("enviando audio----------------")
                    elif method[0]=="BYE":
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                else:
                    self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")
            if not line:
                break

if __name__ == "__main__":
    try:
        XML = sys.argv[1]
        uaobj = uaserver(XML)
        print(uaobj.diccionario["rtport"])
        servIP = uaobj.diccionario["uasip"]
        servPort = uaobj.diccionario["uasport"]
        SIPHandler.diccionario = uaobj.diccionario
        serv = socketserver.UDPServer((servIP, int(servPort)), SIPHandler)
    except:
        print("Usage: python3 server.py IP port audio_file")
    print("Listening...")
    serv.serve_forever()
