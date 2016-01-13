#!/usr/bin/python3
# -*- coding: utf-8 -*-
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import sys
from XMLHandler import XMLHandler
import hashlib

class uaclient():

    def __init__(self, fichero):

        parser = make_parser()
        cHandler = XMLHandler()
        parser.setContentHandler(cHandler)
        try:
            parser.parse(open(fichero))
        except FileNotFoundError:
            print("NO HAY FICHERO")

        self.diccionario = cHandler.get_tags()

if __name__ == "__main__":

    XML = sys.argv[1]
    METODO = sys.argv[2]
    opcion = sys.argv[3]
    uaobj = uaclient(XML)
    rtport = uaobj.diccionario["rtport"]
    usr = uaobj.diccionario["username"]
    servport = uaobj.diccionario["uasport"]

    if METODO == "REGISTER":
        mensaje = "REGISTER sip:" + usr + ":" + servport + " SIP/2.0\r\n" + \
                    "Expires: " + opcion
        print(mensaje)
    elif METODO == "INVITE":
        mensaje = "INVITE sip:" + opcion + " SIP/2.0\r\n" + \
                    "Content-Type: application/sdp\r\n\r\n" + \
                    "v=0\r\n" + "o=" + usr + " 127.0.0.1\r\n" + \
                    "s=misesion\r\n" + "t=0\r\n" + "m=audio " + rtport + " RTP"
        print(mensaje)
    elif METODO == "BYE":
        mensaje = "BYE sip:" + opcion + " SIP/2.0"
        print(mensaje)

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxyIP = uaobj.diccionario["proxyip"]
    proxyPort = uaobj.diccionario["proxyport"]
    print(proxyIP + proxyPort)
    my_socket.connect(("127.0.0.1", int(proxyPort)))#puerto proxy

    my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
    i=0
    while i < 1:
        data = my_socket.recv(1024)
        respuesta = data.decode('utf-8')
        if respuesta != "":
            print(respuesta)
            serv_resp = respuesta.split(" ")
            print(serv_resp)
            if serv_resp[1] == "100":
                print("100--")
                if serv_resp[3] == "180":
                    print("180--")
                    if serv_resp[5] == "200":
                        print("200 concatenado")
                        i = 2
                        #sdp(sacar puerto rtp)
                        ack = "ACK sip:" + opcion + " SIP/2.0\r\n"
                        my_socket.send(bytes(ack, 'utf-8') + b'\r\n')
            elif serv_resp[1] == "200":
                print("------CLOSE------")
                i = 2
                #ok al reg o al bye
            elif serv_resp[1] == "400":
                i = 2
            elif serv_resp[1] == "401":
                nonce = respuesta.split("nonce=")
                nonce = nonce[1]
                passwd = uaobj.diccionario["passwd"]
                passwdb = (bytes(passwd, 'utf-8'))
                nonceb = (bytes(nonce, 'utf-8'))
                m = hashlib.md5()
                m.update(passwdb + nonceb)
                response = m.hexdigest()
                reauten = mensaje + "\r\n" + \
                            "Authorization: response=" + response
                my_socket.send(bytes(reauten, 'utf-8') + b'\r\n')
                print("reautentificando")
            elif serv_resp[1] == "404":
                i = 2
            elif serv_resp[1] == "405":
                i = 2
            else:
                i = 2
    my_socket.close()
    print("THE END")
