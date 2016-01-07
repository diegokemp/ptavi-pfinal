#!/usr/bin/python3
# -*- coding: utf-8 -*-
import socketserver
import sys
import os


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
                        portaudio = lineutf.split("m=audio ")
                        portaudio = portaudio[1].split(" ")
                        portaudio = portaudio[0]
                        print(portaudio)
            if not line:
                break

if __name__ == "__main__":
    try:
        configXML = sys.argv[1]
        serv = socketserver.UDPServer(('', 3443), SIPHandler)
    except:
        print("Usage: python3 server.py IP port audio_file")
    print("Listening...")
    serv.serve_forever()
