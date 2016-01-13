#!/usr/bin/python3
# -*- coding: utf-8 -*-
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import sys
from XMLHandler import XMLHandler
import hashlib
import time


class uaclient():

    def __init__(self, fichero):

        parser = make_parser()
        cHandler = XMLHandler()
        parser.setContentHandler(cHandler)
        try:
            parser.parse(open(fichero))
        except FileNotFoundError:
            print("---->Fichero no encontrado")

        self.diccionario = cHandler.get_tags()

if __name__ == "__main__":

    try:
        XML = sys.argv[1]
        METODO = sys.argv[2]
        opcion = sys.argv[3]
    except:
        print("Usage: python3 uaclient.py <config.xml> method option")
    uaobj = uaclient(XML)
    logpath = uaobj.diccionario["logpath"]
    log = open(logpath, 'w')
    hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    logmen = "Starting..."
    log.write(hora + " " + logmen + "\n")
    rtport = uaobj.diccionario["rtport"]
    usr = uaobj.diccionario["username"]
    servport = uaobj.diccionario["uasport"]

    if METODO == "REGISTER":
        mensaje = "REGISTER sip:" + usr + ":" + servport + " SIP/2.0\r\n" + \
                    "Expires: " + opcion
        print("->Enviando: \r\n" + mensaje)
    elif METODO == "INVITE":
        mensaje = "INVITE sip:" + opcion + " SIP/2.0\r\n" + \
                    "Content-Type: application/sdp\r\n\r\n" + \
                    "v=0\r\n" + "o=" + usr + " 127.0.0.1\r\n" + \
                    "s=misesion\r\n" + "t=0\r\n" + "m=audio " + rtport + " RTP"
        print("->Enviando: \r\n" + mensaje)
    elif METODO == "BYE":
        mensaje = "BYE sip:" + opcion + " SIP/2.0"
        print("->Enviando: \r\n" + mensaje)

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxyIP = uaobj.diccionario["proxyip"]
    proxyPort = uaobj.diccionario["proxyport"]
    my_socket.connect(("127.0.0.1", int(proxyPort)))

    my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
    hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    logmen = "Send to " + "127.0.0.1" + \
            ":" + uaobj.diccionario["proxyport"] + ": " + \
            mensaje.replace("\r\n", " ")
    log.write(hora + " " + logmen + "\n")
    i = 0
    while i < 1:
        data = my_socket.recv(1024)
        respuesta = data.decode('utf-8')
        if respuesta != "":
            serv_resp = respuesta.split(" ")
            if serv_resp[1] == "100":
                print("->Recibido 100 Trying")
                if serv_resp[3] == "180":
                    print("->Recibido 180 Ring")
                    if serv_resp[5] == "200":
                        print("->Recibido 200 OK + sdp")
                        hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                        logmen = "Received from " + "127.0.0.1" + \
                                ":" + proxyPort + ": " + \
                                respuesta.replace("\r\n", " ")
                        log.write(hora + " " + logmen + "\n")
                        # sdp(sacar puerto rtp)
                        ack = "ACK sip:" + opcion + " SIP/2.0\r\n"
                        my_socket.send(bytes(ack, 'utf-8') + b'\r\n')
                        hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                        logmen = "Send to " + "127.0.0.1" + \
                                ":" + uaobj.diccionario["proxyport"] + ": " + \
                                ack.replace("\r\n", " ")
                        log.write(hora + " " + logmen + "\n")

                        # audio = my_socket.recv(1024)

                        # os.system("chmod +x mp32rtp")
                        # exe = "./mp32rtp -i " + "127.0.0.1"
                        # exe = exe + " -p " + portaudio + " < " + audio_file
                        # os.system(exe)
                        i = 2
            elif serv_resp[1] == "200":
                print("->Recibido 200 OK")
                hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                logmen = "Received from " + "127.0.0.1" + \
                        ":" + proxyPort + ": " + \
                        respuesta.replace("\r\n", " ")
                log.write(hora + " " + logmen + "\n")
                i = 2
                # ok al reg o al bye
            elif serv_resp[1] == "400":
                print("->Recibido 400 Bad Request")
                hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                logmen = "Received from " + "127.0.0.1" + \
                        ":" + proxyPort + ": " + \
                        respuesta.replace("\r\n", " ")
                log.write(hora + " " + logmen + "\n")
                i = 2
            elif serv_resp[1] == "401":
                print("->Recibido 401 Unauthorized")
                hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                logmen = "Received from " + "127.0.0.1" + \
                        ":" + proxyPort + ": " + \
                        respuesta.replace("\r\n", " ")
                log.write(hora + " " + logmen + "\n")
                nonce = respuesta.split("nonce=")
                nonce = nonce[1]
                passwd = uaobj.diccionario["passwd"]
                print("    Creando response...")
                passwdb = (bytes(passwd, 'utf-8'))
                nonceb = (bytes(nonce, 'utf-8'))
                m = hashlib.md5()
                m.update(passwdb + nonceb)
                response = m.hexdigest()
                print("->Enviando REGISTER + response")
                reauten = mensaje + "\r\n" + \
                            "Authorization: response=" + response
                my_socket.send(bytes(reauten, 'utf-8') + b'\r\n')
                hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                logmen = "Send to " + "127.0.0.1" + \
                        ":" + uaobj.diccionario["proxyport"] + ": " + \
                        reauten.replace("\r\n", " ")
                log.write(hora + " " + logmen + "\n")
            elif serv_resp[1] == "404":
                print("->Recibido 404 User Not Found")
                hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                logmen = "Received from " + "127.0.0.1" + \
                        ":" + proxyPort + ": " + \
                        respuesta.replace("\r\n", " ")
                log.write(hora + " " + logmen + "\n")
                i = 2
            elif serv_resp[1] == "405":
                print("->Recibido 405 Method Not Allowed")
                hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                logmen = "Received from " + "127.0.0.1" + \
                        ":" + proxyPort + ": " + \
                        respuesta.replace("\r\n", " ")
                log.write(hora + " " + logmen + "\n")
                i = 2
            else:
                i = 2

    hora = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    logmen = "Finishing."
    log.write(hora + " " + logmen + "\n")

    my_socket.close()
    print("--CLOSE--")
