#!/usr/bin/python3
# -*- coding: utf-8 -*-

# import socket
import sys

XML = sys.argv[1]
METODO = sys.argv[2]
opcion = sys.argv[3]

if METODO == "REGISTER":
    mensaje = "REGISTER sip:leonard@bigbang.org:1234 SIP/2.0\r\n" + "Expires: " + opcion
    print(mensaje)
elif METODO == "INVITE":
    mensaje = "INVITE sip:penny@girlnextdoor.com SIP/2.0\r\n" + \
                "Content-Type: application/sdp\r\n\r\n" + \
                "v=0\r\n" + "o=leonard@bigbang.org 127.0.0.1\r\n" + \
                "s=misesion\r\n" + "t=0\r\n" + "m=audio 34543 RTP"
    print(mensaje)

# my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# my_socket.connect((IP, int(PUERTO)))
# my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')

# data = my_socket.recv(1024)
# respuesta = data.decode('utf-8')
